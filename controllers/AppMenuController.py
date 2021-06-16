# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 16:43:26 2020

@author: daewo
"""

import vtk

from views import ViewerMainWindow

from severity_assessment.SeverityAssessmentClass import SeverityAssessment

from services.Files import Files
from services.SegmentationClass import Segmentation
from services.VTKMeshFromLabelsClass import VTKMeshFromLabels 
from services.VTKLabelsFromMeshClass import VTKLabelsFromMesh 
from services.VTKMeshRegistrationClass import VTKMeshRegistration

import time

class AppMenuController(object):

    def __init__(self, main_window: ViewerMainWindow):
        
        self.main_window = main_window

    def load_models(self,action):
        
        start = time.time()
        
        #Load lungs segmentation model
        print('Load lungs segmentation model')
        
        dims = (256,256)

        model = "lungs_segmentation/RESNET_LUNG_Both_2_tf1x.json"
        weights = "lungs_segmentation/RESNET_LUNG_Both_2.h5"
        
        self.lungs_segmentation = Segmentation(dims)
        self.lungs_segmentation.loadModel(model)
        self.lungs_segmentation.loadWeights(weights)
        
        #Load lesions segmentation model
        print('Load lesions segmentation model')
        
        dims = (512,512)
        
        model = "lesion_segmentation/COVID_Les_model.json"
        weights = "lesion_segmentation/COVID_Les_weights_2.h5"
        
        self.lesions_segmentation = Segmentation(dims)
        self.lesions_segmentation.loadModel(model)
        self.lesions_segmentation.loadWeights(weights)
        
        #Load atlas models
        print('Load atlas models')
        self.mesh_registration = VTKMeshRegistration()
        self.mesh_registration.readAtlasLungs()
        self.mesh_registration.readAtlasLobes()
        
        elapsed_time = (time.time() - start) 
        print("Time required to load models: " + str(elapsed_time))
                
        return
    
    def complete_assessment(self,action):               
        
        print('Segment Lungs')
        start = time.time()
        
        vtk_volume = self.main_window.file_menu_controller.vtk_volume
        vtk_lungs =  self.lungs_segmentation.segmentVolume(vtk_volume,visualize=False)
        
        labels_to_mesh = VTKMeshFromLabels()
        masks = labels_to_mesh.getLabelMasks(vtk_lungs,2)
        
        lung_models = []
        for i in range(2):
                
            model = labels_to_mesh.getModelFromMask(masks[i])
            lung_models.append(model)
            
        print('Segment Lesions')

        vtk_lesions = self.lesions_segmentation.segmentVolume(vtk_volume,masks=vtk_lungs,visualize=False)
        
        print("Register Atlas")
        
        self.mesh_registration.setPatientLungs(lung_models)
        self.mesh_registration.registerLungs()
        lobes_models = self.mesh_registration.registerAtlasLobes()
        
        print("Segment Lobes")
        
        mesh_to_labels = VTKLabelsFromMesh(vtk_volume)
        vtk_lobes = mesh_to_labels.getOneMaskFromModels(lobes_models,visualize=False)
        
        print("Assess patient severity")
        
        assess = SeverityAssessment(vtk_volume,vtk_lungs,vtk_lobes,vtk_lesions)
        total_percentage, phenotype = assess.overallAssessment()
        lobes_percentage, lobes_severity = assess.lobarAssessment()
        severity_score = assess.computeSeverityScore()
        
        assess.createReport()

        elapsed_time = (time.time() - start) 
        print("Time required for complete assessment: " + str(elapsed_time))
        
        return