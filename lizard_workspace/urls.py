# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin

from lizard_ui.urls import debugmode_urlpatterns
from lizard_workspace.views import CollageView

admin.autodiscover()

API_URL_NAME = 'lizard_workspace_api_root'
NAME_PREFIX = 'lizard_workspace_'


urlpatterns = patterns(
    '',
    url(r'^collage/(?P<collage_id>\d+)/$',
        CollageView.as_view(),
        name=NAME_PREFIX + 'collage_view'),
    (r'^api/',
     include('lizard_workspace.api.urls')),
    # (r'^admin/', include(admin.site.urls)),
    # url(r'^something/',
    #     direct.import.views.some_method,
    #     name="name_it"),
    )
urlpatterns += debugmode_urlpatterns()
