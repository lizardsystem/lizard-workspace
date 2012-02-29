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
    fields = ('name', 'slug', 'wms', 'category', 'data_set', )
    ordering = ('name', )
