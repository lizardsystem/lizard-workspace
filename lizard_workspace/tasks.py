# Celery tasks
import logging
import datetime
from celery.task import task
from copy import deepcopy
from django.template.defaultfilters import slugify
from django.utils import simplejson
from owslib.wms import WebMapService

from lizard_task.handler import get_handler
from lizard_workspace.models import Layer
from lizard_workspace.models import Tag
from lizard_fewsnorm.models import TimeSeriesCache
from lizard_fewsnorm.models import ParameterCache
from lizard_workspace.models import SyncTask
from lizard_layers.models import ServerMapping
from lizard_workspace.models import LayerWorkspaceItem
from lizard_workspace.models import LayerWorkspace


LOGGER_NAME = 'lizard_workspace_tasks'
logger = logging.getLogger(LOGGER_NAME)


@task
def sync_layers_ekr(
    slug='vss_area_value', username=None, taskname=None, loglevel=20):
    """
    Actually: sync_layers for ekr, esf and measures.
    """

    # Set up logging
    handler = get_handler(username=username, taskname=taskname)
    logger.addHandler(handler)
    logger.setLevel(loglevel)

    # Actual code to do the task
    source_ident = 'lizard-layers::%s' % slug
    layer = Layer.objects.get(slug=slug)
    original_tags = layer.tags.all()
    logger.info('template: %s' % layer)

    tag, _ = Tag.objects.get_or_create(slug=slug)
    logger.info('tag: %s' % tag)

    logger.debug('Invalidating existing layers...')
    existing_layers = dict(
        (l.slug, l) for l in
        Layer.objects.filter(source_ident=source_ident))
    for existing_layer in existing_layers.values():
        # Invalidate first and remove tags
        existing_layer.valid = False
        existing_layer.tags.clear()
        existing_layer.save()

    count_update, count_new = 0, 0

    group_tag_ekr = 'ekr-layers'
    group_tag_esf = 'esf-layers'
    group_tag_measure_status = 'measure-status-layers'
    name_cql_style = (
        ('EKR VIS', "name = 'EKR-VIS'", 'vss_ekr_value', group_tag_ekr),
        ('EKR FYTOPL', "name = 'EKR-FYTOPL'", 'vss_ekr_value', group_tag_ekr),
        ('EKR MAFAUNA', "name = 'EKR-MAFAUNA'", 'vss_ekr_value', group_tag_ekr),
        ('EKR OVWFLORA', "name = 'EKR-OVWFLORA'", 'vss_ekr_value', group_tag_ekr),
        ('EKR Minst gunstig', "name = 'EKR-ONGUNSTIG'", 'vss_ekr_value', group_tag_ekr),
        ('EKR Doelstelling', "name = 'EKR-DOELSCORE'", 'vss_ekr_score', group_tag_ekr),
        ('ESF 1', "name = 'ESF-1'", 'vss_esf', group_tag_esf),
        ('ESF 2', "name = 'ESF-2'", 'vss_esf', group_tag_esf),
        ('ESF 3', "name = 'ESF-3'", 'vss_esf', group_tag_esf),
        ('ESF 4', "name = 'ESF-4'", 'vss_esf', group_tag_esf),
        ('ESF 5', "name = 'ESF-5'", 'vss_esf', group_tag_esf),
        ('ESF 6', "name = 'ESF-6'", 'vss_esf', group_tag_esf),
        ('ESF 7', "name = 'ESF-7'", 'vss_esf', group_tag_esf),
        ('ESF 8', "name = 'ESF-8'", 'vss_esf', group_tag_esf),
        ('ESF 9', "name = 'ESF-9'", 'vss_esf', group_tag_esf),
        ('ESF STATUS', "name = 'ESF-STATUS'", 'vss_esf', group_tag_esf),
        ('Maatregel status', "name = 'MEASURE-STATUS'", 'vss_measure_status',
         group_tag_measure_status),
        ('Maatregel status planning', "name = 'MEASURE-STATUS-PLANNING'", 'vss_measure_status',
         group_tag_measure_status),
    )
    for name, cql, style, group_tag in name_cql_style:

        instance_slug = slugify(name)
        if instance_slug in existing_layers:
            # Update existing, the old existing tags have been
            # removed already.
            new_layer = existing_layers[instance_slug]
            logger.debug('Update: %s' % instance_slug)
            new_layer.data_set = layer.data_set
            count_update += 1
        else:
            # New
            logger.debug('New: %s' % instance_slug)
            new_layer = deepcopy(layer)
            new_layer.slug = instance_slug
            new_layer.id = None
            count_new += 1

        new_layer.filter = cql

        # Note that the same name can occur multiple times, but
        # with different mod, qua and/or stp.
        new_layer.name = name
        new_layer.source_ident = source_ident
        new_layer.valid = True
        new_layer.is_local_server = True
        new_layer.is_clickable = layer.is_local_server
        new_layer.js_popup_class = layer.js_popup_class
        new_layer.request_params = simplejson.dumps(dict(styles=style))
        new_layer.save()

        new_layer.tags.add(tag)
        for original_tag in original_tags:
            new_layer.tags.add(original_tag)
        group_tag, _ = Tag.objects.get_or_create(
            slug=group_tag,
        )
        new_layer.tags.add(group_tag)

    logger.info('new %d items' % count_new)
    logger.info('updated %d items' % count_update)

    # Remove logging handler
    logger.removeHandler(handler)

    return 'OK'


