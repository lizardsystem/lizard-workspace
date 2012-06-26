import json
from django.shortcuts import get_object_or_404

from djangorestframework.views import View
from django.core.urlresolvers import reverse

from djangorestframework.views import ListOrCreateModelView
from lizard_api.base import BaseApiView
from lizard_history.utils import get_simple_history

from lizard_workspace.models import AppScreen
from lizard_workspace.models import Layer
from lizard_workspace.models import LayerFolder
from lizard_workspace.models import LayerCollage
from lizard_workspace.models import LayerWorkspace


class RootView(View):
    """
    Class based REST root view for lizard_workspace.
    """
    def get(self, request):
        return {
            'workspace': {
                'name': 'identifier',
                'url': reverse("lizard_workspace_api_workspace_view")},
            'collage': {
                'name': 'identifier',
                'url': reverse("lizard_workspace_api_collage_view")},
            }


class LayerWorkspaceView(BaseApiView):
    """
    API for LayerWorkspace
    """
    model_class = LayerWorkspace
    name_field = 'name'
    slug_field = 'slug'

    valid_field = None

    field_mapping = {
        'id': 'id',
        'name': 'name',
        'personal_category': 'personal_category',
        'category': 'category__name',
        'owner_type': 'owner_type',
        'data_set': 'data_set',
        'owner': 'owner_id',
        'layers': 'layers__name',
        'read_only': 'owner_type',
    }

    read_only_fields = [
        'tmp',
        'category',
        'data_set',
        'type',
        'read_only'
    ]

    use_filtered_model = True


    def get_filtered_model(self, request):

        return self.model_class.objects.filter(
                   owner=request.user,
                   owner_type=LayerWorkspace.OWNER_TYPE_USER
            ) | self.model_class.objects.exclude(
            owner_type=LayerWorkspace.OWNER_TYPE_USER)

    def get_object_for_api(self,
                           worksp,
                           flat=True,
                           size=BaseApiView.COMPLETE,
                           include_geom=False):
        """
        create object of workspace
        """

        # You get a dict with keys datetime_modified, modified_by,
        # created_by, datetime_created
        history = get_simple_history(worksp)

        if size == self.ID_NAME:
            output = {
                'id': worksp.id,
                'name': worksp.name,
            }
        elif size == self.MEDIUM or size == self.SMALL:
            output = {
                'id': worksp.id,
                'name': worksp.name,
                'personal_category': worksp.personal_category,
                'category': self._get_related_object(
                    worksp.category,
                    flat
                ),
                'data_set': self._get_related_object(
                    worksp.data_set,
                    flat
                ),
                'owner': self._get_related_object(
                    worksp.owner,
                    flat
                ),
                'owner_type': self._get_choice(
                    worksp.owner_type,
                    flat
                ),
                'read_only': not(worksp.owner_type == self.model_class.OWNER_TYPE_USER),
                'datetime_modified': history['datetime_modified'],
                'datetime_created': history['datetime_created'],
            }

        elif size == self.COMPLETE:
            output = {
                'id': worksp.id,
                'name': worksp.name,
                'personal_category': worksp.personal_category,
                'category': self._get_related_object(
                    worksp.category,
                    flat
                ),
                'data_set': self._get_related_object(
                    worksp.data_set,
                    flat
                ),
                'owner': self._get_related_object(
                    worksp.owner,
                    flat
                ),
                'owner_type': self._get_choice(
                    self.model_class._meta.get_field('owner_type'),
                    worksp.owner_type,
                    flat
                ),
                'read_only': not(worksp.owner_type == self.model_class.OWNER_TYPE_USER),
                'layers': worksp.get_workspace_layers(),
                'datetime_modified': history['datetime_modified'],
                'datetime_created': history['datetime_created'],
            }
        # Only for collages, the collage view uses the same class.
        if 'secret_slug' in worksp.__dict__:
            output['secret_slug'] = worksp.secret_slug
        if 'is_temp' in worksp.__dict__:
            output['is_temp'] = worksp.is_temp
        return output

    def create_objects(self, data, request=None):
        """
            overwrite of base api to append code
        """
        for rec in data:
            if not 'owner' in rec or not rec['owner']:
                rec['owner'] = {'id': request.user.id}


        success, touched_objects =  super(LayerWorkspaceView, self).create_objects(data)

        #for object in touched_objects:
        #    object.code = object.id + 1000
        #    object.save()

        return success, touched_objects

    def update_many2many(self, record, model_field, linked_records):
        """
        update specific part of manyToMany relations.
        input:
        - record: measure
        - model_field. many2many field object
        - linked_records. list with dictionaries with:
            id: id of related objects
            optional some relations in case the relation is through
            another object
        """
        # TODO: do we need to 'touch' the workspace or collage object?
        #record.description = 'asdfarjan'
        #record.save()  # Update modified date

        if model_field.name == 'layers':
            record.save_workspace_layers(linked_records)
        else:
            #??
            self.save_single_many2many_relation(record,
                model_field,
                linked_records,
            )


