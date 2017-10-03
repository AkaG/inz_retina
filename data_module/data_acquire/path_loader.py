import logging
import os
from datetime import datetime
from os.path import join

from django.core.files import File

from data_module.models import Person, Examination, Description, ImageSeries, Image


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
            patient = Person(code_name=dir_name)
            patient.save()

        for (dirpath, dirnames, filenames) in os.walk(join(self.path, dir_name)):
            for exam in dirnames:
                self._add_exam_to_patient(patient, dirpath, exam)
            break

    def _add_exam_to_patient(self, patient, path, exam_date):
        date = datetime.strptime(exam_date, "%Y-%m-%d").date()
        try:
            exam = Examination.objects.get(date=date, person=patient)
        except Exception:
            self.logger.info("Create examination for patient {} with date {}".format(patient.code_name, exam_date))
            exam = Examination(date=date, person=patient)
            exam.save()

        exam_path = join(path, exam_date)
        self._add_current_age(exam, exam_path)
        self._add_icd_code(exam, exam_path)
        self._add_json(exam, exam_path)

        self._add_sex_to_person(patient, exam_path)

        self._load_descriptions(exam, exam_path)
        exam.save()

        for (dirpath, dirnames, filenames) in os.walk(exam_path):
            for image_series in dirnames:
                self._add_image_series_to_exam(exam, dirpath, image_series)
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

    def _add_json(self, exam, exam_path):
        try:
            with open(join(exam_path, "OKO_LP.js")) as file:
                exam.json = file.read()
        except Exception as e:
            self.logger.error("Error during _add_json: {}".format(str(e)))

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
                    self._add_description_to_exam(exam, dirpath, file_name)
            break

    def _add_description_to_exam(self, exam, path, file_name):
        try:
            with open(join(path, file_name), encoding='utf-8') as file:
                try:
                    description = Description.objects.get(name=file_name, examination=exam)
                except Exception as e:
                    self.logger.info("Create description {}".format(file_name))
                    description = Description(name=file_name, examination=exam)

                description.text = file.read()
                description.save()
        except Exception as e:
            self.logger.error("Error during _add_description_to_exam: {}".format(str(e)))

    def _add_image_series_to_exam(self, exam, dirpath, image_series_name):
        try:
            im_series = ImageSeries.objects.get(name=image_series_name, examination=exam)
        except Exception as e:
            self.logger.info("Create Image_Series {} for exam {}".format(image_series_name, exam.date))
            im_series = ImageSeries(name=image_series_name, examination=exam,
                                    eye=ImageSeries.LEFT if ("left" in image_series_name.lower()) else ImageSeries.RIGHT)
            im_series.save()

        self._add_images_to_imageSeries(im_series, join(dirpath, image_series_name))

    def _add_images_to_imageSeries(self, im_series, dirpath):
        for img_name in os.listdir(dirpath):
            if img_name.startswith("."):
                continue
            try:
                img_entry = Image.objects.get(name=img_name, image_series=im_series)
            except Exception as e:
                self.logger.info("Create Image {} for series {}".format(img_name, im_series.name))
                img_entry = Image(name=img_name, image_series=im_series)
                img_entry.image.save(img_name, File(open(join(dirpath, img_name), "rb")))
                img_entry.save()
