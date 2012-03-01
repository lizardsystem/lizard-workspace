import json

from djangorestframework.views import View
from django.core.urlresolvers import reverse

from djangorestframework.views import ListOrCreateModelView


class ExtendedListOrCreateModelView(ListOrCreateModelView):
    """
    Extension on standard ListOrCreateModelView:

    - It can sort
    - It can paginate
    - It can process ExtJS POST events.
    """
    def get(self, *args, **kwargs):
        """
        Parse options from arguments.

        - sort: list of {'property': .., 'direction': ..}
          ASC DESC

        How do these parameters relate?
        - start
        - limit
        - page

        {u'sort': [u'[{"property":"name","direction":"ASC"}]'],
        u'_dc': [u'1330593105138'], u'_accept': [u'application/json'],
        u'start': [u'0'], u'limit': [u'25'], u'page': [u'1']}

        """
        request = args[0]
        sort = json.loads(request.GET.get('sort', '[]'))

        # TODO: sort result list and paginate using sort parameters
        return super(ExtendedListOrCreateModelView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """
        Add functionality to handle ExtJS requests.

        We can filter out ExtJS request by looking at GET['action']

        Standard request (from django REST framework):
        - POST contains all the fields of the form
          as well as csrfmiddlewaretoken.

        Ext JS request:
        - GET has 'action'
        - POST has 'data', with all the changes given
          i.e. ['name': 'new name', 'id': 3]
        """

        request = args[0]
        action = request.GET.get('action', None)
        if action != None:
            # Ext JS request. Not sure yet if this works correctly
            data = json.loads(request.POST.get('data', '[]'))
            # If only one element is updated, you'll get a dict
            # directly. Else you get a list with dicts in it.
            if type(data) is dict:
                data = [data, ]

            if action == 'update':
                # Now update the model objects. We assume that every
                # element is already in the database.
                for row in data:
                    obj = self.resource.model.objects.get(pk=row['id'])
                    for k, v in row.items():
                        if k != 'id':
                            obj.__dict__[k] = v
                    obj.save()
            elif action == 'create':
                # Create model objects.
                for row in data:
                    del row['id']
                    obj = self.resource.model(**row)
                    obj.save()

            elif action != None:
                print 'new action'
                print request
        else:
            return super(ExtendedListOrCreateModelView, self).post(*args, **kwargs)


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
