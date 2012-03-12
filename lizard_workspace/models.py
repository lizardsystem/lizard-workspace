# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import json

from django.db import models
from django.contrib.auth.models import User
#from django.core.urlresolvers import reverse

from lizard_security.manager import FilteredManager
from lizard_security.models import DataSet

from lizard_map.models import WorkspaceStorage
from lizard_map.models import ADAPTER_CLASS_WMS
from treebeard.al_tree import AL_Node


class Category(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField()

    def __unicode__(self):
        return '%s' % self.name


class ThematicMap(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField()
    description = models.TextField(default="", blank=True)

    models.ForeignKey('LayerWorkspace', null=True, blank=True)

    def __unicode__(self):
        return '%s' % self.name


class Tag(models.Model):
    """
    Tag objects with this model using a many to many relationship.
    """
    slug = models.SlugField()

    def __unicode__(self):
        return '%s' % self.slug

    def layer_count(self):
        """
        Return number of layers associated with this tag.
        """
        return self.layer_set.all().count()


class WmsServer(models.Model):
    """
        location of WMS server
    """
    name = models.CharField(max_length=128)
    slug = models.SlugField()
    url = models.CharField(
        max_length=512, blank=True, null=True,
        help_text='Url of wms or tile request format for OSM')
    title = models.CharField(
        max_length=256, blank=True, default='',
        help_text='title provided by WMS server self (part of sync script)')
    abstract = models.TextField(blank=True, default='')

    def __unicode__(self):
        return self.name


class SyncTask(models.Model):
    """
        task settings for sync with capabilities of WMS server
    """
    name = models.CharField(max_length=128)
    slug = models.SlugField()
    server = models.ForeignKey(WmsServer)
    data_set = models.ForeignKey(
        DataSet, null=True, blank=True,
        help_text='The data set to be associated with the Layers.')
    tag = models.ForeignKey(
        Tag, null=True, blank=True,
        help_text='The tag to be associated with the Layers. Defaults to auto generated tag.')

    last_sync = models.DateTimeField(blank=True, null=True)
    last_result = models.TextField(blank=True, default='')

    objects = FilteredManager()

    def __unicode__(self):
        return '%s' % (self.name)

    @property
    def source_ident(self):
        """ Used to fill in in Layer model.
        """
        return 'sync_task::%s' % self.slug


class Layer(models.Model):
    """
    Define which layers can be chosen in your Layer Workspace

    Inspired by lizard-wms
    """
    OLLAYER_TYPE_WMS = 'OpenLayers.Layer.WMS'
    OLLAYER_TYPE_OSM = 'OpenLayers.Layer.OSM'

    OLLAYER_TYPE_CHOICES = (
        (OLLAYER_TYPE_WMS, ("WMS")),
        (OLLAYER_TYPE_OSM, ("Openstreetmap")),
    )

    OWNER_TYPE_USER = 0
    OWNER_TYPE_DATASET = 1
    OWNER_TYPE_PUBLIC = 2

    OWNER_TYPE_CHOICES = (
        (OWNER_TYPE_USER, ("User")),
        (OWNER_TYPE_DATASET, ("Dataset")),
        (OWNER_TYPE_PUBLIC, ("Public")),
    )

    #popup
    #has_legend
    #default opacity

    valid = models.BooleanField(default=True)

    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=200)

    use_location_filter = models.BooleanField(
        default=False,
        help_text=("Must a workspace add a filter based on the "
                   "current selected location context"))
    location_filter = models.CharField(
        max_length=128, blank=True, null=True,
        help_text=("Key - value json string. key= parameter, value = template for value. input is an object object (id,name,type) "
                   "if empty the id is used. example: {\"key\":\"cql_filter\", \"tpl\":\"gafident like \'{id}\'\"}Parameter filter string with \'{object_id}\' "
                   ))

    ollayer_class = models.CharField(
        max_length=80, choices=OLLAYER_TYPE_CHOICES, default=OLLAYER_TYPE_WMS)

    #request_params for wms
    server = models.ForeignKey(WmsServer, blank=True, null=True)
    is_local_server = models.BooleanField(default=False)
    layers = models.CharField(max_length=512, blank=True, null=True,
                                help_text='Layers for WMS')
    filter = models.CharField(
        max_length=512, blank=True, null=True,
        help_text='a cql_filter parameter that will be added to the OpenLayers layer params')

    #request_params additional to parameters above.
    #defaults for WMS request params are:
    # format: "image/png"
    # transparent: "true"
    # ....
    request_params = models.TextField(null=True, blank=True, default='{}')

    #layer settings in openlayers (options)
    is_base_layer = models.BooleanField(default=False)
    is_clickable = models.BooleanField(
        default=True, help_text='Is the layer clickable at all?')
    single_tile = models.BooleanField(default=False)

    #default settings for a layer in openlayers:
    #- displayInLayerSwitcher: false (baselayers = true)
    #- displayOutsideMaxExtent: true
    options = models.TextField(null=True, blank=True, default='{}')

    category = models.ForeignKey(Category, null=True, blank=True)
    data_set = models.ForeignKey(DataSet, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)
    owner_type = models.IntegerField(
        choices=OWNER_TYPE_CHOICES, default=OWNER_TYPE_USER)
    # group_code = models.CharField(max_length=128, blank=True, null=True)
    tags = models.ManyToManyField(Tag, null=True, blank=True)

    # sync_task = models.ForeignKey(
    #     SyncTask, null=True, blank=True,
    #     help_text='From what sync task did I come from?')
    source_ident = models.CharField(
        max_length=80, null=True, blank=True,
        help_text='Where do I come from?')

    objects = FilteredManager()

    def __unicode__(self):
        return '%s' % self.name

    def adapter_layer_json(self):
        """Call this function to add an item to your workspace
        """
        return json.dumps({
                'name': self.name,
                'url': self.url,
                'params': self.request_params,
                'options': self.options})

    def adapter_class(self):
        """Call this fun
            'id': self.id,
            'name': self.name,
            'use_location_filter': self.use_location_filter,
            'location_filter': self.location_filter,
ction to add an item to your workspace
        """
        return ADAPTER_CLASS_WMS

    def tags_str(self):
        tag_names = [str(tag) for tag in self.tags.all()]
        if tag_names:
            return ', '.join(tag_names)
        else:
            return 'no tags'

    def get_object_dict(self):


        output = {
            'plid': self.id,

            'use_location_filter': self.use_location_filter,
            'location_filter': self.location_filter,

            'ollayer_class': self.ollayer_class,
            'title': self.name,

            'layers': self.layers,
            'filter': self.filter,
            'request_params': self.request_params,

            'is_base_layer': self.is_base_layer,
            'single_tile': self.single_tile,
            'options': self.options,
        }

        if self.server:
            output['url'] = self.server.url

        return output


class LayerWorkspace(WorkspaceStorage):
    """
    Define a workspace: lizard-map workspace with extensions.

    TODO: some ExtJS call return function?
    """
    OWNER_TYPE_USER = 0
    OWNER_TYPE_DATASET = 1
    OWNER_TYPE_PUBLIC = 2

    OWNER_TYPE_CHOICES = (
        (OWNER_TYPE_USER, ("User")),
        (OWNER_TYPE_DATASET, ("Dataset")),
        (OWNER_TYPE_PUBLIC, ("Public")),
    )

    personal_category = models.CharField(max_length=80, null=True, blank=True)
    category = models.ForeignKey(Category, null=True, blank=True)
    data_set = models.ForeignKey(DataSet, null=True, blank=True)
    owner_type = models.IntegerField(
        choices=OWNER_TYPE_CHOICES, default=OWNER_TYPE_USER)

    objects = FilteredManager()

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return '%s %s %s' % (
            super(LayerWorkspace, self).__unicode__(),
            self.category,
            self.data_set)

    # name = models.CharField(max_length=80)
    # owner = models.ForeignKey(User, null=True, blank=True)  # Or session?

    layers = models.ManyToManyField(
         Layer, through='LayerWorkspaceItem',
         null=True, blank=True)

    # def __unicode__(self):
    #     return '%s' % (self.name)

    # def get_absolute_url(self):
    #     return reverse('lizard_workspace_api_workspace_detail',
    #                    kwargs={'id': self.id})

    def get_workspace_layers(self):
        layers = LayerWorkspaceItem.objects.filter(
            layer_workspace=self).order_by('index').select_related('layer')

        output = []

        for layer in layers:
            item = {
                'id': layer.layer.id,
                'title': layer.layer.name,
                'text': layer.layer.name,
                'use_location_filter': layer.layer.use_location_filter,
                'location_filter': layer.layer.location_filter,
                'order': layer.index,

                'ollayer_class': layer.layer.ollayer_class,
                'url': None,
                'layers': layer.layer.layers,
                'filter': layer.layer.filter,
                'request_params': layer.layer.request_params,

                'is_base_layer': layer.layer.is_base_layer,
                'single_tile': layer.layer.single_tile,
                'options': layer.layer.options,

                'visibility': layer.visible,
                'opacity': layer.opacity,
                'clickable': layer.clickable,
                'filter_string': layer.filter_string,
            }
            if layer.layer.server:
                item['url'] = layer.layer.server.url

            output.append(item)
        return output

    def save_workspace_layers(self, layers):
        """
            save layer object to database
        """
        #todo remove removed layers
        for layer in layers:
            try:
                layer_item, new = self.layerworkspaceitem_set.get_or_create(
                    layer=Layer.objects.get(pk=layer['id']))
                layer_item.visible = layer['visibility']
                layer_item.clickable = layer['clickable']
                layer_item.index = layer['order']
                layer_item.save()
            except Layer.DoesNotExist:
                print "layer %s bestaat niet. Achtergrond kaart?"%layer['title']

        return True


class LayerWorkspaceItem(models.Model):
    """
    Define an item in a workspace
    """
    layer_workspace = models.ForeignKey(LayerWorkspace)
    layer = models.ForeignKey(Layer)

    filter_string = models.CharField(max_length=124, null=True, blank=True)

    visible = models.BooleanField(default=True)
    clickable = models.BooleanField(
        default=True, help_text='Only possible is Layer.is_clickable')

    index = models.IntegerField(default=100)
    opacity = models.IntegerField(default=0)
    # custom layout

    def __unicode__(self):
        return '%s %s' % (self.layer_workspace, self.layer)


class LayerFolder(AL_Node):
    """
    maps with layers

    Contains layers directly and layers referenced by tags
    """
    name = models.CharField(max_length=128)
    layers = models.ManyToManyField(Layer, blank=True, null=True)
    layer_tag = models.ManyToManyField(Tag, blank=True, null=True)
    parent = models.ForeignKey('self',
                           related_name='children_set',
                           null=True, blank=True,
                           db_index=True)
    node_order_by = ['name']

    def __unicode__(self):
        return self.name

    def layers_dict(self):
        """
        Return layers and layers referenced by tags in a dict form.

        TODO: add 'checked' to the layers that are in the current workspace.
        """
        layers = (
            self.layers.all() |
            Layer.objects.filter(
                tags__in=self.layer_tag.all())).distinct().order_by('name')

        output = []

        for layer in layers:
            item = layer.get_object_dict()
            item['plid'] = layer.id
            item['text'] = layer.name
            item['leaf'] = True
            item['checked'] = False
            #del item['id']

            output.append(item)

        return output
#        return [layer.get_object_dict()
#        for layer in layers]
#=======
#            self.layers.filter(valid=True) |
#            Layer.objects.filter(
#                tags__in=self.layer_tag.all(), valid=True)).distinct().order_by('name')
#        return [{'plid': layer.id, 'text': layer.name,
#                 'leaf': True, 'checked': False}
#                for layer in layers]
#>>>>>>> 39d63d892bf00d0cb8c100aeaa9b11bfc0a7d1ec

    @classmethod
    def tree_dict(cls, parent_id=None):
        """
        Output folder hierarchy with layers in dict form.

            {'plid':1, 'text': 'map1', 'children': [
                {'plid':3, 'text': 'leaf 3', 'leaf': True},
                {'plid':4, 'text': 'leaf 4', 'leaf': True},
            ]},
            {'plid':2, 'text': 'map2', 'children': []}
        """
        result = []
        if parent_id is not None:
            parent_folder = cls.objects.get(id=parent_id)
            layer_folders = cls.objects.filter(parent=parent_folder)

            # Add layers and layers filtered by tags
            layer_folder_dict = parent_folder.layers_dict()
            result.extend(layer_folder_dict)
        else:
            layer_folders = cls.objects.filter(parent=None)
        layer_folders = list(layer_folders)  # Fetch from db.

        # Add children
        for layer_folder in layer_folders:
            children_layer_tree = cls.tree_dict(parent_id=layer_folder.id)
            if children_layer_tree:
                result.append(
                    {'text': layer_folder.name,
                     'children': children_layer_tree})

        return result


# class LayerFolderItem(models.Models):
#     layer = model.ForeignKey(Layer)
#     layer_folder = model.ForeignKey(LayerFolder)
#     index = model.IntegerField(default=100)


class AppScreen(models.Model):
    """
    Define a screen full of apps.
    """
    name = models.CharField(max_length=128)
    slug = models.SlugField()
    apps = models.ManyToManyField(
        'App', through='AppScreenAppItems', related_name='screen')

    def __unicode__(self):
        return self.name


class AppScreenAppItems(models.Model):
    """
    """
    appscreen = models.ForeignKey('AppScreen')
    app = models.ForeignKey('App')
    index = models.IntegerField(default=100)

    def __unicode__(self):
        return "%s %s %s" % (self.appscreen.name, self.app.name, self.index)


class AppIcons(models.Model):
    """
    Point to an icon file.
    """
    name = models.CharField(max_length=128)
    url = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name


class App(models.Model):
    """
    App.
    """

    ACTION_TYPE_NOACTION = 0
    ACTION_TYPE_URLLINK = 1
    ACTION_TYPE_PORTLET_LINK = 2
    ACTION_TYPE_APPSCREEN = 10
    ACTION_TYPE_LAYER_NAVIGATION = 20
    ACTION_TYPE_OTHER_NAVIGATION = 50

    ACTION_TYPE_CHOICES = (
        (ACTION_TYPE_NOACTION, 'no action'),
        (ACTION_TYPE_URLLINK, 'url link'),
        (ACTION_TYPE_PORTLET_LINK, 'portlet link'),
        (ACTION_TYPE_APPSCREEN, 'other appscreen'),
        (ACTION_TYPE_LAYER_NAVIGATION, 'layer navigation app'),
        (ACTION_TYPE_OTHER_NAVIGATION, 'other app'),
    )

    name = models.CharField(max_length=128)
    slug = models.SlugField()
    description = models.TextField(blank=True,
                               default='')
    mouse_over = models.CharField(max_length=256,
                                  blank=True,
                                  default='')

    icon = models.ForeignKey(AppIcons)
    action_type = models.IntegerField(
        default=ACTION_TYPE_NOACTION,
        choices=ACTION_TYPE_CHOICES
    )

    # in case of layers
    root_map = models.ForeignKey(
        LayerFolder, blank=True, null=True,
        help_text='Link to layer, layer navigation app. Will be added to action_params.')

    # Link to another app screen, in case of an appscreen link
    appscreen = models.ForeignKey(
        AppScreen, blank=True, null=True, related_name='+',
        help_text='Link to another app screen, other appscreen')

    action_params = models.TextField(
        blank=True,
        default='{}',
        help_text='dictionary with (extra) settings for action'
    )

    def __unicode__(self):
        return self.name
