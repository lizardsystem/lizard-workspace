# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from lizard_security.manager import FilteredGeoManager
from lizard_security.models import DataSet


class Category(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField()

    def __unicode__(self):
        return '%s' % (self.name)


class Layer(models.Model):
    """
    Define which layers can be chosen in your Layer Workspace
    """
    name = models.CharField(max_length=80)
    slug = models.SlugField()
    wms = models.URLField()
    category = models.ForeignKey(Category, null=True, blank=True)

    data_set = models.ForeignKey(DataSet, null=True, blank=True)
    # Extra params to wms?

    def __unicode__(self):
        return '%s' % (self.name)


class Theme(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField()

    def __unicode__(self):
        return '%s' % (self.name)


class LayerWorkspace(models.Model):
    """
    Define a workspace
    """
    name = models.CharField(max_length=80)
    owner = models.ForeignKey(User, null=True, blank=True)  # Or session?

    theme = models.ForeignKey(Theme, null=True, blank=True)
    data_set = models.ForeignKey(DataSet, null=True, blank=True)
    layers = models.ManyToManyField(
        Layer, through='LayerWorkspaceItem',
        null=True, blank=True)

    def __unicode__(self):
        return '%s' % (self.name)

    # def get_absolute_url(self):
    #     return reverse('lizard_workspace_api_workspace_detail', kwargs={'id': self.id})


class LayerWorkspaceItem(models.Model):
    """
    Define an item in a workspace
    """
    layer_workspace = models.ForeignKey(LayerWorkspace)
    layer = models.ForeignKey(Layer)
    category = models.ForeignKey(Category, null=True, blank=True)

    visible = models.BooleanField(default=True)
    clickable = models.BooleanField(default=True)

    index = models.IntegerField(default=100)
    # opacity = models.Float
    # custom layout

    def __unicode__(self):
        return '%s %s %s' % (self.layer_workspace, self.layer, self.category)


class UserLayerWorkspaceItem(models.Model):
    """
    User defined workspace item: essentially a wms.
    """
    layer_workspace = models.ForeignKey(LayerWorkspace)

    name = models.CharField(max_length=80)
    wms = models.URLField()
    index = models.IntegerField(default=100)

    def __unicode__(self):
        return '%s' % self.name
