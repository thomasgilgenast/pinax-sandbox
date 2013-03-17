from django.contrib import admin

from .models import *

admin_models = [
    Profile,
    Broker,
    GenericBrokerInfo,
    NYTBrokerInfo,
]

admin.site.register(admin_models)
