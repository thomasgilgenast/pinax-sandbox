import pytz

from django.http import Http404, HttpResponseForbidden
from django.core.mail import send_mail
from django.shortcuts import redirect, get_object_or_404
from django.utils.http import base36_to_int, int_to_base36
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.edit import FormView

from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.sites.models import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.signals import user_logged_in

from django.views.generic.create_update import update_object
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.edit import UpdateView, FormView
from django.contrib.auth.decorators import login_required

from account import signals
#from account.conf import settings
from account.mixins import LoginRequiredMixin
from account.models import SignupCode, EmailAddress, EmailConfirmation, Account, AccountDeletion
from account.utils import default_redirect, user_display

from account.views import SignupView as AccountSignupView
from account.views import LogoutView as AccountLogoutView
from account.views import ChangePasswordView as AccountChangePasswordView
from account.views import SettingsView as AccountSettingsView
from account.views import PasswordResetView as AccountPasswordResetView
from account.views import LoginView as AccountLoginView

from .forms import *

from .models import Profile, Broker, GenericBrokerInfo

from pinax.settings import ACCOUNT_CONTACT_EMAIL, ACCOUNT_LOGIN_REDIRECT_URL

### utility methods ###

def get_generic_broker_info(user, broker):
    # returns User user's GenericBrokerInfo for Broker broker if it exists and is configured
    # returns None otherwise
    user_broker = None
    try:
        user_broker = user.all_broker_info.get(broker__short_name=broker.short_name)
        if not user_broker.is_configured:
            user_broker = None
    except GenericBrokerInfo.DoesNotExist:
        pass
    return user_broker

### subclassed standard views ###

class SignupView(AccountSignupView):
    template_name_email_confirmation_sent = 'agent_account/email_confirmation_sent.html'
    
    # so I had to copy this entire method to slip in the context['account_contact_email']
    def form_valid(self, form):
        self.created_user = self.create_user(form, commit=False)
        if settings.ACCOUNT_EMAIL_CONFIRMATION_REQUIRED:
            self.created_user.is_active = False
        # prevent User post_save signal from creating an Account instance
        # we want to handle that ourself.
        self.created_user._disable_account_creation = True
        self.created_user.save()
        self.create_account(form)
        email_kwargs = {'primary': True, 'verified': False}
        if self.signup_code:
            self.signup_code.use(self.created_user)
            if self.signup_code.email and self.created_user.email == self.signup_code.email:
                email_kwargs['verified'] = True
                if settings.ACCOUNT_EMAIL_CONFIRMATION_REQUIRED:
                    self.created_user.is_active = True
                    self.created_user.save()
        email_address = EmailAddress.objects.add_email(self.created_user, self.created_user.email, **email_kwargs)
        self.after_signup(form)
        if settings.ACCOUNT_EMAIL_CONFIRMATION_EMAIL and not email_kwargs['verified']:
            email_address.send_confirmation()
        if settings.ACCOUNT_EMAIL_CONFIRMATION_REQUIRED and not email_kwargs['verified']:
            response_kwargs = {
                'request': self.request,
                'template': self.template_name_email_confirmation_sent,
                'context': {
                    'email': self.created_user.email,
                    'success_url': self.get_success_url(),
                    'account_contact_email': ACCOUNT_CONTACT_EMAIL,
                }
            }
            return self.response_class(**response_kwargs)
        else:
            show_message = [
                settings.ACCOUNT_EMAIL_CONFIRMATION_EMAIL,
                self.messages.get('email_confirmation_sent'),
                not email_kwargs['verified']
            ]
            if all(show_message):
                messages.add_message(
                    self.request,
                    self.messages['email_confirmation_sent']['level'],
                    self.messages['email_confirmation_sent']['text'] % {
                        'email': form.cleaned_data['email']
                    }
                )
            self.login_user()
        return redirect(self.get_success_url())

class LogoutView(AccountLogoutView):
    template_name = 'agent_account/logout.html'

class ChangePasswordView(AccountChangePasswordView):
    template_name = 'agent_account/change_password.html'

class PasswordResetView(AccountPasswordResetView):
    template_name = 'agent_account/password_reset.html'
    template_name_sent = 'agent_account/password_reset_sent.html'

    def get_context_data(self, **kwargs):
        context = super(PasswordResetView, self).get_context_data(**kwargs)
        context['account_contact_email'] = ACCOUNT_CONTACT_EMAIL
        return context

class LoginView(AccountLoginView):
    def after_login(self, form):
        user_logged_in.send(sender=LoginView, request=self.request, user=form.user, form=form)
		
### non-standard views ###

