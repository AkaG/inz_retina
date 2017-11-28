from PIL import Image
from braces.views import CsrfExemptMixin
from django.views.generic.edit import FormView
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from integrations.left_right_eye_nn.LeftRightEyeQuery import LeftRightEyeQuery
from integrations.sequence_detection_nn.SequenceDetectionQuery import SequenceDetectionQuery
from neural_network.nn_manager.DataGenerator import DataGenerator
from .forms import UploadForm
from .models import FileUpload
from .serializers import FileUploadSerializer


class FileUploadActionsViewSet(generics.GenericAPIView, CsrfExemptMixin):
    queryset = FileUpload.objects.all()
    serializer_class = FileUploadSerializer
    permission_classes = (AllowAny,)
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        query = LeftRightEyeQuery()
        imglist = request.data.getlist('image')
        if len(imglist) == 0:
            return Response({})

        images = [Image.open(img) for img in imglist]
        names = [img.name for img in imglist]
        datagen = DataGenerator(query.input_shape)
        pred = query.model_predict(datagen.flow(images, names), batch=len(images))
        return Response(pred)


class UploadView(FormView):
    template_name = 'sequencedetection.html'
    form_class = UploadForm

    def form_valid(self, form):
        query = SequenceDetectionQuery()
        order, result_struct = query.predict(form.cleaned_data['attachments'])
        return self.render_to_response(self.get_context_data(order=order, result_struct=result_struct))
