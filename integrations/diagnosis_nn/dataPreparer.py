from text_processing.NGramCounter import NGramCounter
from text_processing.NGramVectorBuilder import NGramVectorBuilder
from data_module.models import Person, Examination, Description, ImageSeries
from data_module.models import Image as Retina_Image
from random import shuffle
import random, re, PIL, csv, cv2, os, time
import numpy as np
from skimage.transform import resize
np.random.seed(7)
import h5py




class DataPreparer():
    def __init__(self):
        self.nGramVbuild = self.get_ngram_vector_builder()
        self.load_image_resolution()

    def samples_from_file(self, f):
        reader = csv.reader(f.readline().split('\n'), delimiter=',')
        for row in reader:
            train_samples = np.array(row[:-1],dtype='uint8')
            break

        reader = csv.reader(f.readline().split('\n'), delimiter=',')
        for row in reader:
            val_samples = np.array(row[:-1],dtype='uint8')
            break

        reader = csv.reader(f.readline().split('\n'), delimiter=',')
        for row in reader:
            test_samples = np.array(row[:-1],dtype='uint8')
            break
        f.close()
        return train_samples,val_samples,test_samples

    def get_ngram_vector_builder(self):
        n = 2; self.outputs = 500; skip = 100; limit = 0
        ngc = NGramCounter()
        self.n_gram = ngc.get_k_skip_n_gram_histogram(n,skip,limit,self.outputs)
        return NGramVectorBuilder(self.n_gram)

    def load_image_resolution(self):
        width = 1388
        height = 1038

        self.img_size_2 = 100
        self.img_size_1 = int(self.img_size_2 * (height / width))

    def get_images_metadata(self,examinations):
        metadata = []
        for exam_id in examinations:
            sequences = ImageSeries.objects.filter(examination_id=exam_id)
            for i in range(len(sequences)):
                if sequences[i].name.endswith("after_registration") or sequences[i].name.startswith("d") :
                    continue
                if sequences[i].name.startswith("left"):
                    side = 'L'
                else:
                    side = 'R'
                imgModels = Retina_Image.objects.filter(image_series=sequences[i])
                imgNum = len(imgModels)
                if imgNum == 0:
                    continue
                metadata.append({'examination_id':exam_id, 'side': side, 'series': sequences[i].id, 'first': imgModels[0].id, 'middle': imgModels[int(imgNum/2)].id,'last': imgModels[imgNum-1].id})
            shuffle(metadata)
        return metadata

    def prepare_image(self,_id):
        img = Retina_Image.objects.get(id=_id)
        img = PIL.Image.open(img.image).convert('L')
        arr_img = np.array(img)
        arr_img = self.preprocess_image(arr_img, self.img_size_1, self.img_size_2)
        return arr_img

    def to_float(self,image):
        func = np.vectorize(lambda x: x / 255.0)
        return func(image)

    def standardization(self,image):
        return (image - np.mean(image)) / np.std(image)

    def preprocess_image(self,image, size_1, size_2, channel=0):
        image = resize(image, (self.img_size_1, self.img_size_2, 1))
        image = self.to_float(image)
        image = self.standardization(image)

        return image

    def create_dataset_and_store(self,hdf5_file, name, metadata):
        x_name = name+'_x'
        x_shape = (len(metadata), self.img_size_1, self.img_size_2, 3)
        hdf5_file.create_dataset(x_name, x_shape, np.float32)

        y_name = name+'_y'
        y_shape = (len(metadata),self.outputs)
        hdf5_file.create_dataset(y_name, y_shape, np.int8)

        meta_name = name+'_metadata'
        meta_shape = (len(metadata),)
        hdf5_file.create_group(meta_name)

        for i in range(len(metadata)):
            meta_elem = metadata[i]

            #save X data
            img1 = self.prepare_image(meta_elem['first'])
            img2 = self.prepare_image(meta_elem['middle'])
            img3 = self.prepare_image(meta_elem['last'])

            x = np.dstack((img1,img2,img3))
            hdf5_file[x_name][i, ...] = x[None]

            #save Y data
            words_vector = self.nGramVbuild.get_vector(meta_elem['examination_id'], meta_elem['side'])
            hdf5_file[y_name][i, ...] = words_vector

            #save metadata
            gr = hdf5_file.create_group(meta_name+'/'+str(i))
            for k, v in meta_elem.items():
                gr[k] = v




    def store_all_data_in_h5py_file(self):

        f = open('splited_data.txt')
        train_samples, val_samples, test_samples = self.samples_from_file(f)

        train_metadata = self.get_images_metadata(train_samples)
        val_metadata = self.get_images_metadata(val_samples)
        test_metadata = self.get_images_metadata(test_samples)

        hdf5_path = './prepared_data.hdf5'
        hdf5_file = h5py.File(hdf5_path, mode='w')

        self.create_dataset_and_store(hdf5_file,'train_data',train_metadata)
        self.create_dataset_and_store(hdf5_file,'val_data',val_metadata)
        self.create_dataset_and_store(hdf5_file,'test_data',test_metadata)

        words = []
        for k, v in self.n_gram.items():
            words.append(k)
        hdf5_file.attrs.create('n_gram', words, dtype=h5py.special_dtype(vlen=str))

        hdf5_file.close()
