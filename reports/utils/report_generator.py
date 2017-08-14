import tempfile
import json

from django.conf import settings
from django.core.files import File
from keras.models import model_from_json

from reports.models import Report
from reports.utils.report_template import ReportTemplate


class ReportGenerator():
    def __init__(self, path, model, model_history, neural_network):
        self.directory = path
        self.model = model
        self.modelHistory = model_history
        self.neural_network = neural_network

    def generate_report(self):
        self._create_directory()
        report = Report()
        report.save()

        report.report = self._get_report_file(report.id)
        report.neural_network = self.neural_network
        report.save()

    def _get_report_file(self, report_id):
        with open(self.directory + '\\' + str(report_id) + '.pdf', 'wb+') as f:
            file = File(f)
            report_content = ReportTemplate(self.model, self.modelHistory, report_id).get_report_content()
            file.write(report_content)
            return file


class ReportGeneratorManager():
    def __init__(self, neural_network=None):
        self.neural_network = neural_network

    def create_report(self, model_history):
        with tempfile.TemporaryDirectory(dir=settings.MEDIA_ROOT) as tempdir:
            json_string = json.load(self.neural_network.model)
            model = model_from_json(json.dumps(json_string))

            report_gen = ReportGenerator(tempdir, model, model_history, self.neural_network)
            report_gen.generate_report()
