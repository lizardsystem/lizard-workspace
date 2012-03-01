from djangorestframework.resources import ModelResource
from django.forms import ModelForm

from lizard_workspace.models import LayerWorkspace
# from lizard_workspace.models import LayerWorkspaceItem

# from lizard_map.models import WorkspaceStorage
from lizard_map.models import WorkspaceStorageItem

from lizard_workspace.models import Layer


# class WorkspaceForm(ModelForm):
#     class Meta:
#         model = Workspace
#         exclude = ('layers', )


class WorkspaceResource(ModelResource):
    """
    Workspaces
    """
    model = LayerWorkspace
    # form = WorkspaceForm

    # exclude = ('layers', )
    # include = ('workspace_items', 'url', )
    exclude = ('owner', )
    include = ('owner_id', 'workspace_items', )

    def workspace_items(self, instance):
        return [
            {'id': wsi.id,
             'adapter_class': wsi.adapter_class,
             'adapter_layer_json': wsi.adapter_layer_json,
             'index': wsi.index,
             'name': wsi.name,
             'clickable': wsi.clickable,
             'visible': wsi.visible
             } for wsi in instance.workspace_items.all()]

    # def url(self, instance):
    #     return instance.get_absolute_url()

    def owner_id(self, instance):
        return instance.owner.id


class WorkspaceItemResource(ModelResource):
    """
    Workspace items
    """
    model = WorkspaceStorageItem

    exclude = ('workspace', )
    include = ('workspace_id', )

    def workspace_id(self, instance):
        return instance.workspace.id


class LayerResource(ModelResource):
    """
    Available layers
    """
    model = Layer
    fields = ('name', 'slug', 'wms', 'category', 'data_set', 'url', )
    ordering = ('name', )

