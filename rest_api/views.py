from PIL import Image
from braces.views import CsrfExemptMixin
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.generic.edit import FormView

from integrations.left_right_eye_nn.LeftRightEyeQuery import LeftRightEyeQuerySingleton
from integrations.sequence_detection_nn.SequenceDetectionQuery import SequenceDetectionNNSingleton
from neural_network.nn_manager.DataGenerator import DataGenerator
from .models import FileUpload
from .serializers import FileUploadSerializer
from .forms import UploadForm


class FileUploadActionsViewSet(generics.GenericAPIView, CsrfExemptMixin):
    queryset = FileUpload.objects.all()
    serializer_class = FileUploadSerializer
    permission_classes = (AllowAny,)
    authentication_classes = []

    def __init__(self):
        self.query = LeftRightEyeQuerySingleton.get_instance()

    def post(self, request, *args, **kwargs):
        imglist = request.data.getlist('image')
        if len(imglist) == 0:
            return Response({})

        images = [Image.open(img) for img in imglist]
        names = [img.name for img in imglist]
        datagen = DataGenerator(self.query.input_shape)
        pred = self.query.model_predict(datagen.flow(images, names), batch=len(images))
        return Response(pred)


class UploadView(FormView):
    template_name = 'sequencedetection.html'
    form_class = UploadForm

    def __init__(self):
        self.query = SequenceDetectionNNSingleton.get_instance()

    def form_valid(self, form):
        order, result_struct = self.query.predict(form.cleaned_data['attachments'])
        return self.render_to_response(self.get_context_data(order = order, result_struct = result_struct))