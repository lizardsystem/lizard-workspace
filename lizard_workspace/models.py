# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import json

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from lizard_security.manager import FilteredManager
from lizard_security.models import DataSet

from lizard_map.models import WorkspaceStorage
from lizard_map.models import ADAPTER_CLASS_WMS


class Category(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField()

    def __unicode__(self):
        return '%s' % (self.name)


class Theme(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField()

    def __unicode__(self):
        return '%s' % (self.name)


class Layer(models.Model):
    """
    Define which layers can be chosen in your Layer Workspace

    Inspired by lizard-wms
    """
    name = models.CharField(max_length=80)
    slug = models.SlugField()
    wms = models.URLField()
    params = models.TextField(null=True, blank=True)
    options = models.TextField(null=True, blank=True)

    category = models.ForeignKey(Category, null=True, blank=True)
    data_set = models.ForeignKey(DataSet, null=True, blank=True)

    objects = FilteredManager()

    def __unicode__(self):
        return '%s' % (self.name)

    def adapter_layer_json(self):
        """Call this function to add an item to your workspace
        """
        return json.dumps({
                'name': self.name,
                'url': self.wms,
                'params': self.params,
                'options': self.options})

    def adapter_class(self):
        """Call this function to add an item to your workspace
        """
        return ADAPTER_CLASS_WMS


class LayerWorkspace(WorkspaceStorage):
    """
    Define a workspace: lizard-map workspace with extensions.

    TODO: some ExtJS call return function?
    """

    theme = models.ForeignKey(Theme, null=True, blank=True)
    category = models.ForeignKey(Category, null=True, blank=True)
    data_set = models.ForeignKey(DataSet, null=True, blank=True)

    objects = FilteredManager()

    def __unicode__(self):
        return '%s %s %s %s' % (
            super(LayerWorkspace, self).__unicode__(),
            theme,
            category,
            data_set)

    # name = models.CharField(max_length=80)
    # owner = models.ForeignKey(User, null=True, blank=True)  # Or session?

    # layers = models.ManyToManyField(
    #     Layer, through='LayerWorkspaceItem',
    #     null=True, blank=True)

    # def __unicode__(self):
    #     return '%s' % (self.name)

    # def get_absolute_url(self):
    #     return reverse('lizard_workspace_api_workspace_detail', kwargs={'id': self.id})


# class LayerWorkspaceItem(models.Model):
#     """
#     Define an item in a workspace
#     """
#     layer_workspace = models.ForeignKey(LayerWorkspace)
#     layer = models.ForeignKey(Layer)
#     category = models.ForeignKey(Category, null=True, blank=True)

#     visible = models.BooleanField(default=True)
#     clickable = models.BooleanField(default=True)

#     index = models.IntegerField(default=100)
#     # opacity = models.Float
#     # custom layout

#     def __unicode__(self):
#         return '%s %s %s' % (self.layer_workspace, self.layer, self.category)


# class UserLayerWorkspaceItem(models.Model):
#     """
#     User defined workspace item: essentially a wms.
#     """
#     layer_workspace = models.ForeignKey(LayerWorkspace)

#     name = models.CharField(max_length=80)
#     wms = models.URLField()
#     index = models.IntegerField(default=100)

#     def __unicode__(self):
#         return '%s' % self.name
