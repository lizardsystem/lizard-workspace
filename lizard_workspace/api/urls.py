# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin

from djangorestframework.views import InstanceModelView

# from lizard_workspace.api.views import ExtendedListOrCreateModelView
from lizard_workspace.api.views import RootView
from lizard_workspace.api.resources import LayerResource
# from lizard_workspace.api.resources import WorkspaceResource
# from lizard_workspace.api.resources import WorkspaceItemResource
from lizard_workspace.api.views import LayerWorkspaceView
from lizard_workspace.api.views import AvailableLayersView
from lizard_workspace.api.views import AppLayerTreeView
from lizard_workspace.api.views import AppScreenView

admin.autodiscover()

NAME_PREFIX = 'lizard_workspace_api_'


urlpatterns = patterns(
    '',
    url(r'^$',
        RootView.as_view(),
        name=NAME_PREFIX + 'root'),
    # url(r'^workspace/$',
    #     ExtendedListOrCreateModelView.as_view(resource=WorkspaceResource),
    #     name=NAME_PREFIX + 'workspace_list'),
    # url(r'^workspace/(?P<id>\d+)/$',
    #     InstanceModelView.as_view(resource=WorkspaceResource),
    #     name=NAME_PREFIX + 'workspace_detail'),
    # url(r'^workspace_item/$',
    #     ExtendedListOrCreateModelView.as_view(resource=WorkspaceItemResource),
    #     name=NAME_PREFIX + 'workspace_item_list'),
    # url(r'^workspace_item/(?P<id>\d+)/$',
    #     InstanceModelView.as_view(resource=WorkspaceItemResource),
    #     name=NAME_PREFIX + 'workspace_item_detail'),
    # url(r'^layer/$',
    #     ExtendedListOrCreateModelView.as_view(resource=LayerResource),
    #     name=NAME_PREFIX + 'layer_list'),
    # url(r'^layer/(?P<id>\d+)/$',
    #     InstanceModelView.as_view(resource=LayerResource),
    #     name=NAME_PREFIX + 'layer_detail'),
    url(r'^workspace_view/$',
        LayerWorkspaceView.as_view(),
        name=NAME_PREFIX + 'workspace_view'),
    url(r'^layer_view/$',
        AvailableLayersView.as_view(),
        name=NAME_PREFIX + 'layer_view'),
    url(r'^app_layer_tree/$',
        AppLayerTreeView.as_view(),
        name=NAME_PREFIX + 'app_layer_tree'),
    url(r'^appscreen/$',
        AppScreenView.as_view(),
        name=NAME_PREFIX + 'appscreen'),


    )
