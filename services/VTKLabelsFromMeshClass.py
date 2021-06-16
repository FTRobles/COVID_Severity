# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 13:27:54 2020

@author: daewo
"""

import random
import numpy as np
import vtk
import matplotlib.pyplot as plt
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk

class VTKLabelsFromMesh:
    
    def __init__(self,vtk_volume):
        
        self.vtk_volume = vtk_volume
        
        
    def getMaskFromModel(self, model, color_value):
        
        dataToStencil = vtk.vtkPolyDataToImageStencil()
        dataToStencil.SetInputData(model)
        dataToStencil.SetOutputSpacing(self.vtk_volume.GetSpacing())
        dataToStencil.SetOutputOrigin(self.vtk_volume.GetOrigin())
        dataToStencil.SetOutputWholeExtent(self.vtk_volume.GetExtent())
        data = dataToStencil.GetOutput()
        dataToStencil.Update()
        
        stencilToImageFilter = vtk.vtkImageStencilToImage()
        stencilToImageFilter.SetInputData(data)
        stencilToImageFilter.SetOutsideValue(0)
        stencilToImageFilter.SetInsideValue(color_value)
        stencilToImageFilter.SetOutputScalarTypeToUnsignedChar()
        stencilToImageFilter.Update()
        
        mask = stencilToImageFilter.GetOutput()
        
        return mask
    
    def getOneMaskFromModels(self,models,visualize=True):
        
        label_map = vtk.vtkImageData()
        label_map.SetDimensions(self.vtk_volume.GetDimensions())
        label_map.SetSpacing(self.vtk_volume.GetSpacing())
        label_map.SetOrigin(self.vtk_volume.GetOrigin())
        label_map.AllocateScalars(vtk.VTK_UNSIGNED_CHAR,1)
        label_map.GetPointData().GetScalars().Fill(0)
        
        for i,model in enumerate(models):
            
            mask = self.getMaskFromModel(model, i+1)
            
            math = vtk.vtkImageMathematics()
            math.SetInput1Data(label_map)
            math.SetInput2Data(mask)
            math.SetOperationToMax()
            math.Update()
            
            label_map = math.GetOutput()
            
        if(visualize):
            
            i, j, k = label_map.GetDimensions()
            
            volume_array = vtk_to_numpy(self.vtk_volume.GetPointData().GetScalars())
            volume_array = volume_array.reshape(k, i, j)
        
            mask_array = vtk_to_numpy(label_map.GetPointData().GetScalars())
            mask_array = mask_array.reshape(k, i, j)
            
            #Set number of images to display and the plot rows and columns
            n_images = 5
            n_cols = 2
        
            #define plot shape
            fig, axs = plt.subplots(n_images,n_cols, figsize=(8, 6))
            
            
            for i in range(0,n_images):
                
                #get random image and its mask
                random_img = random.randint(0,volume_array.shape[0]-1)
                img = volume_array[random_img]
                mask = mask_array[random_img]
                
                #plot imagae and mask
                axs[i,0].imshow(img,cmap=plt.cm.bone)
                axs[i,1].imshow(mask,cmap=plt.cm.bone)
     
            
            plt.show()
            
        return label_map
            
        
        
        
            
            
    
