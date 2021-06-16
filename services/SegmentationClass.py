# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 15:57:04 2020

@author: daewo
"""
import sys
import gc
import random
import numpy as np
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow.keras.models import model_from_json

import vtk
from vtk.util.numpy_support import vtk_to_numpy
from vtk.util.numpy_support import numpy_to_vtk

import cv2

from skimage.morphology import disk
from skimage.morphology import binary_closing as closing
from skimage.morphology import binary_opening as opening
from skimage.measure import label
import scipy

class Segmentation:
    
    def __init__(self,dims=(512,512),n_channels=3):
        
        self.model = None
        self.dims = dims
        self.n_channels = n_channels
        self.prob_images = []
        self.class_images = []
        
        return
    
    def loadModel(self,filename):
        
        # load json and create model
        json_file = open(filename, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.model = model_from_json(loaded_model_json)

        return
    
    def loadWeights(self,filename):
        
        self.model.load_weights(filename)
        
        return
    
    def segmentVolume(self,volume,masks=None,visualize=True):
        
        image_slices = self.prepareData(volume,self.dims,self.n_channels,masks)
        
        for image in image_slices:
            test_image = image.reshape(1, self.dims[0], self.dims[1], self.n_channels)
            prob_predicts = self.model.predict(test_image)
            class_image = np.argmax(prob_predicts, axis=3)
            class_image = np.reshape(class_image[0], (self.dims[0], self.dims[1]))
            self.prob_images.append(prob_predicts)
            self.class_images.append(class_image)

        self.class_images = np.array(self.class_images)
        vtk_mask = self.getVTKImage(volume,self.class_images)
        
        self.ResetKeras(self.model)
        
        if(visualize):
            
            #Set number of images to display and the plot rows and columns
            n_images = 5
            n_cols = 2
        
            #define plot shape
            fig, axs = plt.subplots(n_images,n_cols, figsize=(8, 6))
            
            
            for i in range(0,n_images):
                
                #get random image and its mask
                random_img = random.randint(0,len(self.class_images)-1)
                img = image_slices[random_img]
                img = cv2.normalize(img,None,alpha=0,beta=255, 
                        norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                # img = (((img - img.min())/(img.max() - img.min()))*255 + sys.float_info.epsilon).astype('uint8')
                mask = self.class_images[random_img] 

                
                #plot imagae and mask
                axs[i,0].imshow(img[:,:,0],cmap=plt.cm.bone)
                axs[i,1].imshow(mask,cmap=plt.cm.bone)
     
            
            plt.show()

        return vtk_mask
    
    def postProcess(self,bImg,s=3):
        lImg = label(bImg)
        lcc = self.largestCC(lImg)
        # lcc = scipy.ndimage.morphology.binary_fill_holes(lcc)
        return lcc.astype('uint8')
        
    @staticmethod
    def saveSegmentation(vtk_image, filename):
            
        writer = vtk.vtkMetaImageWriter()
        writer.SetInputData(vtk_image)
        writer.SetFileName(filename + '.mhd')
        writer.SetRAWFileName(filename + '.raw')
        writer.Write() 
            
        return True
    
    @staticmethod
    def prepareData(volume,dims,n_channels,masks=None):
        
        if(masks):
            
            thresh = vtk.vtkImageThreshold()
            thresh.SetInputData(masks)
            thresh.ReplaceInOn()
            thresh.ThresholdByUpper(1.0)
            thresh.SetOutputScalarTypeToShort()
            thresh.SetInValue(1.0)
            thresh.Update()
            
            multiply = vtk.vtkImageMathematics()
            multiply.SetInput1Data(volume)
            multiply.SetInput2Data(thresh.GetOutput())
            multiply.SetOperationToMultiply()
            multiply.Update()
            
            volume = multiply.GetOutput()
        
        i, j, k = volume.GetDimensions()
        sc = volume.GetPointData().GetScalars()
        np_array = vtk_to_numpy(sc)
        numpy_image = np_array.reshape(k, i, j)
        n_slices = len(numpy_image)
        image_slices = np.empty((n_slices, dims[0], dims[1], n_channels), dtype='float32')
        
        for idx in range(n_slices):
            img = numpy_image[idx, :, :]
            img = cv2.resize(img, (dims[0], dims[1]))
            img = (img - img.min()) / (img.max() -img.min()) * 2
            img -= 1.0
            if n_channels == 3:
                image_slices[idx, :, :, 0] = img
                image_slices[idx, :, :, 1] = img
                image_slices[idx, :, :, 2] = img
            else:
                image_slices[idx, :, :] = img
            
        return image_slices
    
    @staticmethod
    def getVTKImage(volume,class_images):

        vtk_dims = volume.GetDimensions()
    
        numpy_image_rs = np.zeros((vtk_dims[2], vtk_dims[0], vtk_dims[1]))
    
        for idx in range(vtk_dims[2]):
            img = class_images[idx, :, :]
            img_sm = cv2.resize(img, (vtk_dims[0], vtk_dims[1]), interpolation=cv2.INTER_NEAREST)
            numpy_image_rs[idx, :, :] = img_sm
        
        vtk_data = numpy_to_vtk(num_array=numpy_image_rs.ravel(), deep=True, 
                                array_type=vtk.VTK_UNSIGNED_CHAR)
        
        vtk_image = vtk.vtkImageData()
        vtk_image.SetDimensions(volume.GetDimensions())
        vtk_image.SetSpacing(volume.GetSpacing())
        vtk_image.SetOrigin(volume.GetOrigin())
        vtk_image.AllocateScalars(vtk.VTK_UNSIGNED_CHAR,1)
        vtk_image.GetPointData().SetScalars(vtk_data)    
        
        return vtk_image
    
    # Reset Keras Session
    @staticmethod
    def ResetKeras(model):
        sess = tf.compat.v1.keras.backend.get_session()
        tf.compat.v1.keras.backend.clear_session()
        sess.close()
        sess = tf.compat.v1.keras.backend.get_session()
    
        try:
            del model # this is from global space - change this as you need
        except:
            pass
    
        print(gc.collect()) # if it's done something you should see a number being outputted
    
        # use the same config as you used to create the session
        config = tf.compat.v1.ConfigProto()
        config.gpu_options.per_process_gpu_memory_fraction = 1
        config.gpu_options.visible_device_list = "0"
        tf.compat.v1.keras.backend.set_session(tf.compat.v1.Session(config=config))
    
    @staticmethod
    def largestCC(lImg, num=1):
        cIdx = np.zeros(num, dtype = int)
        count = np.bincount(lImg.flat)
        count[0] = 0
        lcc = np.zeros(lImg.shape, dtype=bool)
        if len(count) == 2:
            num = 1
        for i in range(num):
            cIdx[i] = np.argmax(count)
            count[cIdx[i]] = 0
            lcc += (lImg == cIdx[i])
        return lcc
            
                    