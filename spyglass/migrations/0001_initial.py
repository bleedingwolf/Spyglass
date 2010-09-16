# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'HttpSession'
        db.create_table('spyglass_httpsession', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('time_requested', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('time_completed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('http_method', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('http_url', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('http_headers', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('http_body', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('follow_redirects', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('http_error', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('http_response', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('celery_task_id', self.gf('django.db.models.fields.CharField')(default='', max_length=64)),
        ))
        db.send_create_signal('spyglass', ['HttpSession'])

        # Adding model 'HttpRedirect'
        db.create_table('spyglass_httpredirect', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['spyglass.HttpSession'])),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('spyglass', ['HttpRedirect'])


    def backwards(self, orm):
        
        # Deleting model 'HttpSession'
        db.delete_table('spyglass_httpsession')

        # Deleting model 'HttpRedirect'
        db.delete_table('spyglass_httpredirect')


    models = {
        'spyglass.httpredirect': {
            'Meta': {'object_name': 'HttpRedirect'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['spyglass.HttpSession']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'spyglass.httpsession': {
            'Meta': {'object_name': 'HttpSession'},
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
        }
    }

    complete_apps = ['spyglass']
