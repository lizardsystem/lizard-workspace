from django.contrib import admin

from lizard_workspace.models import Category, LayerFolder, Tag
from lizard_workspace.models import Layer
from lizard_workspace.models import LayerCollage
from lizard_workspace.models import LayerCollageItem
from lizard_workspace.models import LayerWorkspace
from lizard_workspace.models import LayerWorkspaceItem
from lizard_workspace.models import AppScreenAppItems
from lizard_workspace.models import App
from lizard_workspace.models import AppScreen
from lizard_workspace.models import AppIcons
from lizard_workspace.models import SyncTask
from lizard_workspace.models import WmsServer

from lizard_map.models import WorkspaceStorageItem


class WorkspaceStorageItemInline(admin.TabularInline):
    model = WorkspaceStorageItem


class LayerWorkspaceItemInline(admin.TabularInline):
    model = LayerWorkspaceItem


class LayerCollageItemInline(admin.TabularInline):
    model = LayerCollageItem


class AppScreenAppItemsInline(admin.TabularInline):
    model = AppScreenAppItems


class LayerWorkspaceAdmin(admin.ModelAdmin):
    inlines = [LayerWorkspaceItemInline, WorkspaceStorageItemInline, ]


class LayerCollageAdmin(admin.ModelAdmin):
    inlines = [LayerCollageItemInline, ]
    list_display = ('name', 'secret_slug', 'owner', 'is_temp', )
    list_filter = ('owner', )


class LayerAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ('valid', 'data_set', 'source_ident', 'is_local_server', )
    list_display = ('name', 'valid', 'data_set', 'source_ident',
                    'filter', 'is_local_server', 'tags_str')
    prepopulated_fields = {"slug": ("name", )}


class AppScreenAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}
    inlines = [AppScreenAppItemsInline]


class AppAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}


#class ThemeAdmin(admin.ModelAdmin):
#    prepopulated_fields = {"slug": ("name", )}


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}


class TagAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'layer_count')



class LayerFolderAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'children_str', ]
    filter_horizontal = ('layers', 'layer_tag', )
    search_fields = ['name']

class SyncTaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'server', 'data_set', 'tag', 'last_sync', 'last_result']
    search_fields = ['name']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Layer, LayerAdmin)
admin.site.register(LayerWorkspace, LayerWorkspaceAdmin)
admin.site.register(LayerCollage, LayerCollageAdmin)
#admin.site.register(Theme, ThemeAdmin)

admin.site.register(App, AppAdmin)
admin.site.register(AppScreen, AppScreenAdmin)
admin.site.register(AppIcons)

admin.site.register(LayerFolder, LayerFolderAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(SyncTask, SyncTaskAdmin)
admin.site.register(WmsServer)
