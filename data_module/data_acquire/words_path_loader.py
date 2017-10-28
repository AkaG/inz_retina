import json
import logging
import os
import re

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from data_module.models import Examination, ProcessedDescription, Person, ImageSeries


class WordsPathLoader:
    def __init__(self, path):
        self.path = path
        self.logger = logging.getLogger('WordsPathLoader')
        self.stop_words = ['i', 'czy', 'do', 'od', 'za', 'oraz', 'przez', 'na', 'po', 'o']

    @transaction.atomic
    def load_words(self):
        for file in os.listdir(self.path):
            filename = os.path.join(self.path, file)
            file_path, extension = os.path.splitext(filename)
            if extension == '.json':
                self._load_word_entry(filename)

    def _load_word_entry(self, filename):
        with open(filename, encoding='UTF-8') as json_file:
            json_content = json.load(json_file)
            patient_hash = json_content['md5']
            examination_date = json_content['examination_date']
            try:
                patient = Person.objects.get(code_name=patient_hash)
                exam = Examination.objects.get(person=patient, date=examination_date)
            except ObjectDoesNotExist:
                self.logger.warning('Patient or examination not found for %s md5.' % patient_hash)
                exam = None
            self._save_description(exam, ImageSeries.LEFT, json_content['left_eye_words'], patient_hash)
            self._save_description(exam, ImageSeries.RIGHT, json_content['right_eye_words'], patient_hash)

    def _save_description(self, examination, eye, text, patient_hash):
        if text:
            desc = ProcessedDescription()
            desc.examination = examination
            desc.eye = eye
            desc.text = ' '.join([word for word in re.split(' +', text.strip()) if word not in self.stop_words])
            desc.save()
        else:
            self.logger.warning('No description found for %s md5 and %s eye.', eye, patient_hash)