class LayerCollageView(LayerWorkspaceView):
    """
    API for LayerCollage

    Not sure if this works.. but it should be very similar to the
    LayerWorkspaceView
    """
    model_class = LayerCollage

    field_mapping = {
        'id': 'id',
        'name': 'name',
        'personal_category': 'personal_category',
        'category': 'category__name',
        'owner_type': 'owner_type',
        'data_set': 'data_set',
        'owner': 'owner_id',
        'layers': 'layers__name',
        'read_only': 'owner_type',
        'is_temp': 'is_temp',
        'secret_slug': 'secret_slug',
    }

    read_only_fields = [
        'tmp',
        'category',
        'data_set',
        'type',
        'read_only',
        'secret_slug',
    ]

    def get_filtered_model(self, request):
        return super(LayerCollageView, self).get_filtered_model(
            request).exclude(is_temp=True)


class AvailableLayersView(BaseApiView):
    """
    Show available layers
    """
    model_class = Layer
    name_field = 'name'

    valid_field = None

    field_mapping = {
        'slug': 'slug',
        'id': 'id',
        'name': 'name',
        'use_location_filter': 'use_location_filter',
        'location_filter': 'location_filtere',
        'ollayer_class': 'ollayer_class',
        'url': 'url',
        'owner': 'owner',
        'filter': 'filter',
        'request_params': 'request_params',
        'is_base_layer': 'is_base_layer',
        'single_tile': 'single_tile',
        'options': 'options',
        'is_local_server': 'is_local_server',
        'is_clickable': 'is_clickable',
        'js_popup_class': 'js_popup_class'
    }

    read_only_fields = [

    ]

    def get_object_for_api(self,
                           layer,
                           flat=True,
                           size=BaseApiView.COMPLETE,
                           include_geom=False):
        """
        create object of measure
        """
        if size == self.ID_NAME:
            output = {
                'id': layer.id,
                'name': layer.name,
            }
        else:
            output = layer.get_object_dict()

        return output



class AppLayerTreeView(View):
    """
    Return tree of LayerFolder
    """
    def get(self, request):
        """
        object_id: id of rootmap LayerFolder.

        -provide 'object_id=' to get the root
        -if you don't provide object_id, you'll get nothing
        """
        try:
            parent_id = request.GET['object_id']
            if not parent_id:
                parent_id = None
            result = LayerFolder.tree_dict(parent_id)
        except:
            result = []

        return result


class AppScreenView(View):

    def get(self, request):

        object_id = request.GET.get('object_id', None)

        appscreen = get_object_or_404(AppScreen, slug=object_id)

        output = []

        for app_item in appscreen.appscreenappitems_set.all().select_related(
            'app', 'app__icon').order_by('index'):

            try:
                action_params = json.loads(app_item.app.action_params)
            except:
                print 'error in action_params'
                action_params = {}
            if app_item.app.root_map:
                action_params['root_map'] = app_item.app.root_map.id
            #if app.app.appscreen:
            #    action_params['appscreen'] = app.app.appscreen.slug


            output.append({
                'id': app_item.app.id,
                'name': app_item.app.name,
                'mouse_over': app_item.app.mouse_over,
                'slug': app_item.app.slug,
                'action_type': app_item.app.action_type,
                'action_params': action_params,
                'icon': app_item.app.icon.url,
                'target_app_slug': (app_item.app.appscreen.slug
                                    if app_item.app.appscreen else None)
            })



        return {
            'data': output
        }
