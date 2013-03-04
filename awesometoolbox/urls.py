from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from awesometoolbox.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', index, name='index'),

    url(r'^tools/$', all_tools, name='all_tools'),
    url(r'^tools/(?P<tool_id>\d+)/$', tool_page, name='tool_page'),
    url(r'^tools/(?P<tool_id>\d+)/delete/$', delete_tool, name='delete_tool'),
    url(r'^tools/(?P<tool_id>\d+)/rate/(?P<rating_value>\d)$', add_rating, name='add_rating'),
    url(r'^tools/new/$', new_tool, name='new_tool'),

    # url(r'^toolboxes/$', 'awesometoolbox.views.all_toolboxes', name='all_toolboxes'),
    url(r'^toolboxes/(?P<toolbox_id>\d+)/$', toolbox_page, name='toolbox_page'),
    url(r'^toolboxes/(?P<toolbox_id>\d+)/delete/$', delete_toolbox, name='delete_toolbox'),
    url(r'^toolboxes/new/$', new_toolbox, name='new_toolbox'),

    url(r'^toolboxes/(?P<toolbox_id>\d+)/add/(?P<tool_id>\d+)/$', add_tool_to_toolbox, name='add_tool_to_toolbox'),
    url(r'^toolboxes/(?P<toolbox_id>\d+)/remove/(?P<tool_id>\d+)/$', remove_tool_from_toolbox, name='remove_tool_from_toolbox'),

    # url(r'^categories/$', 'awesometoolbox.views.all_categories', name='all_categories'),
    url(r'^categories/(?P<category_id>\d+)/$', 'awesometoolbox.views.category_page', name='category_page'),

    # url(r'^login/$', login_view, name='login_view'),
    # url(r'^logout/$', logout_view, name='logout_view'),
    # url(r'^signup/$', signup, name='signup'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('registration.urls')),
)