@task
def sync_layers_fewsnorm(
    slug='vss_fews_locations', username=None, taskname=None, loglevel=20):

    # Set up logging
    handler = get_handler(username=username, taskname=taskname)
    logger.addHandler(handler)
    logger.setLevel(loglevel)

    # Actual code to do the task
    source_ident = 'fewsnorm::%s' % slug

    layer = Layer.objects.get(slug=slug)
    original_tags = layer.tags.all()
    logger.info('template: %s' % layer)

    tag, _ = Tag.objects.get_or_create(slug='fewsnorm_%s' % slug)
    logger.info('tag: %s' % tag)

    logger.debug('Invalidating existing layers...')
    existing_layers = dict(
        (l.slug, l) for l in
        Layer.objects.filter(source_ident=source_ident))
    for existing_layer in existing_layers.values():
        # Invalidate first.
        existing_layer.valid = False
        # Remove tags from many to many relationships, not delete
        # the tags themselves.
        for layer_tag in existing_layer.tags.all():
            existing_layer.tags.remove(layer_tag)
        existing_layer.save()

    count_update, count_new = 0, 0

    for par_mod_qua_stp in TimeSeriesCache.objects.filter(active=True).values(
        "parametercache__ident", "parametercache__name", "modulecache__ident",
        "qualifiersetcache__ident", "timestepcache__ident").distinct():
        par = par_mod_qua_stp['parametercache__ident']
        par_name = par_mod_qua_stp['parametercache__name']
        mod = par_mod_qua_stp['modulecache__ident']
        qua = par_mod_qua_stp['qualifiersetcache__ident']
        stp = par_mod_qua_stp['timestepcache__ident']

        instance_slug = '%s_%s_%s_%s_%s' % (slug, par, mod, qua, stp)
        if instance_slug in existing_layers:
            # Update existing, the old existing tags have been
            # removed already.
            new_layer = existing_layers[instance_slug]
            logger.debug('Update: %s' % instance_slug)
            new_layer.data_set = layer.data_set
            count_update += 1
        else:
            # New
            logger.debug('New: %s' % instance_slug)
            new_layer = deepcopy(layer)
            new_layer.slug = instance_slug
            new_layer.id = None
            count_new += 1

        layer_params = []
        if par:
            layer_params.append("par_ident='%s'" % par)
        if mod:
            layer_params.append("mod_ident='%s'" % mod)
        if qua:
            layer_params.append("qua_ident='%s'" % qua)
        if stp:
            layer_params.append("stp_ident='%s'" % stp)
        new_layer.filter = ' and '.join(layer_params)

        # Note that the same name can occur multiple times, but
        # with different mod, qua and/or stp.
        if qua is None:
            new_layer.name = '%s (%s)' % (par_name, stp)
        else:
            new_layer.name = '%s %s (%s)' % (par_name, qua, stp)
        new_layer.name = new_layer.name[:80]
        new_layer.source_ident = source_ident
        new_layer.valid = True
        new_layer.is_local_server = layer.is_local_server
        new_layer.is_clickable = layer.is_local_server
        new_layer.js_popup_class = layer.js_popup_class
        new_layer.save()

        new_layer.tags.add(tag)
        for original_tag in original_tags:
            new_layer.tags.add(original_tag)
        if mod is not None:
            # add tag
            mod_tag, _ = Tag.objects.get_or_create(slug='%s_%s' % (tag, mod))
            new_layer.tags.add(mod_tag)

    logger.info('new %d items' % count_new)
    logger.info('updated %d items' % count_update)

    # Remove logging handler
    logger.removeHandler(handler)

    return 'OK'


