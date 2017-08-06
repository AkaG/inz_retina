from reports.models import Report
from keras.models import model_from_json
import json, tempfile

class ModelLoader():

    def load_model(self,id):
        self.id = id
        modelFile = Report.objects.get(id=id)
        json_string = json.load(modelFile.model)
        model = model_from_json(json.dumps(json_string))
        return model

    def load_weights(self,model,id=None):
        if id is None:
            id = self.id
        weightsFile = Report.objects.get(pk=id)
        model.load_weights(weightsFile.weights.name)
        return model
