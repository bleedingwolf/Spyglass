# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'HttpSession.autocorrected_localhost'
        db.add_column('spyglass_httpsession', 'autocorrected_localhost', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'HttpSession.autocorrected_localhost'
        db.delete_column('spyglass_httpsession', 'autocorrected_localhost')


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
            'autocorrected_localhost': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
