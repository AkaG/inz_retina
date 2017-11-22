from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from gui import views

urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'logged_out.html', 'next_page': '/'}, name='logout'),
    url(r'^', views.IndexView.as_view()),
]