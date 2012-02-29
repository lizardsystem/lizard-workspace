# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Category'
        db.create_table('lizard_workspace_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal('lizard_workspace', ['Category'])

        # Adding model 'Layer'
        db.create_table('lizard_workspace_layer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('wms', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_workspace.Category'], null=True, blank=True)),
            ('data_set', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_security.DataSet'], null=True, blank=True)),
        ))
        db.send_create_signal('lizard_workspace', ['Layer'])

        # Adding model 'Theme'
        db.create_table('lizard_workspace_theme', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal('lizard_workspace', ['Theme'])

        # Adding model 'LayerWorkspace'
        db.create_table('lizard_workspace_layerworkspace', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('theme', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_workspace.Theme'], null=True, blank=True)),
            ('data_set', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_security.DataSet'], null=True, blank=True)),
        ))
        db.send_create_signal('lizard_workspace', ['LayerWorkspace'])

        # Adding model 'LayerWorkspaceItem'
        db.create_table('lizard_workspace_layerworkspaceitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('layer_workspace', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_workspace.LayerWorkspace'])),
            ('layer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_workspace.Layer'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_workspace.Category'], null=True, blank=True)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('clickable', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('index', self.gf('django.db.models.fields.IntegerField')(default=100)),
        ))
        db.send_create_signal('lizard_workspace', ['LayerWorkspaceItem'])

        # Adding model 'UserLayerWorkspaceItem'
        db.create_table('lizard_workspace_userlayerworkspaceitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('layer_workspace', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_workspace.LayerWorkspace'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('wms', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('index', self.gf('django.db.models.fields.IntegerField')(default=100)),
        ))
        db.send_create_signal('lizard_workspace', ['UserLayerWorkspaceItem'])


    def backwards(self, orm):
        
        # Deleting model 'Category'
        db.delete_table('lizard_workspace_category')

        # Deleting model 'Layer'
        db.delete_table('lizard_workspace_layer')

        # Deleting model 'Theme'
        db.delete_table('lizard_workspace_theme')

        # Deleting model 'LayerWorkspace'
        db.delete_table('lizard_workspace_layerworkspace')

        # Deleting model 'LayerWorkspaceItem'
        db.delete_table('lizard_workspace_layerworkspaceitem')

        # Deleting model 'UserLayerWorkspaceItem'
        db.delete_table('lizard_workspace_userlayerworkspaceitem')


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
        'lizard_security.dataset': {
            'Meta': {'ordering': "['name']", 'object_name': 'DataSet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'})
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'wms': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'lizard_workspace.layerworkspace': {
            'Meta': {'object_name': 'LayerWorkspace'},
            'data_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_security.DataSet']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['lizard_workspace.Layer']", 'null': 'True', 'through': "orm['lizard_workspace.LayerWorkspaceItem']", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'theme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_workspace.Theme']", 'null': 'True', 'blank': 'True'})
        },
        'lizard_workspace.layerworkspaceitem': {
            'Meta': {'object_name': 'LayerWorkspaceItem'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_workspace.Category']", 'null': 'True', 'blank': 'True'}),
            'clickable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'layer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_workspace.Layer']"}),
            'layer_workspace': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_workspace.LayerWorkspace']"}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'lizard_workspace.theme': {
            'Meta': {'object_name': 'Theme'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'lizard_workspace.userlayerworkspaceitem': {
            'Meta': {'object_name': 'UserLayerWorkspaceItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'layer_workspace': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_workspace.LayerWorkspace']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'wms': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['lizard_workspace']
