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


class ThematicMap(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField()
    description = models.TextField(default="", blank=True)

    models.ForeignKey('LayerWorkspace', null=True, blank=True)

    def __unicode__(self):
        return '%s' % (self.name)


class Tag(models.Model):
    """
    Tag objects with this model using a many to many relationship.
    """
    slug = models.SlugField()

    def __unicode__(self):
        return '%s' % (self.slug)


class Layer(models.Model):
    """
    Define which layers can be chosen in your Layer Workspace

    Inspired by lizard-wms
    """
    OLLAYER_TYPE_WMS = 'OpenLayers.Layer.WMS'
    OLLAYER_TYPE_OSM = 'OpenLayers.Layer.OSM'

    OLLAYER_TYPE_CHOICES = (
        (OLLAYER_TYPE_WMS, ("WMS")),
        (OLLAYER_TYPE_OSM, ("Openstreetmap")),
    )

    #popup
    #has_legend
    #default opacity

    name = models.CharField(max_length=80)
    slug = models.SlugField()

    use_location_filter = models.BooleanField(default=False,
                            help_text="Must a workspace add a filter based on the current selected location context")
    location_filter = models.CharField(max_length=128, blank=True, null=True,
                            help_text="Parameter filter string with '{object_id}' on the location of the id.")


    ollayer_class = models.CharField(max_length=80, choices=OLLAYER_TYPE_CHOICES, default=OLLAYER_TYPE_WMS)

    #request_params for wms
    url = models.CharField(max_length=256, blank=True, null=True,
                                help_text='Url of wms of tile request format for OSM')
    layers = models.CharField(max_length=512, blank=True, null=True,
                                help_text='Layers for WMS')
    filter = models.CharField(max_length=512, blank=True, null=True)

    #request_params additional to parameters above.
    #defaults for WMS request params are:
    # format: "image/png"
    # transparent: "true"
    # ....
    request_params = models.TextField(null=True, blank=True, default='{}')

    #layer settings in openlayers (options)
    is_base_layer = models.BooleanField(default=False)
    single_tile = models.BooleanField(default=False)

    #default settings for a layer in openlayers:
    #- displayInLayerSwitcher: false (baselayers = true)
    #- displayOutsideMaxExtent: true
    options = models.TextField(null=True, blank=True, default='{}')

    category = models.ForeignKey(Category, null=True, blank=True)
    data_set = models.ForeignKey(DataSet, null=True, blank=True)
    # group_code = models.CharField(max_length=128, blank=True, null=True)
    tags = models.ManyToManyField(Tag, null=True, blank=True)

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
    OWNER_TYPE_USER = 0
    OWNER_TYPE_DATASET = 1
    OWNER_TYPE_PUBLIC = 2


    OWNER_TYPE_CHOICES = (
        (OWNER_TYPE_USER, ("User")),
        (OWNER_TYPE_DATASET, ("Dataset")),
        (OWNER_TYPE_PUBLIC, ("Public")),
    )

    personal_category = models.CharField(max_length=80, null=True, blank=True)
    category = models.ForeignKey(Category, null=True, blank=True)
    data_set = models.ForeignKey(DataSet, null=True, blank=True)
    owner_type = models.IntegerField(choices=OWNER_TYPE_CHOICES, default=OWNER_TYPE_USER)

    objects = FilteredManager()

    def __unicode__(self):
        return '%s %s %s' % (
            super(LayerWorkspace, self).__unicode__(),
            self.category,
            self.data_set)

    # name = models.CharField(max_length=80)
    # owner = models.ForeignKey(User, null=True, blank=True)  # Or session?

    layers = models.ManyToManyField(
         Layer, through='LayerWorkspaceItem',
         null=True, blank=True)

    # def __unicode__(self):
    #     return '%s' % (self.name)

    # def get_absolute_url(self):
    #     return reverse('lizard_workspace_api_workspace_detail', kwargs={'id': self.id})

    def get_workspace_layers(self):
        layers = LayerWorkspaceItem.objects.filter(layer_workspace=self).order_by('index').select_related('layer')

        output=[]

        for layer in layers:
            item = {
                'id': layer.layer.id,
                'name': layer.layer.name,
                'use_location_filter': layer.layer.use_location_filter,
                'location_filter': layer.layer.location_filter,
                'order': layer.index,

                'ollayer_class': layer.layer.ollayer_class,
                'url': layer.layer.url,
                'layers': layer.layer.layers,
                'filter': layer.layer.filter,
                'request_params': layer.layer.request_params,

                'is_base_layer': layer.layer.is_base_layer,
                'single_tile': layer.layer.single_tile,
                'options': layer.layer.options,

                'visibility': layer.visible,
                'opacity': layer.opacity,
                'clickable': layer.clickable,
                'filter_string': layer.filter_string,
            }
            output.append(item)
        return output

    def save_workspace_layers(self, layers):
        """
            save layer object to database
        """
        #todo remove removed layers
        for layer in layers:
            layer_item, new = self.layerworkspaceitem_set.get_or_create(layer=Layer.objects.get(pk=layer['id']))
            layer_item.visible = layer['visibility']
            layer_item.clickable = layer['clickable']
            layer_item.index = layer['order']
            layer.save()

        return true

class LayerWorkspaceItem(models.Model):
    """
    Define an item in a workspace
    """
    layer_workspace = models.ForeignKey(LayerWorkspace)
    layer = models.ForeignKey(Layer)

    filter_string = models.CharField(max_length=124, null=True, blank=True)

    visible = models.BooleanField(default=True)
    clickable = models.BooleanField(default=True)

    index = models.IntegerField(default=100)
    opacity = models.IntegerField(default=0)
    # custom layout

    def __unicode__(self):
        return '%s %s' % (self.layer_workspace, self.layer)


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
