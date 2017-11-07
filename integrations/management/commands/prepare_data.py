import os
from django.core.management import BaseCommand
from integrations.diagnosis_nn.dataPreparer import DataPreparer


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.main()

    def main(self):
        print("creating hdf5 file with data")
        data_preparer = DataPreparer()
        data_preparer.store_all_data_in_h5py_file()
