from django.contrib import admin

from lizard_workspace.models import Category, LayerFolder, Tag
from lizard_workspace.models import Layer
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

class AppScreenAppItemsInline(admin.TabularInline):
    model = AppScreenAppItems


class LayerWorkspaceAdmin(admin.ModelAdmin):
    inlines = [LayerWorkspaceItemInline, WorkspaceStorageItemInline, ]


class LayerAdmin(admin.ModelAdmin):
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


admin.site.register(Category, CategoryAdmin)
admin.site.register(Layer, LayerAdmin)
admin.site.register(LayerWorkspace, LayerWorkspaceAdmin)
#admin.site.register(Theme, ThemeAdmin)

admin.site.register(App, AppAdmin)
admin.site.register(AppScreen, AppScreenAdmin)
admin.site.register(AppIcons)

admin.site.register(LayerFolder)
admin.site.register(Tag)
admin.site.register(SyncTask)
admin.site.register(WmsServer)