@task
def sync_layers_measure(
    slug='vss_measure', username=None, taskname=None, loglevel=20):

    # Set up logging
    handler = get_handler(username=username, taskname=taskname)
    logger.addHandler(handler)
    logger.setLevel(loglevel)

    # Actual code to do the task
    logger.info('start sync')
    source_ident = 'lizard-layers::%s' % slug

    layer = Layer.objects.get(slug=slug)
    original_tags = layer.tags.all()
    logger.info('template: %s' % layer)

    tag, _ = Tag.objects.get_or_create(slug=slug)
    logger.info('tag: %s' % tag)

    logger.debug('Invalidating existing layers...')
    existing_layers = dict(
        (l.slug, l) for l in
        Layer.objects.filter(source_ident=source_ident))
    for existing_layer in existing_layers.values():
        # Invalidate first and remove tags
        existing_layer.valid = False
        existing_layer.tags.clear()
        existing_layer.save()

    count_update, count_new = 0, 0

    esf_name_template = "Maatregelen ESF%s"
    esf_cql_template = ("esf = %s AND ("
                        "is_target_esf = TRUE OR "
                        "positive = TRUE OR "
                        "negative = TRUE)")
    datalist = [
        # For measure layers based on type
        {
            'group_tag': 'maatregel-type',
            'cql_and_names': (
                ("type like 'BE%'", 'Beheermaatregelen'),
                ("type like 'BR%'", 'Bronmaatregelen'),
                ("type like 'IM%'", 'Immissiemaatregelen'),
                ("type like 'IN%'", 'Inrichtingsmaatregelen'),
                (
                    "type LIKE 'G%' OR type LIKE 'S%' OR type LIKE 'RO%'",
                    'Overige maatregelen',
                ),
            )
        },
        # For measure layers based on related esf
        {
            'group_tag': 'maatregel-esf',
            'cql_and_names': [(esf_cql_template % e, esf_name_template % e)
                              for e in range(1, 10)]
        },
    ]

    for datadict in datalist:
        for cql, name in datadict['cql_and_names']:

            instance_slug = slugify(name)
            if instance_slug in existing_layers:
                # Update existing, the old existing tags have been
                # removed already.
                new_layer = existing_layers[instance_slug]
                logger.debug('Update: %s' % instance_slug)
                new_layer.data_set = layer.data_set
                count_update += 1
            else:
                # New
                logger.debug('New: %s' % instance_slug)
                new_layer = deepcopy(layer)
                new_layer.slug = instance_slug
                new_layer.id = None
                count_new += 1

            new_layer.filter = cql

            # Note that the same name can occur multiple times, but
            # with different mod, qua and/or stp.
            new_layer.name = name
            new_layer.source_ident = source_ident
            new_layer.valid = True
            new_layer.is_local_server = True
            new_layer.is_clickable = layer.is_local_server
            new_layer.js_popup_class = layer.js_popup_class
            new_layer.save()

            new_layer.tags.add(tag)
            for original_tag in original_tags:
                new_layer.tags.add(original_tag)
            group_tag, _ = Tag.objects.get_or_create(
                slug=datadict['group_tag'],
            )
            new_layer.tags.add(group_tag)

    logger.info('new %d items' % count_new)
    logger.info('updated %d items' % count_update)

    # Remove logging handler
    logger.removeHandler(handler)

    return 'OK'


