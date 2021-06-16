import vtk
import SimpleITK as sitk
from vtkmodules.util.numpy_support import numpy_to_vtk

import numpy as np

import pydicom
from pydicom.filereader import read_dicomdir
from os.path import dirname, join
from pprint import pprint

class Files(object):

    @staticmethod
    def read_dicom(foldername):
        """
        Reads DICOM volume from a given folder containing the images.
        :param foldername: folder name and path
        :return: a vtkImageData
        """
        reader = sitk.ImageSeriesReader()
        dicom_names = reader.GetGDCMSeriesFileNames(foldername)
        reader.SetFileNames(dicom_names)
        itk_image = reader.Execute()

        np_image = sitk.GetArrayFromImage(itk_image)
        vtk_data_array = numpy_to_vtk(np_image.flatten(), array_type=vtk.VTK_SHORT)

        vtk_image = vtk.vtkImageData()
        vtk_image.SetDimensions(itk_image.GetSize())
        vtk_image.SetSpacing(itk_image.GetSpacing())
        # vtk_image.SetOrigin(itk_image.GetOrigin())
        vtk_image.GetPointData().SetScalars(vtk_data_array)
        return vtk_image

    @staticmethod
    def read_volume_itk(filename):
        itk_image = sitk.ReadImage(filename)
        np_image = sitk.GetArrayFromImage(itk_image)
        vtk_data_array = numpy_to_vtk(np_image.flatten(), array_type=vtk.VTK_SHORT)

        vtk_image = vtk.vtkImageData()
        vtk_image.SetDimensions(itk_image.GetSize())
        vtk_image.SetSpacing(itk_image.GetSpacing())
        # vtk_image.SetOrigin(itk_image.GetOrigin())
        vtk_image.GetPointData().SetScalars(vtk_data_array)
        return vtk_image
    
    @staticmethod
    def read_stl(filename):
        reader = vtk.vtkSTLReader()
        reader.SetFileName(filename)
        reader.Update()
        poly_data = reader.GetOutput()
        return poly_data
    
    @staticmethod
    def read_dicomdir(filename):
        
        dicom_dir = read_dicomdir(filename)
        base_dir = dirname(filename)
        
        # go through the patient record and print information
        for patient_record in dicom_dir.patient_records:
            

            studies = patient_record.children
            
            # got through each serie
            for study in studies:

                all_series = study.children
                
                # go through each serie
                for series in all_series:
                    
                    
                    if(series.SeriesDescription == "CORONAL"):
                        print(" " * 12 + "Reading images...")
                        image_records = series.children
                        image_filenames = [join(base_dir, *image_rec.ReferencedFileID)
                                           for image_rec in image_records]
            
                        datasets = [pydicom.dcmread(image_filename)
                                    for image_filename in image_filenames]
                   
        imgs = []
        for n, ds in enumerate(datasets):
            imgs.append(ds.pixel_array)
            
        np_image = np.array(imgs)
        vtk_data_array = numpy_to_vtk(np_image.flatten(), array_type=vtk.VTK_SHORT)
        
        img_size = [ds.Rows, ds.Columns,len(datasets)]
        img_spacing = [ds.PixelSpacing[0],ds.PixelSpacing[1],1]
        
        vtk_image = vtk.vtkImageData()
        vtk_image.SetDimensions(img_size)
        vtk_image.SetSpacing(img_spacing)
        # vtk_image.SetOrigin(itk_image.GetOrigin())
        vtk_image.GetPointData().SetScalars(vtk_data_array)
        
        
        return
                
                
