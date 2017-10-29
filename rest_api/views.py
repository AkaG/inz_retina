from PIL import Image
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from integrations.left_right_eye_nn.LeftRightEyeQuery import LeftRightEyeQuerySingleton
from neural_network.nn_manager.DataGenerator import DataGenerator
from .models import FileUpload
from .serializers import FileUploadSerializer


class FileUploadActionsViewSet(generics.GenericAPIView):
    queryset = FileUpload.objects.all()
    serializer_class = FileUploadSerializer
    permission_classes = (AllowAny,)

    def __init__(self):
        self.query = LeftRightEyeQuerySingleton.get_instance()

    def post(self, request, *args, **kwargs):
        image = Image.open(request.data['image'])
        datagen = DataGenerator(self.query.nn.input_shape)
        pred = self.query.model_predict(datagen.flow([image, ], [request.data['image'].name, ]), batch=1)
        return Response(pred)
