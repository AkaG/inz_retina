from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, Preformatted
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
import matplotlib.pyplot as plt
import datetime, io, sys


class ReportTemplate():
    def __init__(self, model, modelHistory, reportId):
        self.model = model
        self.modelHistory = modelHistory
        self.reportId = reportId
        self.lineTemplate = "<font fontName='Helvetica-Bold'> %s </font> %s"
        self.story = []

    def get_report_content(self):
        self._init_styles()
        self._add_general_section()
        self._add_metrics_section()
        self._add_network_structure_section()

        stream = io.BytesIO()
        doc = SimpleDocTemplate(stream, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        doc.build(self.story)
        pdf_buffer = stream.getvalue()
        return pdf_buffer

    def _init_styles(self):
        self.styles = getSampleStyleSheet()
        self.style_center = ParagraphStyle(name='center', parent=self.styles['Normal'], alignment=TA_CENTER)
        self.style_header = ParagraphStyle(name='header', parent=self.styles['Heading1'], alignment=TA_CENTER, leading=50)
        self.style_section = ParagraphStyle(name='section', parent=self.styles['Heading1'], alignment=TA_LEFT, leading=20,
                                            fontSize=13, spaceBefore=30)

    def _add_general_section(self):
        self.story.append(Paragraph('Model report', self.style_header))
        self.story.append(Paragraph("1. General", self.style_section))
        dateParagraph = self.lineTemplate % ("Date: ", datetime.datetime.now().strftime("%Y-%m-%d  %H:%M"))
        idParagraph = self.lineTemplate % ("Id: ", self.reportId)
        self.story.append(Paragraph(dateParagraph, self.styles["Normal"]))
        self.story.append(Paragraph(idParagraph, self.styles["Normal"]))

    def _add_metrics_section(self):
        self.story.append(Paragraph("2. Metrics", self.style_section))
        history = self.modelHistory.history
        keys = history.keys()
        tbl = [];
        plots = [];
        labels = []
        imgSize = 250

        if 'acc' in keys and 'val_acc' in keys:
            plt.clf()
            plt.plot(history['acc'])
            plt.plot(history['val_acc'])
            plt.title('model accuracy')
            plt.ylabel('accuracy')
            plt.xlabel('epoch')
            plt.legend(['train', 'test'], loc='upper left')
            imgdata = io.BytesIO()
            plt.savefig(imgdata, format='png')
            plots.append(Image(imgdata, imgSize, imgSize))
            labels.append(Paragraph(self.lineTemplate % ("Final accuracy: ", history['val_acc'][-1]),self.style_center))

        if 'loss' in keys and 'val_loss' in keys:
            plt.clf()
            plt.plot(history['loss'])
            plt.plot(history['val_loss'])
            plt.title('model loss')
            plt.ylabel('loss')
            plt.xlabel('epoch')
            plt.legend(['train', 'test'], loc='upper left')
            imgdata = io.BytesIO()
            plt.savefig(imgdata, format='png')
            plots.append(Image(imgdata, imgSize, imgSize))
            labels.append(Paragraph(self.lineTemplate % ("Final loss: ", history['val_loss'][-1]),self.style_center))

        tbl.append(plots)
        tbl.append(labels)
        tbl = Table(tbl)
        self.story.append(tbl)

    def _add_network_structure_section(self):
        self.story.append(Paragraph("3. Network structure", self.style_section))
        model_summary = self._get_model_summary()
        self.story.append(Preformatted(model_summary.getvalue(), self.styles["Code"]))

    def _get_model_summary(self):
        origStdout = sys.stdout
        output = io.StringIO()
        sys.stdout = output
        self.model.summary()
        sys.stdout = origStdout
        output.seek(0)
        return output
