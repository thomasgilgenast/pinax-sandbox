from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .choices import *

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
        
        
def listing_picture_upload_to(instance, filename):
    return '/'.join(['images', instance.listing.id, filename])

class ListingPicture(models.Model):
    listing = models.ForeignKey(Listing)
    img = models.ImageField(upload_to=listing_picture_upload_to)
    
    def __unicode__(self):
        return self.listing.user.username + "'s picture: " + os.path.basename(self.file.name)
        
class Listing(models.Model):
    user = models.ForeignKey(User)
    # flags
    is_sold = models.BooleanField(default=False)
    push_nyt = models.BooleanField(default=False)
    # real fields
    listing_id = models.CharField(max_length=40, editable=False)
    street_number = models.CharField(_('street number'), max_length=10)
    street_name = models.CharField(_('street name'), max_length=39)
    apt_number = models.CharField(_('apartment/unit number'), max_length=50, blank=True)
    headline = models.CharField(_('headline'), max_length=99, blank=True)
    cross_street = models.CharField(_('cross street'), max_length=150, blank=True)
    city = models.CharField(_('city'), max_length=150)
    state = models.CharField(_('state/province'), max_length=2, choices=STATE_CHOICES)
    zip_code = models.CharField(_('zip/postal code'), max_length=6)
    country = models.CharField(_('country'), max_length=3, choices=COUNTRY_CHOICES, default='USA')
    price = models.DecimalField(_('price'), decimal_places=2, max_digits=15)
    monthly_maintenance = models.DecimalField(_('price'), decimal_places=2, max_digits=15)
    bedrooms = models.IntegerField(_('number of bedrooms'))
    
    
    def create(cls, request=None, **kwargs):