@task
def sync_layers_track(
    slug='vss_track_records', username=None, taskname=None, loglevel=20):
    """
    Sync layers for track records.
    """

    # Set up logging
    handler = get_handler(username=username, taskname=taskname)
    logger.addHandler(handler)
    logger.setLevel(loglevel)

    # Actual code to do the task
    source_ident = 'lizard-layers::%s' % slug
    layer = Layer.objects.get(slug=slug)
    original_tags = layer.tags.all()
    logger.info('template: %s' % layer)

    tag, _ = Tag.objects.get_or_create(slug=slug)
    logger.info('tag: %s' % tag)

    logger.debug('Invalidating existing layers...')
    existing_layers = dict(
        (l.slug, l) for l in
        Layer.objects.filter(source_ident=source_ident))
    for existing_layer in existing_layers.values():
        # Invalidate first and remove tags
        existing_layer.valid = False
        existing_layer.tags.clear()
        existing_layer.save()

    count_update, count_new = 0, 0

    group_tag = 'track_records'
    parameter_id_Ptot = ParameterCache.objects.get(ident='Ptot.bodem').id
    parameter_id_PO4 = ParameterCache.objects.get(ident='PO4.bodem').id
    parameter_id_aqmad_Ptot = ParameterCache.objects.get(
        ident='Ptot.z-score.water',
    ).id
    name_cql_style = (
        (
            'PO4 in bodemvocht',
            "parameter_id = %s" % parameter_id_PO4,
            'vss_track_record_PO4',
        ),
        (
            'P-totaal in bodem',
            "parameter_id = %s" % parameter_id_Ptot,
            'vss_track_record_Ptot',
        ),
        (
            'AqMaD water Ptot',
            "parameter_id = %s" % parameter_id_aqmad_Ptot,
            'vss_aqmad_Ptot',
        ),

    )
    for name, cql, style in name_cql_style:

        instance_slug = slugify(name)
        if instance_slug in existing_layers:
            # Update existing, the old existing tags have been
            # removed already.
            new_layer = existing_layers[instance_slug]
            logger.debug('Update: %s' % instance_slug)
            new_layer.data_set = layer.data_set
            count_update += 1
        else:
            # New
            logger.debug('New: %s' % instance_slug)
            new_layer = deepcopy(layer)
            new_layer.slug = instance_slug
            new_layer.id = None
            count_new += 1

        new_layer.filter = cql

        # Note that the same name can occur multiple times, but
        # with different mod, qua and/or stp.
        new_layer.name = name
        new_layer.source_ident = source_ident
        new_layer.valid = True
        new_layer.is_local_server = True
        new_layer.is_clickable = layer.is_local_server
        new_layer.js_popup_class = layer.js_popup_class
        new_layer.request_params = simplejson.dumps(dict(styles=style))
        new_layer.save()

        new_layer.tags.add(tag)
        for original_tag in original_tags:
            new_layer.tags.add(original_tag)
        group_tag, _ = Tag.objects.get_or_create(
            slug=group_tag,
        )
        new_layer.tags.add(group_tag)

    logger.info('new %d items' % count_new)
    logger.info('updated %d items' % count_update)

    # Remove logging handler
    logger.removeHandler(handler)

    return 'OK'

