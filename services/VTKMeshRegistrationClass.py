# -*- coding: utf-8 -*-
"""
Created on Tue May 19 18:59:44 2020

@author: daewo
"""

from PyQt5 import QtWidgets

import vtk
from vtk.util import numpy_support as VN
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

# from sklearn.cluster import KMeans 
import time as time

class VTKMeshRegistration():
    
    #%%
    def __init__(self,scene_widget=None):
        
        self.scene_widget = scene_widget
        
        # The source file
        self.path = 'models/'
        
        self.filenames_lungs_Atlas = ['RL.stl','LL.stl']
        
        self.filenames_lobes_Atlas = ['RUL.stl', 'RML.stl', 'RLL.stl', 
                                   'LUL.stl','LLL.stl']
        
        self.colors_atlas = [[177/255,45/255,55/255],
                        [192/255,104/255,88/255]]
        
        self.colors_atlas_lobes =  [[0/255,255/255,0/255],
                                    [255/255,255/255,0/255],
                                    [220/255,26/255,152/255],
                                    [0/255,128/255,200/255],
                                    [197/255,104/255,99/255]]
        
        self.colors_patient = [[144/255,238/255,144/255],
                    [111/255,184/255,210/255]]

    #%% Funcionality
    
    def readSTL(self,path,filename):
     
        reader = vtk.vtkSTLReader()
        reader.SetFileName((path + filename))
        reader.Update()
        poly_data = reader.GetOutput() 
        
        return reader, poly_data
    
    def getPointsArray(self,output):
        
        points_vtk = output.GetPoints()
        points = VN.vtk_to_numpy(points_vtk.GetData())
        
        return points    
    
    def displayModel(self,model,opacity=1,rgb=None):
              
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
        
        self.scene_widget.add_actor(actor)
        self.scene_widget.update_view()
        
        return

    
    def getCenter(self,polydata):
        
        centerOfMassFilter = vtk.vtkCenterOfMass()
        centerOfMassFilter.SetInputData(polydata)
        centerOfMassFilter.SetUseScalarsAsWeights(False)
        centerOfMassFilter.Update()
        center = centerOfMassFilter.GetCenter()
        
        return center
    
    def getBoundingBox(self,points):
        
        dim = points.shape[1]
        max_points = []
        min_points = []
        
        for i in range(dim):
            max_points.append(points[:,i].max())
            min_points.append(points[:,i].min())
            
        bbox = []
        bbox.append([min_points[0],min_points[1],min_points[2]])
        bbox.append([min_points[0],max_points[1],min_points[2]])
        bbox.append([max_points[0],min_points[1],min_points[2]])
        bbox.append([max_points[0],max_points[1],min_points[2]])
        bbox.append([min_points[0],min_points[1],max_points[2]])
        bbox.append([max_points[0],min_points[1],max_points[2]])
        bbox.append([min_points[0],max_points[1],max_points[2]])
        bbox.append([max_points[0],max_points[1],max_points[2]])
         
        return bbox
    
        
    #%% Read Lungs
    
    def readLungs(self,filenames,colors=None):
        
        poly_datas = []
        
        for i,file in enumerate(filenames):
            _, poly_data = self.readSTL(self.path,file)
            poly_datas.append(poly_data)
      
        return poly_datas
    
        
    def setPatientLungs(self,lungs):
        
        self.poly_data_patient = lungs
        
    
    def readAtlasLungs(self,):
        self.poly_data_lungs_atlas = self.readLungs(self.filenames_lungs_Atlas,
                                                    colors=self.colors_atlas)
        
    
        return
    #%% Register Functions
    
    def transformPolydata(self,poly_data,transform):
        
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetInputData(poly_data)
        transformFilter.SetTransform(transform)
        transformFilter.Update()
        transform_polydata = transformFilter.GetOutput()
        
        
        return transform_polydata
    
    def getLandmarkPoints(self,poly_datas):
        
        
        landmarks = vtk.vtkPoints()
    
        for i, poly_data in enumerate(poly_datas):      
        
            
            
            center = self.getCenter(poly_data)
            landmarks.InsertNextPoint(center)

            
            points = self.getPointsArray(poly_data)
            bbox = self.getBoundingBox(points)  
            
            for point in bbox:
                
                landmarks.InsertNextPoint(point)

        
        return landmarks
    
    def getLandmarkTransform(self,source_points,target_points):
            
        transform = vtk.vtkLandmarkTransform()
        transform.SetModeToAffine()
        transform.SetSourceLandmarks(source_points)
        transform.SetTargetLandmarks(target_points)
            
        return transform
    

    def getICPTransform(self,source,target,n_iter=2000,n_landmarks=1000,mean_distance=0.001):
    
        icp = vtk.vtkIterativeClosestPointTransform()
        icp.SetSource(source)
        icp.SetTarget(target)
        icp.GetLandmarkTransform().SetModeToAffine()
        icp.SetCheckMeanDistance(True)
        icp.SetStartByMatchingCentroids(True)
        icp.SetMaximumNumberOfLandmarks(n_landmarks)
        icp.SetMaximumNumberOfIterations(n_iter)
        # icp.SetMaximumMeanDistance(mean_distance)
        icp.Modified()
        icp.Update()
        
        return icp
    
    #%% Register Lungs
    
    def registerLungs(self,):
    
        landmarks_atlas = self.getLandmarkPoints(self.poly_data_lungs_atlas)     
        landmarks_patient = self.getLandmarkPoints(self.poly_data_patient)
        
        self.transform_init = self.getLandmarkTransform(landmarks_atlas,landmarks_patient)
        self.transform_icp = []
        
        transform_lung_atlas = []
        
        
        for i, poly_data in enumerate(self.poly_data_lungs_atlas):
            
            poly_data = self.transformPolydata(poly_data,self.transform_init)
            
            self.transform_icp.append(self.getICPTransform(poly_data,self.poly_data_patient[i]))
            poly_data = self.transformPolydata(poly_data,self.transform_icp[i])
            
            transform_lung_atlas.append(poly_data)  
        
        return
    
    #%% read Lobes
    
    def readLobes(self,filenames,colors=None):
        
        poly_datas = []
        
        for i,file in enumerate(filenames):
            _, poly_data = self.readSTL(self.path,file)
            poly_datas.append(poly_data)
            
        return poly_datas
    
    def readAtlasLobes(self,):
        self.poly_data_lobes_atlas = self.readLobes(self.filenames_lobes_Atlas,
                                                    colors=self.colors_atlas_lobes)
    
    #%% Register Lobes
    
    def transformLobes(self,poly_datas):
        
        transform_polydatas = []
        
        for i, poly_data in enumerate(poly_datas):
            
            poly_data = self.transformPolydata(poly_data,self.transform_init)

            if i<3:
                poly_data = self.transformPolydata(poly_data,self.transform_icp[0])
            else:
                poly_data = self.transformPolydata(poly_data,self.transform_icp[1])
            
            transform_polydatas.append(poly_data)
        
        return transform_polydatas
    
    def registerAtlasLobes(self):
    
        transform_lobes = self.transformLobes(self.poly_data_lobes_atlas)
        
        if(self.scene_widget):
        
            self.displayModel(transform_lobes[0],
                          opacity=0.5,rgb=self.colors_atlas_lobes[0])
            self.displayModel(transform_lobes[1],
                          opacity=0.5,rgb=self.colors_atlas_lobes[1])
            self.displayModel(transform_lobes[2],
                          opacity=0.5,rgb=self.colors_atlas_lobes[2])
            self.displayModel(transform_lobes[3],
                          opacity=0.5,rgb=self.colors_atlas_lobes[3])
            self.displayModel(transform_lobes[4],
                          opacity=0.5,rgb=self.colors_atlas_lobes[4])
        
        return transform_lobes
    
    
    
