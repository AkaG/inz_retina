from rest_framework import generics
from rest_framework.response import Response

from integrations.sequence_detection_nn.SequenceDetectionQuery import SequenceDetectionNNSingleton

class SequencePredictionViewSet(generics.GenericAPIView):
    def __init__(self):
        self.query = SequenceDetectionNNSingleton.get_instance()

    def post(self, request, *args, **kwargs):
        order, result = self.query.predict(request.data['id'])
        content = {'order': order, 'details': result}
        return Response(content)