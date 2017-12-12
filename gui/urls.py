from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from gui import views

urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'logged_out.html', 'next_page': '/'}, name='logout'),

    url(r'^patients/$', views.PatientList.as_view(), name='patient-list'),
    url(r'^patients/add/$', views.PatientAdd.as_view(), name='patient-add'),
    url(r'^patients/(?P<pk>[0-9]+)/edit/$', views.PatientUpdate.as_view(), name='patient-update'),
    url(r'^patients/(?P<pk>[0-9]+)/delete/$', views.PatientDelete.as_view(), name='patient-delete'),

    url(r'^examinations/$', views.ExaminationList.as_view(), name='examination-list'),
    url(r'^examinations/add$', views.ExaminationAdd.as_view(), name='examination-add'),
    url(r'^examinations/(?P<pk>[0-9]+)/$', views.ExaminationDetail.as_view(), name='examination-detail'),
    url(r'^examinations/(?P<pk>[0-9]+)/edit/$', views.ExaminationUpdate.as_view(), name='examination-update'),
    url(r'^examinations/(?P<pk>[0-9]+)/delete/$', views.ExaminationDelete.as_view(), name='examination-delete'),

    url(r'^examinations/(?P<pk>[0-9]+)/leftRightEyeNet/$', views.LeftRightEyeNet.as_view(), name='examination-left-right-eye'),
    url(r'^examinations/(?P<pk>[0-9]+)/sequenceDetectionNet/$', views.ExaminationUpdate.as_view(), name='examination-sequence-detection'),

    url(r'^examinations/(?P<pk>[0-9]+)/changeLeft/(?P<id>[0-9]+)/$', views.ImageChangeLeft.as_view(), name='examination-image-change-left'),
    url(r'^examinations/(?P<pk>[0-9]+)/changeRight/(?P<id>[0-9]+)/$', views.ImageChangeRight.as_view(), name='examination-image-change-right'),

    url(r'^$', views.IndexView.as_view()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
