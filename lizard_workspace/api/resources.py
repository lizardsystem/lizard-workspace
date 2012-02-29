from djangorestframework.resources import ModelResource
from django.forms import ModelForm

from lizard_workspace.models import LayerWorkspace
from lizard_workspace.models import LayerWorkspaceItem
from lizard_workspace.models import Layer


class WorkspaceForm(ModelForm):
    class Meta:
        model = LayerWorkspace
        exclude = ('layers', )


class WorkspaceResource(ModelResource):
    """
    Workspaces
    """
    model = LayerWorkspace
    form = WorkspaceForm

    exclude = ('layers', )
    include = ('workspace_items', 'url', )

    def workspace_items(self, instance):
        return instance.layerworkspaceitem_set.all()

    # def url(self, instance):
    #     return instance.get_absolute_url()


class WorkspaceItemResource(ModelResource):
    """
    Workspace items
    """
    model = LayerWorkspaceItem


class LayerResource(ModelResource):
    """
    Available layers
    """
    model = Layer
    fields = ('name', 'slug', 'wms', 'category', 'data_set', 'url', )
    ordering = ('name', )

