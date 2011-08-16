# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Plugin'
        db.create_table('spyglass_plugin', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('class_name', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('spyglass', ['Plugin'])

        # Deleting field 'HttpSession.autocorrected_localhost'
        db.delete_column('spyglass_httpsession', 'autocorrected_localhost')

        # Adding M2M table for field applied_plugins on 'HttpSession'
        db.create_table('spyglass_httpsession_applied_plugins', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('httpsession', models.ForeignKey(orm['spyglass.httpsession'], null=False)),
            ('plugin', models.ForeignKey(orm['spyglass.plugin'], null=False))
        ))
        db.create_unique('spyglass_httpsession_applied_plugins', ['httpsession_id', 'plugin_id'])


    def backwards(self, orm):
        
        # Deleting model 'Plugin'
        db.delete_table('spyglass_plugin')

        # Adding field 'HttpSession.autocorrected_localhost'
        db.add_column('spyglass_httpsession', 'autocorrected_localhost', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Removing M2M table for field applied_plugins on 'HttpSession'
        db.delete_table('spyglass_httpsession_applied_plugins')


    models = {
        'spyglass.httpredirect': {
            'Meta': {'object_name': 'HttpRedirect'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'redirect_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['spyglass.HttpSession']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'spyglass.httpsession': {
            'Meta': {'object_name': 'HttpSession'},
            'applied_plugins': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['spyglass.Plugin']", 'symmetrical': 'False'}),
            'celery_task_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64'}),
            'follow_redirects': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'http_body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'http_error': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'http_headers': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'http_method': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'http_response': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'http_url': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time_completed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'time_requested': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'spyglass.plugin': {
            'Meta': {'object_name': 'Plugin'},
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['spyglass']