def perform_sync_task(task):
    """
    Run sync_task

    TODO: move to SyncTask object
    """
    logger.info('start with sync of server %s' % task.server.name)

    data_set = task.data_set
    if task.server.is_local_server:
        path_and_parameters = task.server.url.split('?')
        path = path_and_parameters[0]
        regex = r'^' + path + r'/?$'
        external_server = ServerMapping.objects.get(
            relative_path__regex=regex,
        ).external_server
        if len(path_and_parameters) > 1:
            parameters = path_and_parameters[1]
            service_url = external_server + '?' + parameters
        else:
            service_url = external_server
    else:
        service_url = task.server.url
    password = task.server.password
    username = task.server.username

    wms = WebMapService(
        service_url,
        version='1.1.1',
        password=password,
        username=username,
    )

    if task.tag:
        tag, new = task.tag, False
    else:
        tag, new = Tag.objects.get_or_create(
            slug='server_%s' % task.server.name)

    # layers = Layer.objects.filter(server=task.server)
    layers = Layer.objects.filter(source_ident=task.source_ident)

    layer_dict = dict(layers.values_list('layers', 'id'))

    #update server info
    task.server.title = wms.identification.title
    task.server.abstract = wms.identification.abstract
    task.server.save()

    new = 0
    new_names = []
    removed = 0
    removed_names = []
    updated = 0

    for wmslayer in wms.contents:
        if wmslayer in layer_dict:
            layer = layers.get(pk=layer_dict[wmslayer])
            del layer_dict[wmslayer]

            updated += 1
        else:
            layer = Layer()
            layer.server = task.server
            layer.layers = wmslayer
            layer.name = wms[wmslayer].title

            layer.slug = slugify(layer.name)
            layer.save()
            layer.tags.add(tag)

            new += 1
            new_names.append(layer.name)

        layer.data_set = data_set
        layer.is_local_server = task.server.is_local_server
        layer.is_clickable = task.server.is_clickable
        if not layer.js_popup_class and task.server.js_popup_class:
            layer.js_popup_class = task.server.js_popup_class
        layer.valid = True
        if data_set:
            layer.owner_type = Layer.OWNER_TYPE_DATASET
        else:
            layer.owner_type = Layer.OWNER_TYPE_PUBLIC

        layer.source_ident = task.source_ident
        layer.save()

        #nog iets met styles?

    for name, id in layer_dict.items():
        layer = layers.get(pk=id)
        layer.valid = False
        layer.save()

        removed += 1
        removed_names.append(layer.name)

    logger.info('%i new layers: %s.' % (new, str(', '.join(new_names))))
    logger.info('%i updated layers.' % (updated))
    logger.info('%i removed layers: %s.' % (
            removed, str(', '.join(removed_names))))

    task.last_sync = datetime.datetime.now()
    task.last_result = '%i new, %i updated, %i removed' % (
        new, updated, removed)

    task.save()


@task
def sync_layers_with_wmsserver(
    synctask=None, all=False, username=None, taskname=None, loglevel=20):

    # Set up logging
    handler = get_handler(username=username, taskname=taskname)
    logger.addHandler(handler)
    logger.setLevel(loglevel)

    # Actual code to do the task
    if all:
        tasks = SyncTask.objects.all()
        logger.info('All sync tasks')
    else:
        tasks = [SyncTask.objects.get(synctask), ]
        logger.info('Task: %s' % synctask)

    for task in tasks:
        try:
            perform_sync_task(task=task)
        except Exception as e:
            logger.error('Something went wrong performing task %s' % task)
            print e
            continue

    # Remove logging handler
    logger.removeHandler(handler)

    return 'OK'


