# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        for redirect in orm.HttpRedirect.objects.all():
            redirect.redirect_timestamp = redirect.timestamp
            redirect.save()

    def backwards(self, orm):
        for redirect in orm.HttpRedirect.objects.all():
            redirect.timestamp = redirect.redirect_timestamp
            redirect.save()


    models = {
        'spyglass.httpredirect': {
            'Meta': {'object_name': 'HttpRedirect'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'redirect_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
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
