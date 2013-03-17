# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Profile'
        db.create_table('agent_account_profile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='profile', unique=True, to=orm['auth.User'])),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('picture', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('company', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('license_number', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal('agent_account', ['Profile'])

        # Adding model 'Broker'
        db.create_table('agent_account_broker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('short_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
        ))
        db.send_create_signal('agent_account', ['Broker'])

        # Adding model 'GenericBrokerInfo'
        db.create_table('agent_account_genericbrokerinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='all_broker_info', to=orm['auth.User'])),
            ('broker', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['agent_account.Broker'])),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_configured', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('agent_account', ['GenericBrokerInfo'])

        # Adding model 'NYTBrokerInfo'
        db.create_table('agent_account_nytbrokerinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('csa_email', self.gf('django.db.models.fields.EmailField')(max_length=254, blank=True)),
            ('company_name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('company_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('generic_info', self.gf('django.db.models.fields.related.OneToOneField')(related_name='nyt_broker_info', unique=True, to=orm['agent_account.GenericBrokerInfo'])),
            ('ftp_login', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('ftp_password', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal('agent_account', ['NYTBrokerInfo'])


    def backwards(self, orm):
        # Deleting model 'Profile'
        db.delete_table('agent_account_profile')

        # Deleting model 'Broker'
        db.delete_table('agent_account_broker')

        # Deleting model 'GenericBrokerInfo'
        db.delete_table('agent_account_genericbrokerinfo')

        # Deleting model 'NYTBrokerInfo'
        db.delete_table('agent_account_nytbrokerinfo')


    models = {
        'agent_account.broker': {
            'Meta': {'object_name': 'Broker'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'short_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'})
        },
        'agent_account.genericbrokerinfo': {
            'Meta': {'object_name': 'GenericBrokerInfo'},
            'broker': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['agent_account.Broker']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_configured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'all_broker_info'", 'to': "orm['auth.User']"})
        },
        'agent_account.nytbrokerinfo': {
            'Meta': {'object_name': 'NYTBrokerInfo'},
            'company_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'csa_email': ('django.db.models.fields.EmailField', [], {'max_length': '254', 'blank': 'True'}),
            'ftp_login': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ftp_password': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'generic_info': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'nyt_broker_info'", 'unique': 'True', 'to': "orm['agent_account.GenericBrokerInfo']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'agent_account.profile': {
            'Meta': {'object_name': 'Profile'},
            'company': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'license_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'profile'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
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
        }
    }

    complete_apps = ['agent_account']