@task
def workspace_update_baselayers(username=None, taskname=None, loglevel=20):
    """
    Reconfigure layers that have is_base_layer=True
    """
    # Set up logging
    handler = get_handler(username=username, taskname=taskname)
    logger.addHandler(handler)
    logger.setLevel(loglevel)

    # Actual code to do the task
    TOP10NL_LAYER_SLUG = 'top10nl'
    TOP10NL_TAG_SLUG = 'server_pdok-top10'
    SEMI_TRANSPARENT_SLUG_POSTFIX = '-semi-transparent'
    SEMI_TRANSPARENT_NAME_POSTFIX = ' (semitransparant)'

    # Get open streetmap, rename if necessary
    try:
        osm = Layer.objects.get(name='openstreetmap')
        osm.name = 'OpenStreetMap'
        osm.save()
    except:
        osm = Layer.objects.get(name='OpenStreetMap')

    # Remove anything except osm
    Layer.objects.filter(
        is_base_layer=True,
    ).exclude(
        pk=osm.pk,
    ).update(is_base_layer=False)

    # Remove old baselayer(s) for the top10nl if it exists
    Layer.objects.filter(slug=TOP10NL_LAYER_SLUG).delete()

    # Add a baselayer for the top10nl
    tag = Tag.objects.get(slug=TOP10NL_TAG_SLUG)
    top10_layers = tag.layer_set.all()
    new_layer = top10_layers[0]
    new_layer.name = 'Top10NL'
    new_layer.slug = TOP10NL_LAYER_SLUG
    new_layer.is_base_layer = True
    new_layer.source_ident = 'workspace-update-command',
    new_layer.layers = ','.join(l.layers for l in top10_layers)
    new_layer.source_ident = None
    new_layer.pk = None  # We want a new layer.
    new_layer.save()

    logger.info('Created default baselayers.')

    # Add or replace baselayers with 50% opacity
    base_layers = Layer.objects.filter(is_base_layer=True)
    Layer.objects.filter(
        slug__in=[b.slug + SEMI_TRANSPARENT_SLUG_POSTFIX
                  for b in base_layers],
    ).delete()

    for b in base_layers:
        options = simplejson.loads(b.options)
        options.update(opacity=0.5)
        b.pk = None  # Clone the layer
        b.source_ident = 'workspace-update-command'
        b.slug += SEMI_TRANSPARENT_SLUG_POSTFIX
        b.name += SEMI_TRANSPARENT_NAME_POSTFIX
        b.options = simplejson.dumps(options)
        b.save()

    logger.info('Added transparent variants of default baselayers.')

    # Remove logging handler
    logger.removeHandler(handler)

    return 'OK'


