# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import transaction

import optparse
import datetime
import logging

from lizard_workspace.models import (
    LayerWorkspaceItem,
    LayerWorkspace,
    Layer,
    Tag,
)

logger = logging.getLogger(__name__) 

def _option(option, help_text):
    """
    Return an option.
    """
    return optparse.make_option(
        '--' + option,
        action='store_true',
        dest=option,
        default=False,
        help=help_text,
    )


def _create_or_replace_merged_layer(name, slug, tag, layers):
    """
    Return created layer object.

    Laye is created with name and slug, and layers assembled from layers
    field of contributing layers. Contributing layers are looked up by
    the same layers field.
    """
    Layer.objects.filter(slug=slug).delete()
    
    contributing_layers = Layer.objects.filter(
        layers__in=layers,
    )
    layer = Layer.objects.create(
        slug=slug,
        name=name,
        source_ident='workspace-update-command',
        server=contributing_layers[0].server,
        layers=','.join(l.layers for l in contributing_layers),
    )
    layer.tags.add(tag)
    return layer


class Command(BaseCommand):
    args = ''
    help = 'Run some updating code based on provided options.'

    option_list = BaseCommand.option_list + (
        _option('baselayers', 'Configure baselayers'),
        _option('watersystem', 'Configure watersystem layers'),
    )

    def _baselayers(self):
        """
        Reconfigure layers that have is_base_layer=True
        """
        TOP10NL_LAYER_SLUG = 'top10nl'
        TOP10NL_TAG_SLUG = 'server_pdok-top10'

        # Get open streetmap, rename if necessary
        try:
            osm = Layer.objects.get(name='openstreetmap')
            osm.name = 'OpenStreetMap'
            osm.save()
        except:
            osm = Layer.objects.get(name='OpenStreetMap')

        # Remove anything except osm
            Layer.objects.filter(
                is_base_layer=True,
            ).exclude(
                pk=osm.pk,
            ).update(is_base_layer=False)

        # Remove old baselayer(s) for the top10nl if it exists
            Layer.objects.filter(slug=TOP10NL_LAYER_SLUG).delete()

        # Add a baselayer for the top10nl
            tag = Tag.objects.get(slug=TOP10NL_TAG_SLUG)
            top10_layers = tag.layer_set.all()
            new_layer = top10_layers[0]
            new_layer.name = 'Top10NL'
            new_layer.slug = TOP10NL_LAYER_SLUG
            new_layer.is_base_layer = True
            new_layer.layers = ','.join(l.layers for l in top10_layers)
            new_layer.source_ident = None
            new_layer.pk = None  # We want a new layer.
            new_layer.save()
            new_layer.tags.clear()

    def _watersystem(self):
        """
        Reconfigure layers for the watersystem map.
        """
        WORKSPACE_SLUG = 'watersysteemkaart'
        TAG_SLUG = 'basis'
        
        # Clear the layer workspace, get the tag
        layer_workspace = LayerWorkspace.objects.get(
            slug=WORKSPACE_SLUG,
        )
        LayerWorkspaceItem.objects.filter(
            layer_workspace=layer_workspace,
        ).delete()
        tag = Tag.objects.get_or_create(slug=TAG_SLUG)[0]

        # Create layers and add to workspace
        # Kunstwerken basis
        layer = _create_or_replace_merged_layer(
            slug='kunstwerken-basis',
            name='Kunstwerken Basis',
            tag=tag,
            layers=['wsh:gemaal', 'wsh:stuw', 'wsh:sluis'],
        )
        LayerWorkspaceItem.objects.create(
            layer_workspace=layer_workspace,
            layer=layer,
            index=10,
        )
            
        # Kunstwerken extra
        layer = _create_or_replace_merged_layer(
            slug='kunstwerken-extra',
            name='Kunstwerken Extra',
            tag=tag,
            layers=[
                'wsh:vispassage', 'wsh:vaste_dam', 'wsh:sifon',
                'wsh:duiker', 'wsh:coupure', 'wsh:brug', 'wsh:aquaduct',
            ],
        )
        LayerWorkspaceItem.objects.create(
            layer_workspace=layer_workspace,
            layer=layer,
            visible=False,
            index=20,
        )

        # Peilgebied
        layer = _create_or_replace_merged_layer(
            slug='peilgebied-basis',
            name='Peilgebied',
            tag=tag,
            layers=['wsh:peilgebied'],
        )
        LayerWorkspaceItem.objects.create(
            layer_workspace=layer_workspace,
            layer=layer,
            visible=False,
            index=30,
        )
    
        # Waterloop
        layer = _create_or_replace_merged_layer(
            slug='waterloop-basis',
            name='Waterloop',
            tag=tag,
            layers=['wsh:waterloop'],
        )
        LayerWorkspaceItem.objects.create(
            layer_workspace=layer_workspace,
            layer=layer,
            visible=False,
            index=40,
        )

        # Waterlichaam
        layer = _create_or_replace_merged_layer(
            slug='krw_waterlichaam',
            name='KRW-waterlichaam',
            tag=tag,
            layers=[
                'vss:krw_waterbody_polygon',
                'vss:krw_waterbody_linestring',
            ],
        )
        LayerWorkspaceItem.objects.create(
            layer_workspace=layer_workspace,
            layer=layer,
            visible=False,
            index=60,
        )

        layer = Layer.objects.get(slug='vss_measure')
        layer.name = 'Maatregelen'
        layer.save()
        LayerWorkspaceItem.objects.create(
            layer_workspace=layer_workspace,
            layer=layer,
            visible=False,
            index=70,
        )

        layer = Layer.objects.get(slug='witte-waas-gebieden')
        layer.name = 'Witte waas'
        layer.save()
        LayerWorkspaceItem.objects.create(
            layer_workspace=layer_workspace,
            layer=layer,
            visible=False,
            index=90,
        )

    @transaction.commit_on_success
    def handle(self, *args, **options):
        if options.get('baselayers'):
            self._baselayers()
        if options.get('watersystem'):
            self._watersystem()
