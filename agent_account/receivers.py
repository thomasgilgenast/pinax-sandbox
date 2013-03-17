import pytz

from django.dispatch import receiver

from django.contrib.auth.signals import user_logged_in

@receiver(user_logged_in)
def lang(sender, request, user, **kwargs):
    request.session["django_language"] = user.account.language

@receiver(user_logged_in)
def tz(sender, request, user, **kwargs):
    if user.account.timezone != '':
        self.request.session["django_timezone"] = pytz.timezone(user.account.timezone)