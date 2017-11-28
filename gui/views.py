from django.shortcuts import render, redirect
from django.views.generic import View, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from integrations.left_right_eye_nn.LeftRightEyeQuery import LeftRightEyeQuerySingleton
from integrations.sequence_detection_nn.SequenceDetectionQuery import SequenceDetectionNNSingleton
from neural_network.nn_manager.DataGenerator import DataGenerator
from PIL import Image

from django_filters.views import FilterView
from django_filters import rest_framework as filters

from . import forms, models
from data_module import models as dataModels

class IndexView(LoginRequiredMixin, View):
    template_name = 'home.html'
    login_url = 'gui:login'
    
    response = ''

    def get(self, request):
        leftright = request.session.get('leftright')

        if type(leftright) is dict:
            leftright = list(leftright.values())[0]

        try:
            del request.session['leftright']
        except KeyError:
            pass

        return render(request, self.template_name, {'leftright': leftright})

    def post(self, request, *args, **kwargs):
        image = Image.open(request.FILES.get('image'))

        query = LeftRightEyeQuerySingleton.get_instance()
        datagen = DataGenerator(query.nn.input_shape)
        pred = query.model_predict(datagen.flow(
            [image, ], [request.FILES.get('image').name, ]), batch=1)

        request.session['leftright'] = pred

        return HttpResponseRedirect('/')


class PatientList(LoginRequiredMixin, FilterView):
    model = models.Patient
    template_name = 'patient_list.html'
    login_url = 'gui:login'
    filter_fields = ('first_name', 'last_name')


class PatientAdd(LoginRequiredMixin, CreateView):
    model = models.Patient
    form_class = forms.PatientForm
    template_name = 'patient_form.html'
    success_url = '/patients'


class ExaminationList(LoginRequiredMixin, ListView):
    model = dataModels.Examination
    template_name = 'examination_list.html'
    login_url = 'gui:login'


class ExaminationAdd(LoginRequiredMixin, CreateView):
    model = dataModels.Examination
    form_class = forms.ExaminationForm
    template_name = 'examination_form.html'
    success_url = '/examinations'
