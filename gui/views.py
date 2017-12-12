from django.shortcuts import render, redirect
from django.views.generic import View, ListView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from integrations.left_right_eye_nn.LeftRightEyeQuery import LeftRightEyeQuery
from integrations.sequence_detection_nn.SequenceDetectionQuery import SequenceDetectionQuery
from neural_network.nn_manager.DataGenerator import DataGenerator
from PIL import Image

from django_filters.views import FilterView
from django_filters import rest_framework as filters

from . import forms
from data_module import models

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

        query = LeftRightEyeQuery()
        datagen = DataGenerator(query.input_shape)
        pred = query.model_predict(datagen.flow(
            [image, ], [request.FILES.get('image').name, ]), batch=1)

        request.session['leftright'] = pred

        return HttpResponseRedirect('/')


class PatientList(LoginRequiredMixin, FilterView):
    model = models.Person
    template_name = 'patient_list.html'
    login_url = 'gui:login'
    filter_fields = ('first_name', 'last_name')


class PatientAdd(LoginRequiredMixin, CreateView):
    model = models.Person
    form_class = forms.PatientForm
    template_name = 'patient_form.html'
    success_url = '/patients'
    login_url = 'gui:login'


class PatientUpdate(LoginRequiredMixin, UpdateView):
    model = models.Person
    form_class = forms.PatientForm
    template_name = 'patient_form.html'
    success_url = '/patients'
    login_url = 'gui:login'


class PatientDelete(LoginRequiredMixin, DeleteView):
    model = models.Person
    template_name = 'patient_confirm_delete.html'
    success_url = '/patients'  
    login_url = 'gui:login'


class ExaminationList(LoginRequiredMixin, FilterView):
    model = models.Examination
    template_name = 'examination_list.html'
    login_url = 'gui:login'
    filter_fields = ('person',)
    
    def get_queryset(self):
        queryset = models.Examination.objects.all()

        for examination in queryset:
            description = models.Description.objects.filter(examination=examination)
            if len(description) > 0:
                examination.description = description[0]
            else:
                examination.description = None

        return queryset


class ExaminationAdd(LoginRequiredMixin, FormView):
    model = models.Examination
    form_class = forms.ExaminationCombinedForm
    template_name = 'examination_form.html'
    success_url = '/examinations'

    def form_valid(self, form):
        examination = models.Examination.objects.create(
            person=form.cleaned_data['person'],
            date=form.cleaned_data['date']
        )
        models.Description.objects.create(
            text=form.cleaned_data['text'],
            examination=examination
        )
        models.ImageSeries.objects.create(eye='L', examination=examination)
        models.ImageSeries.objects.create(eye='R', examination=examination)
        image_series = models.ImageSeries.objects.create(name='unknown', examination=examination)
        images = form.cleaned_data['attachments']
        for image in images:
            imageObject = models.Image.objects.create(name=image.name, image_series=image_series)
            imageObject.image.save(image.name, image)

        return super(ExaminationAdd, self).form_valid(form)


class ExaminationUpdate(LoginRequiredMixin, FormView):
    # TODO
    model = models.Examination
    form_class = forms.ExaminationCombinedForm
    template_name = 'examination_form.html'
    success_url = '/examinations'
    login_url = 'gui:login'


class ExaminationDelete(LoginRequiredMixin, DeleteView):
    model = models.Examination
    template_name = 'examination_confirm_delete.html'
    success_url = '/examinations'
    login_url = 'gui:login'


class ExaminationDetail(LoginRequiredMixin, View):
    template_name = 'examination_detail.html'
    login_url = 'gui:login'

    def get(self, request, pk):
        examination = models.Examination.objects.filter(id=pk)[0]
        description = models.Description.objects.filter(examination=examination)[0]

        image_series_unknown = models.ImageSeries.objects.filter(name='unknown', examination=examination)
        image_series_left = models.ImageSeries.objects.filter(eye='L', examination=examination)
        image_series_right = models.ImageSeries.objects.filter(eye='R', examination=examination)
        images_unknown = models.Image.objects.filter(image_series=image_series_unknown).order_by('order')
        images_left = models.Image.objects.filter(image_series=image_series_left).order_by('order')
        images_right = models.Image.objects.filter(image_series=image_series_right).order_by('order')

        return render(request, self.template_name, {
            'examination': examination,
            'description': description.text,
            'images_unknown': images_unknown,
            'images_left': images_left,
            'images_right': images_right
        })