class SettingsView(UpdateView):
    form_class = SettingsForm
    template_name = 'agent_account/settings.html'
    context_object_name = 'account'
    success_url = reverse_lazy('account_settings')
    messages = {
        'settings_updated': {
            'level': messages.SUCCESS,
            'text': _('Your account settings were updated successfully.')
        },
    }

    def get_object(self, queryset=None):
        return Account.objects.get(user=self.request.user)

    def form_valid(self, form):
        # update the language
        self.request.session['django_language'] = form.cleaned_data['language']
		# update the timezone
        if form.cleaned_data['timezone'] != "":
            self.request.session['django_timezone'] = pytz.timezone(form.cleaned_data['timezone'])
        if self.messages.get('settings_updated'):
            messages.add_message(
                self.request,
                self.messages['settings_updated']['level'],
                self.messages['settings_updated']['text']
            )
        return super(SettingsView, self).form_valid(form)

class ProfileView(UpdateView):
    form_class = ProfileForm
    template_name = 'agent_account/profile.html'
    context_object_name = 'profile'
    success_url = reverse_lazy('account_profile')
    messages = {
        'profile_updated': {
            'level': messages.SUCCESS,
            'text': _('Your profile was updated successfully.')
        },
    }

    def get_object(self, queryset=None):
        # look for profiles bound to this user
        profile = Profile.objects.filter(user=self.request.user)
        if not profile:
            # no profiles found, make a new one
            profile = Profile(user=self.request.user)
            profile.save()
        else:
            # the field is onetoone so we just grab the first result
            profile = profile[0]
        return profile

    def form_valid(self, form):
        if self.messages.get('profile_updated'):
            messages.add_message(
                self.request,
                self.messages['profile_updated']['level'],
                self.messages['profile_updated']['text']
            )
        return super(ProfileView, self).form_valid(form)

class BrokersView(TemplateView):
    template_name = 'agent_account/brokers.html'
                
    def get_context_data(self, **kwargs):
        ctx = kwargs
        # the rows of the brokers table
        rows = []
        # fill in the list of rows
        for broker in Broker.objects.all():
            edit = False
            active = False
            # does the user have this broker set up?
            user_broker = get_generic_broker_info(self.request.user, broker)
            if user_broker:
                edit = True
                if user_broker.is_active:
                    active = True
            row = {
                'broker': broker,
                'edit': edit,
                'active': active,
            }
            rows.append(row)
        ctx.update({'rows': rows})
        return ctx
        
class BrokersAddView(UpdateView):
    # these lists must be in the same order as the Models table
    # I don't know if there's a way to make this programmatic
    # also note that the first entry corresponds to id 0 which is unused
    template_names = [
        '',
        'agent_account/add_nyt.html',
    ]
    form_classes = [
        None,
        AddNYTBrokerInfoForm,
    ]
    
    def get_object(self):
        # again, doing this manually sucks
        user_broker = None
        if self.kwargs['id'] == '1':
            user_broker = NYTBrokerInfo.objects.filter(generic_info__user=self.request.user)
            if user_broker:
                user_broker = user_broker[0]
            else:
                generic_info = GenericBrokerInfo(user=self.request.user, broker=Broker.objects.get(id=1))
                generic_info.save()
                user_broker = NYTBrokerInfo(generic_info=generic_info)
                user_broker.save()
            return user_broker
        else:
            return None
    
    def get_initial(self):
        initial = super(BrokersAddView, self).get_initial()
        if 'company_name' not in initial:
            initial['company_name'] = self.request.user.profile.company
        elif initial['company_name'] == '':
            initial['company_name'] = self.request.user.profile.company
        return initial
    
    def get_template_names(self):
        return self.template_names[int(self.kwargs['id'])]

    def get_form_class(self):
        return self.form_classes[int(self.kwargs['id'])]
        
    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx.update({'broker_id': self.kwargs['id']})
        return ctx
    
    def get_success_url(self):
        return reverse('account_brokers_add_next', kwargs={'id': self.kwargs['id']})

class BrokersAddNextView(TemplateView):
    template_names = [
        '',
        'agent_account/add_nyt_next.html',
    ]
    
    def get_template_names(self):
        return self.template_names[int(self.kwargs['id'])]

class BrokersEditView(UpdateView):
    template_names = [
        '',
        'agent_account/edit_nyt.html',
    ]
    form_classes = [
        None,
        EditNYTBrokerInfoForm,
    ]
    messages = {
        'broker_updated': {
            'level': messages.SUCCESS,
            'text': _('The broker information was updated successfully.')
        },
        'update_failed': {
            'level': messages.ERROR,
            'text': _('Updating the broker information failed.')
        },
    }
    
    def get_object(self):
        # again, doing this manually sucks
        user_broker = None
        if self.kwargs['id'] == '1':
            user_broker = NYTBrokerInfo.objects.filter(generic_info__user=self.request.user)
            if user_broker:
                user_broker = user_broker[0]
            else:
                if self.messages.get('update_failed'):
                    messages.add_message(
                        self.request,
                        self.messages['update_failed']['level'],
                        self.messages['update_failed']['text']
                    )
                redirect('account_brokers')
            return user_broker
        else:
            return None
    
    def get_template_names(self):
        return self.template_names[int(self.kwargs['id'])]

    def get_form_class(self):
        return self.form_classes[int(self.kwargs['id'])]
        
    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx.update({'broker_id': self.kwargs['id']})
        return ctx
        
    def form_valid(self, form):
        if self.messages.get('broker_updated'):
            messages.add_message(
                self.request,
                self.messages['broker_updated']['level'],
                self.messages['broker_updated']['text']
            )
        super(BrokersEditView, self).form_valid(form)
    
    def get_success_url(self):
        return reverse('account_brokers_edit', kwargs={'id': self.kwargs['id']})

