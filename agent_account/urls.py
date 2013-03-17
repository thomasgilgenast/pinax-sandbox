from django.conf.urls import patterns, url

from django.contrib.auth.decorators import login_required

from account.views import ConfirmEmailView, PasswordResetTokenView
#from account.views import DeleteView

from .views import *

urlpatterns = patterns("agent_account.views",
    # standard urls (imported from account)
    url(r"^password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$", PasswordResetTokenView.as_view(), name="account_password_reset_token"),
    url(r"^confirm_email/(?P<key>\w+)/$", ConfirmEmailView.as_view(), name="account_confirm_email"),

    # edited standard urls (these views are subclasses of the views in account.views)
    url(r"^signup/$", SignupView.as_view(), name="account_signup"),
    url(r"^logout/$", LogoutView.as_view(), name="account_logout"),
    url(r"^password/$", ChangePasswordView.as_view(), name="account_password"),
    url(r"^password/reset/$", PasswordResetView.as_view(), name="account_password_reset"),
    url(r"^login/$", LoginView.as_view(), name="account_login"),

    # deprecated standard urls (completely unused)
    #url(r"^delete/$", DeleteView.as_view(), name="account_delete"),

    # non-standard urls
    #url(r"^billing/$", TemplateView.as_view(template_name="agent_account/billing.html"), name="account_billing"),
    #url(r"^trial/$", TrialView.as_view(), name="account_trial"),
    url(r"^brokers/$", login_required(BrokersView.as_view()), name="account_brokers"),
    url(r"^brokers/add/(?P<id>\d+)/$", login_required(BrokersAddView.as_view()), name="account_brokers_add"),
    url(r"^brokers/add/(?P<id>\d+)/next/$", login_required(BrokersAddNextView.as_view()), name="account_brokers_add_next"),
    url(r"^brokers/send_email_nyt/$", login_required(SendEmailNYTView.as_view()), name="account_brokers_send_email_nyt"),
    url(r"^brokers/edit/(?P<id>\d+)/$", login_required(BrokersEditView.as_view()), name="account_brokers_edit"),
    url(r"^brokers/activate/(?P<id>\d+)/$", login_required(BrokersActivateView.as_view()), name="account_brokers_activate"),
    url(r"^brokers/deactivate/(?P<id>\d+)/$", login_required(BrokersDeactivateView.as_view()), name="account_brokers_deactivate"),
    url(r"^profile/$", login_required(ProfileView.as_view()), name="account_profile"),
    url(r"^settings/$", login_required(SettingsView.as_view()), name="account_settings"),
)