class LeftRightEyeNet(LoginRequiredMixin, View):
    login_url = 'gui:login'

    def get(self, request, pk):
        query = LeftRightEyeQuery()
        datagen = DataGenerator(query.input_shape)
        examination = models.Examination.objects.filter(id=pk)[0]

        image_series_all = models.ImageSeries.objects.filter(examination=examination)
        image_series_unknown = models.ImageSeries.objects.filter(name='unknown', examination=examination)
        image_series_left = models.ImageSeries.objects.filter(eye='L', examination=examination)
        image_series_right = models.ImageSeries.objects.filter(eye='R', examination=examination)

        images_all = models.Image.objects.filter(image_series=image_series_unknown) | models.Image.objects.filter(
            image_series=image_series_right) | models.Image.objects.filter(image_series=image_series_left)
        images = [Image.open(image.image) for image in images_all]
        names = [image.name for image in images_all]

        pred = query.model_predict(datagen.flow(
            images, names), batch=len(images_all)
        )

        if len(image_series_unknown) == 0:
            image_series_unknown = models.ImageSeries.objects.create(name='unknown', examination=examination)
        else:
            image_series_unknown = image_series_unknown[0]

        if len(image_series_left) == 0:
            image_series_left = models.ImageSeries.objects.create(eye='L', examination=examination)
        else:
            image_series_left = image_series_left[0]

        if len(image_series_right) == 0:
            image_series_right = models.ImageSeries.objects.create(eye='R', examination=examination)
        else:
            image_series_right = image_series_right[0]

        for image in images_all:
            prediction = pred[image.name]['prediction']
            if prediction == 'L':
                image.image_series = image_series_left
            if prediction == 'R':
                image.image_series = image_series_right
            if prediction == 'N':
                image.image_series = image_series_unknown

            image.save()

        return redirect('gui:examination-detail', pk=examination.id)


class ImageChangeLeft(LoginRequiredMixin, View):
    login_url = 'gui:login'

    def get(self, request, pk, id):
        examination = models.Examination.objects.filter(id=pk)[0]
        image = models.Image.objects.filter(id=id)[0]
        image_series_left = models.ImageSeries.objects.filter(eye='L', examination=examination)

        if len(image_series_left) == 0:
            image_series_left = models.ImageSeries.objects.create(eye='L', examination=examination)
        else:
            image_series_left = image_series_left[0]

        image.image_series = image_series_left
        image.save()

        return redirect('gui:examination-detail', pk=examination.id)


class ImageChangeRight(LoginRequiredMixin, View):
    login_url = 'gui:login'

    def get(self, request, pk, id):
        examination = models.Examination.objects.filter(id=pk)[0]
        image = models.Image.objects.filter(id=id)[0]
        image_series_right = models.ImageSeries.objects.filter(
            eye='R', examination=examination)

        if len(image_series_right) == 0:
            image_series_right = models.ImageSeries.objects.create(
                eye='R', examination=examination)
        else:
            image_series_right = image_series_right[0]

        image.image_series = image_series_right
        image.save()

        return redirect('gui:examination-detail', pk=examination.id)


class SequenceDetectionNet(LoginRequiredMixin, View):
    login_url = 'gui:login'

    def get(self, request, pk):
        query = SequenceDetectionQuery()
        examination = models.Examination.objects.filter(id=pk)[0]

        image_series_right = models.ImageSeries.objects.filter(eye='R', examination=examination)
        images_right = models.Image.objects.filter(image_series=image_series_right)
        images = [image.image for image in images_right]
        result, differences = query.predict(images)
        result_keys = result.keys()
        for image in images_right:
            pos = list(result_keys).index(image.image.name)
            image.order = pos + 1
            image.save()

        image_series_left = models.ImageSeries.objects.filter(eye='L', examination=examination)
        images_left = models.Image.objects.filter(image_series=image_series_left)
        images = [image.image for image in images_left]
        result, differences = query.predict(images)
        result_keys = result.keys()
        for image in images_left:
            pos = list(result_keys).index(image.image.name)
            image.order = pos + 1
            image.save()


        return redirect('gui:examination-detail', pk=examination.id)