class BrokersActivateView(RedirectView):
    permanent = False
    messages = {
        'broker_activated': {
            'level': messages.SUCCESS,
            'text': _('The broker was activated successfully.')
        },
        'activation_failed': {
            'level': messages.ERROR,
            'text': _('Activating the broker failed.')
        },
    }
    
    def get_redirect_url(self, id):
        infos = self.request.user.all_broker_info.filter(broker=Broker.objects.get(id=id))
        if infos:
            info = infos[0]
            info.is_active = True
            info.save()
            if self.messages.get('broker_activated'):
                messages.add_message(
                    self.request,
                    self.messages['broker_activated']['level'],
                    self.messages['broker_activated']['text']
                )
        else:
            if self.messages.get('activation_failed'):
                messages.add_message(
                    self.request,
                    self.messages['activation_failed']['level'],
                    self.messages['activation_failed']['text']
                )
        return reverse('account_brokers')
        
class BrokersDeactivateView(RedirectView):
    permanent = False
    messages = {
        'broker_deactivated': {
            'level': messages.SUCCESS,
            'text': _('The broker was activated successfully.')
        },
        'deactivation_failed': {
            'level': messages.ERROR,
            'text': _('Deactivating the broker failed.')
        },
    }
    
    def get_redirect_url(self, id):
        infos = self.request.user.all_broker_info.filter(broker=Broker.objects.get(id=id))
        if infos:
            info = infos[0]
            info.is_active = False
            info.save()
            if self.messages.get('broker_deactivated'):
                messages.add_message(
                    self.request,
                    self.messages['broker_deactivated']['level'],
                    self.messages['broker_deactivated']['text']
                )
        else:
            if self.messages.get('deactivation_failed'):
                messages.add_message(
                    self.request,
                    self.messages['deactivation_failed']['level'],
                    self.messages['deactivation_failed']['text']
                )
        return reverse('account_brokers')
        
class SendEmailNYTView(RedirectView):
    permanent = False
    messages = {
        'email_sent': {
            'level': messages.SUCCESS,
            'text': _('The email was sent successfully.')
        },
        'email_failed': {
            'level': messages.ERROR,
            'text': _('Sending the email failed.')
        },
    }
    
    def get_redirect_url(self):
        # TODO: create the test file
        # TODO: send the email
        if self.messages.get('email_sent'):
            messages.add_message(
                self.request,
                self.messages['email_sent']['level'],
                self.messages['email_sent']['text']
            )
        nyt_infos = self.request.user.all_broker_info.filter(broker=Broker.objects.get(short_name='nyt'))
        if nyt_infos:
            nyt_info = nyt_infos[0]
            nyt_info.is_configured = True
            nyt_info.save()
        else:
            pass
        return reverse('account_brokers')

# old BrokersView implemented as a FormView
"""class BrokersView(FormView):
    template_name = 'agent_account/brokers.html'
    form_class = BrokerForm
    
    def get_initial(self):
        initial = super(BrokersView, self).get_initial()
        for broker in Broker.objects.all():
            # does the user have this broker set up?
            user_broker = get_generic_broker_info(self.request.user, broker)
            if user_broker:
                initial[broker.short_name] = user_broker.is_active
            else:
                initial[broker.short_name] = False
        return initial
    
    def form_valid(self, form):
        for broker in Broker.objects.all():
            # did the user have this broker set up?
            user_broker = get_generic_broker_info(self.request.user, broker)
            if user_broker:
                # was the is_active flag toggled?
                if user_broker.is_active != form.cleaned_data[broker.short_name]:
                    user_broker.is_active = form.cleaned_data[broker.short_name]
                    user_broker.save()
        return redirect(self.get_success_url())
                
    def get_context_data(self, **kwargs):
        ctx = kwargs
        # the rows of the brokers table
        rows = []
        # fill in the list of rows
        for broker in Broker.objects.all():
            # does the user have this broker set up?
            user_broker = get_generic_broker_info(self.request.user, broker)
            button_text = 'Add'
            #button_url = reverse('account_brokers_add', broker.id)
            button_url = 'add/'
            if user_broker:
                # they do, set the button data appropriately
                button_text = 'Edit'
                #button_url = reverse('account_brokers_edit', broker.id)
                button_url = 'edit'
            row = {
                'broker_name': broker.name,
                'button_url': button_url,
                'button_text': button_text,
                'form_field': broker.short_name
            }
            rows.append(row)
        ctx.update({'rows': rows})
        return ctx
                
    def get_success_url(self, *args, **kwargs):
        return reverse('account_brokers')"""