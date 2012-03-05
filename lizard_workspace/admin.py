from django.contrib import admin

from lizard_workspace.models import Category
from lizard_workspace.models import Layer
from lizard_workspace.models import LayerWorkspace
from lizard_workspace.models import LayerWorkspaceItem
#from lizard_workspace.models import Theme

from lizard_map.models import WorkspaceStorageItem


class WorkspaceStorageItemInline(admin.TabularInline):
    model = WorkspaceStorageItem

class LayerWorkspaceItemInline(admin.TabularInline):
    model = LayerWorkspaceItem

class LayerWorkspaceAdmin(admin.ModelAdmin):
    inlines = [LayerWorkspaceItemInline, WorkspaceStorageItemInline, ]


class LayerAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}


#class ThemeAdmin(admin.ModelAdmin):
#    prepopulated_fields = {"slug": ("name", )}


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Layer, LayerAdmin)
admin.site.register(LayerWorkspace, LayerWorkspaceAdmin)
#admin.site.register(Theme, ThemeAdmin)
