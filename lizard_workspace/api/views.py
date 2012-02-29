from djangorestframework.views import View
from django.core.urlresolvers import reverse


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
