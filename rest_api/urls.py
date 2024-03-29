from django.conf.urls import url, include
from rest_framework import routers

from rest_api import views

router = routers.DefaultRouter()

urlpatterns = [
    url(r'left-right-eye', views.FileUploadActionsViewSet.as_view()),
    url(r'^sequence-detection/$', views.UploadView.as_view()),
    url(r'^sequence-detection-rest/$', views.SequenceDetectionRest.as_view()),
    url(r'^', include(router.urls)),
]
