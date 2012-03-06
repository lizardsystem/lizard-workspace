# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SyncTask'
        db.create_table('lizard_workspace_synctask', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_workspace.WmsServer'])),
            ('data_set', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_security.DataSet'], null=True, blank=True)),
            ('last_sync', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('last_result', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('lizard_workspace', ['SyncTask'])

        # Adding model 'WmsServer'
        db.create_table('lizard_workspace_wmsserver', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=256, blank=True)),
            ('abstract', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('lizard_workspace', ['WmsServer'])

        # Deleting field 'Layer.url'
        db.delete_column('lizard_workspace_layer', 'url')

        # Adding field 'Layer.server'
        db.add_column('lizard_workspace_layer', 'server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_workspace.WmsServer'], null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'SyncTask'
        db.delete_table('lizard_workspace_synctask')

        # Deleting model 'WmsServer'
        db.delete_table('lizard_workspace_wmsserver')

        # Adding field 'Layer.url'
        db.add_column('lizard_workspace_layer', 'url', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True), keep_default=False)

        # Deleting field 'Layer.server'
        db.delete_column('lizard_workspace_layer', 'server_id')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'lizard_map.backgroundmap': {
            'Meta': {'ordering': "('index',)", 'object_name': 'BackgroundMap'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'google_type': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'is_base_layer': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'layer_names': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'layer_type': ('django.db.models.fields.IntegerField', [], {}),
            'layer_url': ('django.db.models.fields.CharField', [], {'default': "'http://tile.openstreetmap.nl/tiles/${z}/${x}/${y}.png'", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'lizard_map.workspacestorage': {
            'Meta': {'object_name': 'WorkspaceStorage'},
            'absolute': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'background_map': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_map.BackgroundMap']", 'null': 'True', 'blank': 'True'}),
            'custom_time': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dt_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dt_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'td': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'td_end': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'td_start': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'x_max': ('django.db.models.fields.FloatField', [], {'default': '1254790'}),
            'x_min': ('django.db.models.fields.FloatField', [], {'default': '-14675'}),
            'y_max': ('django.db.models.fields.FloatField', [], {'default': '6964942'}),
            'y_min': ('django.db.models.fields.FloatField', [], {'default': '6668977'})
        },
        'lizard_security.dataset': {
            'Meta': {'ordering': "['name']", 'object_name': 'DataSet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'})
        },
        'lizard_workspace.app': {
            'Meta': {'object_name': 'App'},
            'action_params': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'blank': 'True'}),
            'action_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'appscreen': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['lizard_workspace.AppScreen']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'icon': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_workspace.AppIcons']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mouse_over': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'root_map': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_workspace.LayerFolder']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'lizard_workspace.appicons': {
            'Meta': {'object_name': 'AppIcons'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'lizard_workspace.appscreen': {
            'Meta': {'object_name': 'AppScreen'},
            'apps': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'screen'", 'symmetrical': 'False', 'through': "orm['lizard_workspace.AppScreenAppItems']", 'to': "orm['lizard_workspace.App']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'lizard_workspace.appscreenappitems': {
            'Meta': {'object_name': 'AppScreenAppItems'},
            'app': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_workspace.App']"}),
            'appscreen': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_workspace.AppScreen']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '100'})
        },
        'lizard_workspace.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'lizard_workspace.layer': {
            'Meta': {'object_name': 'Layer'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_workspace.Category']", 'null': 'True', 'blank': 'True'}),
            'data_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_security.DataSet']", 'null': 'True', 'blank': 'True'}),
            'filter': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_base_layer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'layers': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'location_filter': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'ollayer_class': ('django.db.models.fields.CharField', [], {'default': "'OpenLayers.Layer.WMS'", 'max_length': '80'}),
            'options': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'null': 'True', 'blank': 'True'}),
            'owner_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'request_params': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'null': 'True', 'blank': 'True'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_workspace.WmsServer']", 'null': 'True', 'blank': 'True'}),
            'single_tile': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['lizard_workspace.Tag']", 'null': 'True', 'blank': 'True'}),
            'use_location_filter': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'lizard_workspace.layerfolder': {
            'Meta': {'object_name': 'LayerFolder'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layer_tab': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['lizard_workspace.Tag']", 'null': 'True', 'blank': 'True'}),
            'layers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['lizard_workspace.Layer']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children_set'", 'null': 'True', 'to': "orm['lizard_workspace.LayerFolder']"})
        },
        'lizard_workspace.layerworkspace': {
            'Meta': {'object_name': 'LayerWorkspace', '_ormbases': ['lizard_map.WorkspaceStorage']},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_workspace.Category']", 'null': 'True', 'blank': 'True'}),
            'data_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_security.DataSet']", 'null': 'True', 'blank': 'True'}),
            'layers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['lizard_workspace.Layer']", 'null': 'True', 'through': "orm['lizard_workspace.LayerWorkspaceItem']", 'blank': 'True'}),
            'owner_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'personal_category': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'workspacestorage_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['lizard_map.WorkspaceStorage']", 'unique': 'True', 'primary_key': 'True'})
        },
        'lizard_workspace.layerworkspaceitem': {
            'Meta': {'object_name': 'LayerWorkspaceItem'},
            'clickable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'filter_string': ('django.db.models.fields.CharField', [], {'max_length': '124', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'layer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_workspace.Layer']"}),
            'layer_workspace': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_workspace.LayerWorkspace']"}),
            'opacity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'lizard_workspace.synctask': {
            'Meta': {'object_name': 'SyncTask'},
            'data_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_security.DataSet']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_result': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'last_sync': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_workspace.WmsServer']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'lizard_workspace.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'lizard_workspace.thematicmap': {
            'Meta': {'object_name': 'ThematicMap'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'lizard_workspace.wmsserver': {
            'Meta': {'object_name': 'WmsServer'},
            'abstract': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['lizard_workspace']
