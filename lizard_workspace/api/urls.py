# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin

from djangorestframework.views import InstanceModelView
from djangorestframework.views import ListOrCreateModelView

from lizard_workspace.api.views import RootView
from lizard_workspace.api.resources import LayerResource
from lizard_workspace.api.resources import WorkspaceResource
from lizard_workspace.api.resources import WorkspaceItemResource

admin.autodiscover()

NAME_PREFIX = 'lizard_workspace_api_'


urlpatterns = patterns(
    '',
    url(r'^$',
        RootView.as_view(),
        name=NAME_PREFIX + 'root'),
    url(r'^workspace/$',
        ListOrCreateModelView.as_view(resource=WorkspaceResource),
        name=NAME_PREFIX + 'workspace_list'),
    url(r'^workspace/(?P<id>\d+)/$',
        InstanceModelView.as_view(resource=WorkspaceResource),
        name=NAME_PREFIX + 'workspace_detail'),
    url(r'^workspace_item/$',
        ListOrCreateModelView.as_view(resource=WorkspaceItemResource),
        name=NAME_PREFIX + 'workspace_item_list'),
    url(r'^workspace_item/(?P<id>\d+)/$',
        InstanceModelView.as_view(resource=WorkspaceItemResource),
        name=NAME_PREFIX + 'workspace_item_detail'),
    url(r'^layer/$',
        ListOrCreateModelView.as_view(resource=LayerResource),
        name=NAME_PREFIX + 'layer_list'),
    url(r'^layer/(?P<id>\d+)/$',
        InstanceModelView.as_view(resource=LayerResource),
        name=NAME_PREFIX + 'layer_detail'),
    )