@task
def workspace_update_watersystem(username=None, taskname=None, loglevel=20):
    """
    Reconfigure layers for the watersystem map.
    """
    def _create_or_replace_merged_layer(name, slug, tag, layers):
        """
        Return created layer object.

        Laye is created with name and slug, and layers assembled from layers
        field of contributing layers. Contributing layers are looked up by
        the same layers field.
        """
        Layer.objects.filter(slug=slug).delete()

        contributing_layers = Layer.objects.filter(
            layers__in=layers,
        )
        layer = Layer.objects.create(
            slug=slug,
            name=name,
            source_ident='workspace-update-command',
            server=contributing_layers[0].server,
            layers=','.join(l.layers for l in contributing_layers),
        )
        layer.tags.add(tag)
        return layer

    # Set up logging
    handler = get_handler(username=username, taskname=taskname)
    logger.addHandler(handler)
    logger.setLevel(loglevel)

    # Actual code to do the task
    WORKSPACE_SLUG = 'watersysteemkaart'
    TAG_SLUG = 'basis'

    # Clear the layer workspace, get the tag
    layer_workspace = LayerWorkspace.objects.get(
        slug=WORKSPACE_SLUG,
    )
    LayerWorkspaceItem.objects.filter(
        layer_workspace=layer_workspace,
    ).delete()
    tag = Tag.objects.get_or_create(slug=TAG_SLUG)[0]

    # Create layers and add to workspace
    # Kunstwerken basis
    layer = _create_or_replace_merged_layer(
        slug='kunstwerken-basis',
        name='Kunstwerken Basis',
        tag=tag,
        layers=['wsh:gemaal', 'wsh:stuw', 'wsh:sluis'],
    )
    LayerWorkspaceItem.objects.create(
        layer_workspace=layer_workspace,
        layer=layer,
        visible=True,
        index=10,
    )

    # Kunstwerken extra
    layer = _create_or_replace_merged_layer(
        slug='kunstwerken-extra',
        name='Kunstwerken Extra',
        tag=tag,
        layers=[
            'wsh:vispassage', 'wsh:vaste_dam', 'wsh:sifon',
            'wsh:duiker', 'wsh:coupure', 'wsh:brug', 'wsh:aquaduct',
        ],
    )
    LayerWorkspaceItem.objects.create(
        layer_workspace=layer_workspace,
        layer=layer,
        visible=False,
        index=20,
    )

    # Peilgebied
    layer = _create_or_replace_merged_layer(
        slug='peilgebied-basis',
        name='Peilgebied',
        tag=tag,
        layers=['wsh:peilgebied'],
    )
    LayerWorkspaceItem.objects.create(
        layer_workspace=layer_workspace,
        layer=layer,
        visible=False,
        index=30,
    )

    # Waterloop
    layer = _create_or_replace_merged_layer(
        slug='waterloop-basis',
        name='Waterloop',
        tag=tag,
        layers=['wsh:waterloop'],
    )
    LayerWorkspaceItem.objects.create(
        layer_workspace=layer_workspace,
        layer=layer,
        visible=False,
        index=40,
    )

    # Oppervlake waterdeel
    layer = _create_or_replace_merged_layer(
        slug='oppervlakte-waterdeel-basis',
        name='Oppervlakte waterdeel',
        tag=tag,
        layers=['wsh:oppervlakte_waterdeel'],
    )
    LayerWorkspaceItem.objects.create(
        layer_workspace=layer_workspace,
        layer=layer,
        visible=False,
        index=50,
    )

    # Waterlichaam
    layer = _create_or_replace_merged_layer(
        slug='krw_waterlichaam',
        name='KRW-waterlichaam',
        tag=tag,
        layers=[
            'vss:vss_krw_waterbody_polygon',
            'vss:vss_krw_waterbody_linestring',
        ],
    )
    LayerWorkspaceItem.objects.create(
        layer_workspace=layer_workspace,
        layer=layer,
        visible=False,
        index=60,
    )

    layer = Layer.objects.get(slug='vss_measure')
    layer.name = 'Maatregelen'
    layer.js_popup_class = 'MeasurePopup'
    layer.save()
    LayerWorkspaceItem.objects.create(
        layer_workspace=layer_workspace,
        layer=layer,
        visible=False,
        index=70,
    )

    layer = Layer.objects.get(slug='vss_annotation')
    layer.name = 'Analyse interpretaties'
    layer.js_popup_class = 'AnnotationPopup'
    layer.save()
    LayerWorkspaceItem.objects.create(
        layer_workspace=layer_workspace,
        layer=layer,
        visible=False,
        index=80,
    )

    layer = Layer.objects.get(slug='witte-waas-gebieden')
    layer.name = 'Masker'
    layer.save()
    LayerWorkspaceItem.objects.create(
        layer_workspace=layer_workspace,
        layer=layer,
        visible=True,
        index=90,
    )

    logger.info('Reinstalled watersystem workspace.')

    # Remove logging handler
    logger.removeHandler(handler)

    return 'OK'


@task
def workspace_update_trackrecords(username=None, taskname=None, loglevel=20):
    """
    Create or replace trackrecordslayers in correct workspace
    """
    # Set up logging
    handler = get_handler(username=username, taskname=taskname)
    logger.addHandler(handler)
    logger.setLevel(loglevel)

    # Actual code to do the task
    layerworkspace = LayerWorkspace.objects.get(slug='p_map')
    layerworkspace.layers.clear()
    LayerWorkspaceItem.objects.create(
        layer_workspace=layerworkspace,
        layer=Layer.objects.get(slug='p-totaal-in-bodem'),
    )
    LayerWorkspaceItem.objects.create(
        layer_workspace=layerworkspace,
        layer=Layer.objects.get(slug='witte-waas-gebieden'),
    )

    logger.info('Replaced P-layer')

    layerworkspace = LayerWorkspace.objects.get(slug='po4_map')
    layerworkspace.layers.clear()
    LayerWorkspaceItem.objects.create(
        layer_workspace=layerworkspace,
        layer=Layer.objects.get(slug='po4-in-bodemvocht'),
    )
    LayerWorkspaceItem.objects.create(
        layer_workspace=layerworkspace,
        layer=Layer.objects.get(slug='witte-waas-gebieden'),
    )
    logger.info('Replaced PO4-layer')

    layerworkspace = LayerWorkspace.objects.get(slug='aqmad_map')
    layerworkspace.layers.clear()
    LayerWorkspaceItem.objects.create(
        layer_workspace=layerworkspace,
        layer=Layer.objects.get(slug='aqmad-water-ptot'),
    )
    LayerWorkspaceItem.objects.create(
        layer_workspace=layerworkspace,
        layer=Layer.objects.get(slug='witte-waas-gebieden'),
    )
    logger.info('Replaced adqmad PO4-layer')

    # Remove logging handler
    logger.removeHandler(handler)

    return 'OK'


