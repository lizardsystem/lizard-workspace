# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin

from lizard_ui.urls import debugmode_urlpatterns
from lizard_workspace.views import CollageView
from lizard_workspace.views import CollageBoxView
from lizard_workspace.views import CollageItemView

admin.autodiscover()

API_URL_NAME = 'lizard_workspace_api_root'
NAME_PREFIX = 'lizard_workspace_'


urlpatterns = patterns(
    '',
    url(r'^collage/(?P<collage_slug>\w+)/$',
        CollageView.as_view(),
        name=NAME_PREFIX + 'collage_view'),
    url(r'^collage/(?P<collage_slug>\w+)/box/$',
        CollageBoxView.as_view(),
        name=NAME_PREFIX + 'collage_box'),
    # Note: collage items are not protected by a secret slug
    url(r'^collage_item/(?P<collage_item_id>\d+)/$',
        CollageItemView.as_view(),
        name=NAME_PREFIX + 'collage_item_view'),
    (r'^api/',
     include('lizard_workspace.api.urls')),
    # (r'^admin/', include(admin.site.urls)),
    # url(r'^something/',
    #     direct.import.views.some_method,
    #     name="name_it"),
    )
urlpatterns += debugmode_urlpatterns()
