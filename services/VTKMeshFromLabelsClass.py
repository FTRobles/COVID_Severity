# -*- coding: utf-8 -*-
"""
Created on Thu May 21 09:31:24 2020

@author: daewo
"""
from random import random
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk

class VTKMeshFromLabels:
    
    @staticmethod
    def getModelFromMask(mask,decimationFactor = 0.25, smooth_iter = 20):
    
        surface = vtk.vtkMarchingCubes()
        surface.SetInputData(mask)
        surface.SetNumberOfContours(1)
        surface.ComputeScalarsOff()
        surface.ComputeGradientsOff()
        surface.ComputeNormalsOff()
        surface.SetValue(0, 1.0)
        surface.ReleaseDataFlagOn()
        surface.Update()
        model = surface.GetOutput()
        
        if (decimationFactor > 0.0):
            decimator = vtk.vtkDecimatePro()
            decimator.SetInputData(model)
            decimator.SetFeatureAngle(60)
            decimator.SplittingOff()
            decimator.PreserveTopologyOn()
            decimator.SetMaximumError(1)
            decimator.SetTargetReduction(decimationFactor)
            decimator.Update()
            model = decimator.GetOutput()
            
            
        if (smooth_iter > 0):

            smoother = vtk.vtkWindowedSincPolyDataFilter()
            smoother.SetInputConnection(decimator.GetOutputPort())
            smoother.SetNumberOfIterations(smooth_iter)
            smoother.BoundarySmoothingOff()
            smoother.FeatureEdgeSmoothingOff()
            smoother.Update()

            model = smoother.GetOutput()

        
            
        return model
            
    @staticmethod
    def getLabelMasks(volume,nLabels = 2):
        
        i,j,k = volume.GetDimensions()
        
        mask_array = vtk_to_numpy(volume.GetPointData().GetScalars())
        mask_array = mask_array.reshape(k,i,j)
        
        masks = []
        for label in range(nLabels):
            
            idx = np.where(mask_array == label+1)
            mask = np.zeros((k,i,j))
            mask[idx] = 1
            
            vtk_data_array = numpy_to_vtk(mask.flatten())
            
            vtk_mask = vtk.vtkImageData()
            vtk_mask.DeepCopy(volume)
            vtk_mask.GetPointData().SetScalars(vtk_data_array)
            
            masks.append(vtk_mask)
        
        return masks
    
    @staticmethod
    def displayModel(scene_widget,model,opacity=1,rgb=None):
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(model)
        
        if rgb==None:
            
            rgb = []
            rgb.append(vtk.vtkMath.Random())
            rgb.append(vtk.vtkMath.Random())
            rgb.append(vtk.vtkMath.Random())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(rgb[0], rgb[1], rgb[2])
        actor.GetProperty().SetOpacity(opacity)
        scene_widget.add_actor(actor)

        scene_widget.update_view()
        
        return

    
    @staticmethod
    def saveModel(filename,model):
        
        writer = vtk.vtkSTLWriter()
        writer.SetInputData(model)
        writer.SetFileName(filename)
        writer.Write()
        
        return