def _create_single_layer_workspace(
        layerworkspace_template_slug,
        layerworkspace_slug,
        layerworkspace_name,
        layer_template_slug,
        layer_style,
        layer_slug,
        layer_name,
    ):
    """
    Create or replace new layer and layerworkspace based on template objects.
    """
    logger.info('Deleting any layer with slug %s', layer_slug)
    Layer.objects.filter(slug=layer_slug).delete()

    logger.info(
        'Creating new layer %s with style %s based on layer with slug %s',
        layer_name,
        layer_style,
        layer_slug,
    )
    layer = Layer.objects.get(slug=layer_template_slug)
    layer.pk = None
    layer.request_params = simplejson.dumps(dict(styles=layer_style))
    layer.name = layer_name
    layer.slug = layer_slug
    layer.save()


    logger.info(
        'Deleting any layerworkspace with slug %s',
        layerworkspace_slug,
    )
    LayerWorkspace.objects.filter(
        slug=layerworkspace_slug,
    ).delete()

    logger.info(
        'Creating new layerworkspace %s based on layerworkspace with slug %s',
        layerworkspace_name,
        layerworkspace_slug,
    )
    layerworkspace = LayerWorkspace.objects.get(slug=layerworkspace_template_slug)
    layerworkspace.pk = None
    layerworkspace.id = None
    layerworkspace.save()
    layerworkspace.slug = layerworkspace_slug
    layerworkspace.name = layerworkspace_name
    layerworkspace.save()

    logger.info(
        'Adding new layer %s to new layerworkspace %s',
        layer,
        layerworkspace,
    )
        
    LayerWorkspaceItem.objects.create(
        layer_workspace=layerworkspace,
        layer=layer,
    )


@task
def workspace_update_minimap(username=None, taskname=None, loglevel=20):
    """
    Add an area layer with a special style.
    """
    # Set up logging
    handler = get_handler(username=username, taskname=taskname)
    logger.addHandler(handler)
    logger.setLevel(loglevel)

    # Actual code to do the task
    MINIMAP_LAYER_SLUG_KRW = 'minimap-krw'
    MINIMAP_LAYERWORKSPACE_SLUG_KRW = 'minimap-krw'
    MINIMAP_LAYER_SLUG_AREA = 'minimap-area'
    MINIMAP_LAYERWORKSPACE_SLUG_AREA = 'minimap-area'

    # For krw minimap
    _create_single_layer_workspace(
        layerworkspace_template_slug='watersysteemkaart',
        layerworkspace_slug=MINIMAP_LAYERWORKSPACE_SLUG_KRW,
        layerworkspace_name='MiniMap KRW',
        layer_template_slug='krw_waterlichaam',
        layer_style='vss_red_on_gray_line,vss_red_on_gray',
        layer_slug=MINIMAP_LAYER_SLUG_KRW,
        layer_name='MiniMap KRW',
    )

    # For area minimap
    _create_single_layer_workspace(
        layerworkspace_template_slug='watersysteemkaart',
        layerworkspace_slug=MINIMAP_LAYERWORKSPACE_SLUG_AREA,
        layerworkspace_name='MiniMap gebieden',
        layer_template_slug='witte-waas-gebieden',
        layer_style='vss_red_on_gray',
        layer_slug=MINIMAP_LAYER_SLUG_AREA,
        layer_name='MiniMap gebieden',
    )

    # Remove logging handler
    logger.removeHandler(handler)

    return 'OK'
