import json
from django.shortcuts import get_object_or_404

from djangorestframework.views import View
from django.core.urlresolvers import reverse

from djangorestframework.views import ListOrCreateModelView
from lizard_api.base import BaseApiView

from lizard_workspace.models import LayerWorkspace, AppScreen
from lizard_workspace.models import Layer


class RootView(View):
    """
    Class based REST root view for lizard_workspace.
    """
    def get(self, request):
        return {
            'workspace': {
                'name': 'identifier',
                'url': reverse("lizard_workspace_api_workspace_list")},
            'workspace-item': {
                'name': 'identifier',
                'url': reverse("lizard_workspace_api_workspace_item_list")},
            'layer': {
                'name': 'source',
                'url': reverse("lizard_workspace_api_layer_list")},
            }


class LayerWorkspaceView(BaseApiView):
    """
        Show organisations for selection and edit
    """
    model_class = LayerWorkspace
    name_field = 'name'

    valid_field = None

    field_mapping = {
        'id': 'id',
        'name': 'name',
        'personal_category': 'personal_category',
        'category': 'category__name',
        'owner_type': 'owner_type',
        'data_set': 'data_set',
        'owner': 'owner_id',
        'layers': 'layers__name'
    }

    read_only_fields = [
        'tmp',
        'category',
        'data_set',
        'type'
    ]

    def get_object_for_api(self,
                           worksp,
                           flat=True,
                           size=BaseApiView.COMPLETE,
                           include_geom=False):
        """
        create object of measure
        """
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
                    LayerWorkspace._meta.get_field('owner_type'),
                    worksp.owner_type,
                    flat
                ),
                'layers': worksp.get_workspace_layers()
                #'status_planned': measure.status_moment_string(is_planning=True),
            }
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

        if model_field.name == 'layers':
            record.save_workspace_layers(linked_records)
        else:
            #??
            self.save_single_many2many_relation(record,
                model_field,
                linked_records,
            )



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
    }

    read_only_fields = [

    ]

#    def get_object_for_api(self,
#                           layer,
#                           flat=True,
#                           size=BaseApiView.COMPLETE,
#                           include_geom=False):
#        """
#        create object of measure
#        """
#        if size == self.ID_NAME:
#            output = {
#                'id': worksp.id,
#                'name': worksp.name,
#            }
#        else:
#            output = {
#                'id': layer.id,
#                'name': layer.name,
#                'use_location_filter': layer.use_location_filter,
#                'location_filter': layer.location_filter,
#
#                'ollayer_class': layer.ollayer_class,
#                'url': layer.url,
#                'layers': layer.layers,
#                'filter': layer.filter,
#                'request_params': layer.request_params,
#
#                'is_base_layer': layer.is_base_layer,
#                'single_tile': layer.single_tile,
#                'options': layer.options,
#            }
#
#        return output



    def get_object_for_api(
        self, obj, flat=True, size=BaseApiView.COMPLETE, include_geom=False):
        return {'id': obj.id, 'text': obj.name, 'slug': obj.slug,
                'children': [], 'leaf': True, 'checked': False}


class AppLayerTreeView(View):


    def get(self, request):




        return  [
            {'plid':1, 'text': 'map1', 'children': [
                {'plid':3, 'text': 'leaf 3', 'checked': False, 'leaf': True},
                {'plid':4, 'text': 'leaf 4', 'checked': True, 'leaf': True},
            ]},
            {'plid':2, 'text': 'map2', 'children': []}
        ]


class AppScreenView(View):

    def get(self, request):

        object_id = request.GET.get('object_id', None)

        appscreen = get_object_or_404(AppScreen, slug=object_id)

        output = []

        for app in appscreen.appscreenappitems_set.all().select_related('app', 'app__icon').order_by('index'):

            try:
                action_params = json.loads(app.app.action_params)
            except:
                print 'error in action_params'
                action_params = {}
            if app.app.root_map:
                action_params['root_map'] = app.app.root_map.id
            #if app.app.appscreen:
            #    action_params['appscreen'] = app.app.appscreen.slug


            output.append({
                'id': app.app.id,
                'name': app.app.name,
                'mouse_over': app.app.mouse_over,
                'slug': app.app.slug,
                'action_type': app.app.action_type,
                'action_params': action_params,
                'icon': app.app.icon.url,
            })



        return {
            'data': output
        }
