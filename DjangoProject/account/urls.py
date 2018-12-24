from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^login/$', views.user_login, name='user_login'),
    url(r'^register/$', views.user_register, name='user_register'),
    url(r'^activate/(?P<token>\w+.[-_\w]*\w+.[-_\w]*\w+)/$', views.active_user, name='active_user'),
    url(r'^password_reset/$', auth_views.password_reset,
        {"template_name": "account/password_reset_form.html",
         "email_template_name": "account/password_reset_email.html",
         "subject_template_name": "account/password_reset_subject.txt",
         "post_reset_redirect": "/account/password_reset_done"},
        name="password_reset"),
    url(r'^password_reset_done/$', auth_views.password_reset_done,
        {"template_name": "account/password_reset_done.html"},
        name='password_reset_done'),
    url(r'^password_reset_confirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$',
        auth_views.password_reset_confirm,
        {"template_name": "account/password_reset_confirm.html",
         "post_reset_redirect": "/account/password_reset_complete"},
        name='password_reset_confirm'),
    url(r'^password_reset_complete/$', auth_views.password_reset_complete,
        {"template_name": "account/password_reset_complete.html"},
        name="password_reset_complete"),
    url(r'^logout/$', auth_views.logout, {"next_page": "/account/login", "template_name": "home.html"}, name='user_logout'),
    url(r'^myself_info/$', views.myself_info, name="myself_info"),
    url(r'^myself_tou/$', views.myself_tou, name="myself_tou"),
    url(r'^myself_mi/$', views.myself_mi, name="myself_mi"),
    url(r'^my_image/$', views.my_image, name="my_image"),
]
app_name = "account"
