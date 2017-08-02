import logging
import os
from datetime import datetime
from os.path import join

from data_module.models import Person, Examination


class PathLoader():
    def __init__(self, path):
        self.path = path
        self.logger = logging.getLogger('PathLoader')
        self.logging_level = logging.DEBUG
        self._setupLogger()

    def _setupLogger(self):
        self.logger.setLevel(self.logging_level)
        ch = logging.StreamHandler()
        ch.setLevel(self.logging_level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        self.logger.addHandler(ch)

    def load_data(self):
        for dir in os.listdir(self.path):
            self._load_patient_entry(dir)

    def _load_patient_entry(self, dir_name):
        self.logger.info("Check directory {}".format(dir_name))
        try:
            patient = Person.objects.get(code_name=dir_name)
        except Exception:
            self.logger.info("Create person {}".format(dir_name))
            patient = Person()
            patient.code_name = dir_name
            patient.save()

        for (dirpath, dirnames, filenames) in os.walk(join(self.path, dir_name)):
            for exam in dirnames:
                self._add_exam_to_patient(patient, dirpath, exam)
            break

    def _add_exam_to_patient(self, patient, path, exam_date):
        date = datetime.strptime(exam_date, "%Y-%m-%d").date()
        try:
            exam = Examination.objects.get(date=date)
        except Exception:
            self.logger.info("Create examination for patient {} with date {}".format(patient.code_name, exam_date))
            exam = Examination()
            exam.date = date
            exam.person = patient

        exam_path = join(path, exam_date)
        self._add_current_age(exam, exam_path)
        self._add_icd_code(exam, exam_path)

        self._add_sex_to_person(patient, exam_path)

        self._load_descriptions(exam, exam_path)
        exam.save()

        for (dirpath, dirnames, filenames) in os.walk(exam_date):
            for image_series in dirnames:
                self._add_imageSeries_to_exam(exam, dirpath, image_series)
            break

    def _add_current_age(self, exam, exam_path):
        try:
            with open(join(exam_path, "age.txt")) as file:
                exam.current_age = float(file.read())
        except Exception as e:
            self.logger.error("Error during _add_current_age: {}".format(str(e)))

    def _add_icd_code(self, exam, exam_path):
        try:
            with open(join(exam_path, "correct_icd_code.txt")) as file:
                exam.icd_code = file.read()
        except Exception as e:
            self.logger.error("Error during _add_icd_code: {}".format(str(e)))

    def _add_sex_to_person(self, person, exam_path):
        try:
            with open(join(exam_path, "sex.txt")) as file:
                person.sex = file.read()
                person.save()
        except Exception as e:
            self.logger.error("Error during _add_sex_to_person: {}".format(str(e)))

    def _load_descriptions(self, exam, exam_path):
        for (dirpath, dirnames, filenames) in os.walk(exam_path):
            for file_name in filenames:
                if "description" in file_name:
                    self._add_descriprion_to_exam(exam, dirpath, file_name)
            break

    def _add_descriprion_to_exam(self, exam, path, file_name):
        try:
            with open(join(path, file_name)) as file:
                pass
        except Exception as e:
            self.logger.error("Error during _add_descriprion_to_exam: {}".format(str(e)))


    def _add_imageSeries_to_exam(self, exam, dirpath, image_series_name):
        pass


