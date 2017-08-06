from reports.utils.report_template import  ReportTemplate
from reports.models import Report
from django.core.files import File
from django.conf import settings
import os, io, tempfile

class ReportGenerator():
    def __init__(self, modelHistory, model):
        self.directory = 'saved_reports'
        self.model = model
        self.modelHistory = modelHistory

    def generate_report(self):
        self._create_directory()
        id = self._get_next_report_id()
        reportFile = self._get_report_file(id)
        modelFile = self._get_model_file(id)
        weightsFile = self._get_weights_file(id)
        report = Report(report = reportFile, model=modelFile, weights=weightsFile)
        report.save()

        reportFile.close()
        modelFile.close()
        weightsFile.close()

    def _create_directory(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def _get_next_report_id(self):
        if(len(Report.objects.all()) > 0):
            nextId =  Report.objects.latest('id').id + 1
        else:
            nextId = 1
        return nextId

    def _get_report_file(self, reportId):
            f = open(self.directory+'/report'+str(reportId)+'.pdf','wb+')
            file = File(f)
            reportContent = ReportTemplate(self.model,self.modelHistory,reportId).get_report_content()
            file.write(reportContent)
            return file

    def _get_model_file(self,id):
        folderPath = settings.MEDIA_ROOT+'\\models\\'
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
        file = tempfile.NamedTemporaryFile(mode='w+',dir=folderPath, suffix='_id'+str(id), delete=True)
        file.write(self.model.to_json())
        return File(file)

    def _get_weights_file(self,id):
        folderPath = settings.MEDIA_ROOT+'\\weights\\'
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
        path = folderPath+'weight'+str(id)
        self.model.save_weights(path)
        return File(open(path,mode='rb'))