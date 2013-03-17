from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

def profile_picture_upload_to(instance, filename):
    return '/'.join(['profilepics', str(instance.id), filename])

class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', verbose_name=_('user'))
    first_name = models.CharField(_('first name'), max_length=50, blank=True)
    last_name = models.CharField(_('last name'), max_length=50, blank=True)
    picture = models.FileField(_('profile picture'), upload_to=profile_picture_upload_to, blank=True, null=True)
    company = models.CharField(_('company'), max_length=50, blank=True)
    license_number = models.CharField(_('license number'), max_length=50, blank=True)
    
    def __unicode__(self):
        return self.user.username
    
class Broker(models.Model):
    name = models.CharField(_('broker name'), max_length=50)
    short_name = models.CharField(_('broker short name'), max_length=10, unique=True)
    
    def __unicode__(self):
        return self.name
    
class GenericBrokerInfo(models.Model):
    user = models.ForeignKey(User, related_name='all_broker_info', verbose_name=_('user')) 
    broker = models.ForeignKey(Broker, related_name='+', verbose_name=_('broker'))
    is_active = models.BooleanField(_('Is active?'), default=False)
    is_configured = models.BooleanField(_('Is configured?'), default=False)
    
    def __unicode__(self):
        return self.user.username + "'s info for " + self.broker.name
    
class NYTBrokerInfo(models.Model):
    csa_email = models.EmailField(_('CSA email'), max_length=254, blank=True)
    company_name = models.CharField(_('company name'), max_length=50, blank=True)
    company_id = models.IntegerField(_('company ID'), blank=True, null=True)
    generic_info = models.OneToOneField(GenericBrokerInfo, related_name='nyt_broker_info', verbose_name=_('generic info'))
    ftp_login = models.CharField(_('FTP login'), max_length=50, blank=True)
    ftp_password = models.CharField(_('FTP password'), max_length=50, blank=True)
    
    def __unicode__(self):
        return self.generic_info.user.username + "'s NYTBrokerInfo"