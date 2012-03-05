import json

from djangorestframework.views import View
from django.core.urlresolvers import reverse

from djangorestframework.views import ListOrCreateModelView
from lizard_api.base import BaseApiView

from lizard_workspace.models import LayerWorkspace
from lizard_workspace.models import Layer


# class ExtendedListOrCreateModelView(ListOrCreateModelView):
#     """
#     Extension on standard ListOrCreateModelView:

#     - It can sort
#     - It can paginate
#     - It can process ExtJS POST events.
#     """
#     def get(self, *args, **kwargs):
#         """
#         Parse options from arguments.

#         - sort: list of {'property': .., 'direction': ..}
#           ASC DESC

#         How do these parameters relate?
#         - start
#         - limit
#         - page

#         {u'sort': [u'[{"property":"name","direction":"ASC"}]'],
#         u'_dc': [u'1330593105138'], u'_accept': [u'application/json'],
#         u'start': [u'0'], u'limit': [u'25'], u'page': [u'1']}

#         """
#         request = args[0]
#         sort = json.loads(request.GET.get('sort', '[]'))

#         # TODO: sort result list and paginate using sort parameters
#         return super(ExtendedListOrCreateModelView, self).get(*args, **kwargs)

#     def post(self, *args, **kwargs):
#         """
#         Add functionality to handle ExtJS requests.

#         We can filter out ExtJS request by looking at GET['action']

#         Standard request (from django REST framework):
#         - POST contains all the fields of the form
#           as well as csrfmiddlewaretoken.

#         Ext JS request:
#         - GET has 'action'
#         - POST has 'data', with all the changes given
#           i.e. ['name': 'new name', 'id': 3]
#         """

#         request = args[0]
#         action = request.GET.get('action', None)
#         if action != None:
#             # Ext JS request. Not sure yet if this works correctly
#             data = json.loads(request.POST.get('data', '[]'))
#             # If only one element is updated, you'll get a dict
#             # directly. Else you get a list with dicts in it.
#             if type(data) is dict:
#                 data = [data, ]

#             if action == 'update':
#                 # Now update the model objects. We assume that every
#                 # element is already in the database.
#                 for row in data:
#                     obj = self.resource.model.objects.get(pk=row['id'])
#                     for k, v in row.items():
#                         if k != 'id':
#                             obj.__dict__[k] = v
#                     obj.save()
#             elif action == 'create':
#                 # Create model objects.
#                 for row in data:
#                     del row['id']
#                     obj = self.resource.model(**row)
#                     obj.save()

#             elif action != None:
#                 print 'new action'
#                 print request
#         else:
#             return super(ExtendedListOrCreateModelView, self).post(*args, **kwargs)


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
        'id': 'id',
        'name': 'name',
        'slug': 'slug'
        }

    def get_object_for_api(
        self, obj, flat=True, size=BaseApiView.COMPLETE, include_geom=False):
        return {'id': obj.id, 'text': obj.name, 'slug': obj.slug,
                'children': [], 'leaf': True, 'checked': False}


