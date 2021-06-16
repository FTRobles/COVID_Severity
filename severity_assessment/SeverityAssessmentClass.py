# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 15:22:53 2020

@author: daewo
"""
import vtk
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk

from severity_assessment.CreateReportClass import  CreateReport

import numpy as np
import matplotlib.pyplot as plt

class SeverityAssessment:
    
        def __init__(self,volume,lungs,lobes,lesions):
            
            self.volume = volume
            self.lungs = lungs
            self.lobes = lobes
            self.lesions = lesions
            
            self.total_percentage = 0
            self.phenotype = 'L'
            
            self.lobes_percentages = [0]*5
            self.lobes_severity = [0]*5

            self.severity_score = 0
            
            return
        
        def overallAssessment(self):
           
            lungs_mask = self.binarizeMask(self.lungs)
            self.lesion_masks = self.getLabelMasks(self.lesions,n_labels=2)
            
            ground_glass = self.computeIntersection(lungs_mask,self.lesion_masks[0])
            consolidation = self.computeIntersection(lungs_mask,self.lesion_masks[1])
            
            self.total_percentage = round(ground_glass + consolidation,2)
            
            if(consolidation>=ground_glass):
                self.phenotype = 'H'
                              
            return self.total_percentage, self.phenotype
        
        def lobarAssessment(self):
            
            lesions_mask = self.binarizeMask(self.lesions,low_thresh=1,high_thresh=2)
            self.lobe_masks = self.getLabelMasks(self.lobes,n_labels=5)
            
            for i,lobe in enumerate(self.lobe_masks):
                
                p = self.computeIntersection(lobe,lesions_mask)                
                self.lobes_percentages[i] = p
                
                if (p > 0) and (p <= 5):
                    self.lobes_severity[i] = 1
                elif (p > 5) and (p <= 25):
                    self.lobes_severity[i] = 2
                elif (p > 25) and (p <= 50):
                    self.lobes_severity[i] = 3
                elif (p > 50) and (p <= 75):
                    self.lobes_severity[i] = 4
                elif (p > 75):
                    self.lobes_severity[i] = 5
                
            return self.lobes_percentages, self.lobes_severity
        
        def computeSeverityScore(self):
                        
            self.severity_score = np.sum(self.lobes_severity)
            
            return self.severity_score
        
        def displayAssessment(self,display_widget):
            
            cornerAnnotation = vtk.vtkCornerAnnotation()
            cornerAnnotation.SetLinearFontScaleFactor(2)
            cornerAnnotation.SetNonlinearFontScaleFactor(1)
            cornerAnnotation.SetMaximumFontSize(20)
            cornerAnnotation.GetTextProperty().SetColor(1,0,0)
            
            text_overall = "Overall Assessment: \n" + \
                    "Severity Score: " + str(self.severity_score) + '\n' + \
                    "Affected Area (%): " + str(self.total_percentage) + '\n' + \
                    "Phenotype: " + self.phenotype    
                    
            cornerAnnotation.SetText(2,text_overall)
  
            
            text_RL = "Right lung assessment (percentage, score): \n" + \
                      " \n" + \
                      "RUL: " + str(self.lobes_percentages[0]) + ", " + str(self.lobes_severity[0]) + '\n' + \
                      "RML: " + str(self.lobes_percentages[1]) + ", " + str(self.lobes_severity[1]) + '\n' + \
                      "RLL: " + str(self.lobes_percentages[2]) + ", " + str(self.lobes_severity[2])
            
            cornerAnnotation.SetText(0,text_RL)
            
            text_LL = "Left lung assessment (percentage, score): \n" + \
                      " \n" + \
                      "LUL: " + str(self.lobes_percentages[3]) + ", " + str(self.lobes_severity[3]) + '\n' + \
                      "LLL: " + str(self.lobes_percentages[4]) + ", " + str(self.lobes_severity[4])
            
            cornerAnnotation.SetText(1,text_LL)
            
            display_widget.add_corner_annotation(cornerAnnotation)
            
            return
        
        def createReport(self):
            
            report = CreateReport(self.total_percentage,self.severity_score,
                              self.phenotype,self.lobes_percentages,self.lobes_severity)
            report.setImages(self.volume,self.lobe_masks,self.lesion_masks)
            report.createImages()
            report.createReport()
        
        
        @staticmethod
        def computeIntersection(mask1,mask2):
            
            intersection = mask1*mask2 
            
            total_pixels = len(np.where(mask1==1)[0])
            intersection_pixels = len(np.where(intersection==1)[0])
            
            percentage = round((intersection_pixels/total_pixels)*100,2)
            
            
            return percentage
        
        @staticmethod
        def binarizeMask(mask,low_thresh=1,high_thresh=None):
            
            i,j,k = mask.GetDimensions()
            
            mask = vtk_to_numpy(mask.GetPointData().GetScalars())
            mask = mask.reshape(k,i,j)
            
            if(high_thresh):
                mask[np.where(np.logical_and(mask>=low_thresh, mask<=high_thresh))] = 1 
            else:
                mask[np.where(mask>=low_thresh)] = 1 
            return mask
             
        @staticmethod
        def getLabelMasks(volume,n_labels = 2):
        
            i,j,k = volume.GetDimensions()
            
            mask_array = vtk_to_numpy(volume.GetPointData().GetScalars())
            mask_array = mask_array.reshape(k,i,j)
            
            masks = []
            for label in range(n_labels):
                
                idx = np.where(mask_array == label+1)
                mask = np.zeros((k,i,j))
                mask[idx] = 1
                
                masks.append(mask)
            
            return masks
