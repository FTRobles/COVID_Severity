# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 15:25:27 2020

@author: daewo
"""

from fpdf import FPDF

import vtk
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk

import numpy as np
import cv2

class CreateReport:
    
    def __init__(self,total_percentage,severity_score,
                 phenotype,lobes_percentage,lobes_severity):
        
        self.total_percentage = total_percentage
        self.severity_score = severity_score
        self.phenotype = phenotype
        self.lobes_percentage = lobes_percentage
        self.lobes_severity = lobes_severity
        
        self.colors =  [[0,255,0],
                        [255,255,0],
                        [220,26,152],
                        [0,128,200],
                        [197,104,99]]
        
        return
    
    def setImages(self,volume,lobes,lesions):
        
        i,j,k = volume.GetDimensions()
        self.spacing = volume.GetSpacing()
            
        mask_array = vtk_to_numpy(volume.GetPointData().GetScalars())
        self.volume = mask_array.reshape(k,i,j)

        self.lobes = lobes
        self.lesions= lesions
        
        return
    
    def createReport(self):
        
        # Create instance of FPDF class
        # Letter size paper, use inches as unit of measure
        pdf=FPDF(format='letter', unit='in')
        
        # Add new page. Without this you cannot create the document.
        pdf.add_page()
        pdf.set_text_color(102,102,102)
         
        # Effective page width, or just epw
        epw = pdf.w - 2*pdf.l_margin
        
        # Document title centered, 'B'old, 14 pt
        pdf.set_font('Times','B',14.0) 
        pdf.cell(epw, 0.0, 'Overall Assessment', align='C')
        pdf.set_font('Times','',10.0) 
        pdf.ln(0.5)
        
        # Remember to always put one of these at least once.
        pdf.set_font('Times','',10.0) 
        # Text height is the same as current font size
        th = pdf.font_size
        
        # Set column width to 1/4 of effective page width to distribute content 
        # evenly across table and page
        col_width = epw/8
        
        pdf.set_fill_color(63,187,192)
        pdf.cell(col_width,th,'Severity Score:',border = 1, fill=True)
        pdf.cell(col_width,th,str(self.severity_score),border = 1)
        pdf.ln(th)
        pdf.cell(col_width,th,'Affected Area:',border = 1, fill=True)
        pdf.cell(col_width,th,str(self.total_percentage),border = 1)
        pdf.ln(th)
        pdf.cell(col_width,th,'Phenotype:',border = 1, fill=True)
        pdf.cell(col_width,th,self.phenotype,border = 1)
        
        pdf.ln(4*th)
        
        pdf.set_font('Times','B',14.0) 
        pdf.cell(epw, 0.0, 'Lobar Assessment', align='C')
        pdf.set_font('Times','',10.0) 
        pdf.ln(0.5)
        
        # Remember to always put one of these at least once.
        pdf.set_font('Times','',10.0) 
        # Text height is the same as current font size
        th = pdf.font_size
        
        # Set column width to 1/4 of effective page width to distribute content 
        # evenly across table and page
        col_width = epw/8
        
        pdf.cell(col_width,th,'')
        pdf.set_fill_color(self.colors[0][0],self.colors[0][1],self.colors[0][2])
        pdf.cell(col_width,th,'RUL',border = 1,fill=True)
        pdf.set_fill_color(self.colors[1][0],self.colors[1][1],self.colors[1][2])
        pdf.cell(col_width,th,'RML',border = 1,fill=True)
        pdf.set_fill_color(self.colors[2][0],self.colors[2][1],self.colors[2][2])
        pdf.cell(col_width,th,'RLL',border = 1,fill=True)
        pdf.set_fill_color(self.colors[3][0],self.colors[3][1],self.colors[3][2])
        pdf.cell(col_width,th,'LUL',border = 1,fill=True)
        pdf.set_fill_color(self.colors[4][0],self.colors[4][1],self.colors[4][2])
        pdf.cell(col_width,th,'LLL',border = 1,fill=True)
        
        pdf.ln(th)
        
        pdf.set_fill_color(63,187,192)
        pdf.cell(col_width,th,'Severity Score:',border=1,fill=True)
        pdf.cell(col_width,th,str(self.lobes_severity[0]),border = 1)
        pdf.cell(col_width,th,str(self.lobes_severity[1]),border = 1)
        pdf.cell(col_width,th,str(self.lobes_severity[2]),border = 1)
        pdf.cell(col_width,th,str(self.lobes_severity[3]),border = 1)
        pdf.cell(col_width,th,str(self.lobes_severity[4]),border = 1)
        
        pdf.ln(th)
        
        pdf.cell(col_width,th,'Affected Area:',border=1,fill=True)
        pdf.cell(col_width,th,str(self.lobes_percentage[0]),border = 1)
        pdf.cell(col_width,th,str(self.lobes_percentage[1]),border = 1)
        pdf.cell(col_width,th,str(self.lobes_percentage[2]),border = 1)
        pdf.cell(col_width,th,str(self.lobes_percentage[3]),border = 1)
        pdf.cell(col_width,th,str(self.lobes_percentage[4]),border = 1)
        
        pdf.ln(4*th)
        
        col_width = epw/4
        
        pdf.image('coronal.png',x = pdf.get_x(), y = pdf. get_y(), w = col_width*2, h = col_width*2)
     
        pdf.output('prueba.pdf','F')
    
        return
    
    def createImages(self):
        
        n = 0
        coronal_slice = 0
        
        for i in range(self.volume.shape[0]):
            
            n_temp = len(np.where(self.lesions[0][i]==1)[0]) + len(np.where(self.lesions[1][i]==1)[0])
            
            if(n_temp>n):
                
                coronal_slice = i
                n = n_temp    
                
        img = self.volume[coronal_slice]         
        ground_glass_bw = self.lesions[0][coronal_slice]
        compound_bw = self.lesions[1][coronal_slice]
        
        blend = self.blendImages(img,ground_glass_bw,compound_bw)
        
        # vtk_blend = self.createVTKImage(blend)
        # vtk_blend.SetSpacing(self.spacing[0],self.spacing[1],0)
        # self.saveVtkImage(vtk_blend,"coronal_vtk.png")
        
        cv2.imwrite("coronal.png",blend)

        # n = 0
        # axial_slice = 0
        
        # for i in range(self.volume.shape[1]):
            
        #     n_temp = len(np.where(self.lesions[0][:,i,:]==1)[0]) + len(np.where(self.lesions[1][:,i,:]==1)[0])
            
        #     if(n_temp>n):
                
        #         axial_slice = i
        #         n = n_temp    
                
        # img = self.volume[:,axial_slice,:]         
        # ground_glass_bw = self.lesions[0][:,axial_slice,:]
        # compound_bw = self.lesions[1][:,axial_slice,:]
        
        # blend = self.blendImages(img,ground_glass_bw,compound_bw)
        # blend = cv2.rotate(blend, cv2.ROTATE_180)
        
        # vtk_blend = self.createVTKImage(blend)
        # vtk_blend.SetSpacing(self.spacing[1],self.spacing[2],0)
        # self.saveVtkImage(vtk_blend,"axial_vtk.png")
        
        # cv2.imwrite("axial.png",blend)

        return
    
    @staticmethod
    def blendImages(img,ground_glass_bw,compound_bw):

        ground_glass_idx = np.where(ground_glass_bw == 1)
        
        ground_glass = np.zeros((ground_glass_bw.shape[0],ground_glass_bw.shape[1],3)).astype('uint8')  
        ground_glass[ground_glass_idx[0],ground_glass_idx[1],0] = 255       
        
        
        compound_idx = np.where(compound_bw == 1)
        
        compound = np.zeros((compound_bw.shape[0],compound_bw.shape[1],3)).astype('uint8')  
        compound[compound_idx[0],compound_idx[1],2] = 255 
        
        
        img = cv2.normalize(img,None,alpha=0,beta=255, 
                        norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        img = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)
        
        blend = cv2.addWeighted(img,1,ground_glass,0.5,0)       
        blend = cv2.addWeighted(blend,1,compound,0.5,0)  
        
        return blend
    
    @staticmethod
    def createVTKImage(image):
        
        vtk_image = vtk.vtkImageData()
        vtk_image.SetDimensions(image.shape[1], image.shape[0], 1)
        vtkarr = numpy_to_vtk(np.flip(image.swapaxes(0,1), axis=1).reshape((-1, 3), order='F'))
        vtkarr.SetName('Image')
        vtk_image.GetPointData().AddArray(vtkarr)
        vtk_image.GetPointData().SetActiveScalars('Image')
        
        return vtk_image
    
    @staticmethod
    def saveVtkImage(image,filename):
        
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(filename)
        writer.SetInputData(image)
        writer.Write()
        
        return
        
        
    
