import vtk

from random import random

from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory

from services.Files import Files
from views import ViewerMainWindow


class FileMenuController(object):

    def __init__(self, main_window: ViewerMainWindow):
        self.main_window = main_window
        
        self.vtk_volume = vtk.vtkImageData()
        
    def open_stl_mesh(self, action):
        """
        Display a stl mesh into the visualizer
        :param action: action from an event
        :return: null
        """
        Tk().withdraw()
        filenames = askopenfilename(title="Open Mesh",
                                    filetypes=(("mesh files", "*.stl"), ("all files", "*.*")),
                                    multiple="true")

        if filenames != "":
            color_atlas = []
            scene_widget = self.main_window.scene_widget
            
            for i, filename in enumerate(filenames):
                poly_data = Files.read_stl(filename)

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputData(poly_data)

                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                
                if len(color_atlas) < len(filenames):
                    color_atlas.insert(i, [random(), random(), random()])

                actor.GetProperty().SetColor(color_atlas[i][0], color_atlas[i][1], color_atlas[i][2])
                actor.GetProperty().SetOpacity(0.9)
                scene_widget.add_actor(actor)

            scene_widget.update_view()


    def open_dicom_volume(self, action):
        Tk().withdraw()
        foldername = askdirectory(title="Select DICOM Folder")
        if foldername != "":
            scene_widget = self.main_window.scene_widget
            self.vtk_volume = Files.read_dicom(foldername)
 
            dims = self.vtk_volume.GetDimensions()
            origin = self.vtk_volume.GetOrigin()
            print(dims)

            outline_actor = self.__add_outline(self.vtk_volume)
            plane_actors = self.__add_3d_slices(self.vtk_volume)
            axial = plane_actors[0]
            coronal = plane_actors[1]
            sagittal = plane_actors[2]

            # add components to the scene and update
            scene_widget.add_actor(sagittal)
            scene_widget.add_actor(coronal)
            scene_widget.add_actor(axial)
            scene_widget.add_actor(outline_actor)
            scene_widget.update_view()
            
    def open_nifti_volume(self, action):
        
        Tk().withdraw()
        filename = askopenfilename(title="Open Volume")
        if filename != "":
            scene_widget = self.main_window.scene_widget
            self.vtk_volume = Files.read_volume_itk(filename)

            dims = self.vtk_volume.GetDimensions()
            origin = self.vtk_volume.GetOrigin()

            outline_actor = self.__add_outline(self.vtk_volume)
            plane_actors = self.__add_3d_slices(self.vtk_volume)
            axial = plane_actors[0]
            coronal = plane_actors[1]
            sagittal = plane_actors[2]

            # add components to the scene and update
            scene_widget.add_actor(sagittal)
            scene_widget.add_actor(coronal)
            scene_widget.add_actor(axial)
            scene_widget.add_actor(outline_actor)
            scene_widget.update_view()    
            
    def open_DICOMDIR(self,action):
        
        Tk().withdraw()
        filename = askopenfilename(title="Open Volume")
        if filename != "":
            scene_widget = self.main_window.scene_widget
            self.vtk_volume = Files.read_dicomdir(filename)
        
        

    def close_all(self, action):
        self.main_window.close()
        

    @staticmethod
    def __add_outline(image) -> vtk.vtkActor:
        """
        Create an outline over the volume
        :param image:
        :return: an actor representing the outline
        """

        colors = vtk.vtkNamedColors()
        outline_data = vtk.vtkOutlineFilter()
        outline_data.SetInputData(image)
        map_outline = vtk.vtkPolyDataMapper()
        map_outline.SetInputConnection(outline_data.GetOutputPort())

        outline_actor = vtk.vtkActor()
        outline_actor.SetMapper(map_outline)
        outline_actor.GetProperty().SetColor(colors.GetColor3d("Gray"))

        return outline_actor
    
    @staticmethod
    def __add_3d_slices(image_data):
        dims = image_data.GetDimensions()

        # creating a black/white lookup table.
        bw_lut = vtk.vtkLookupTable()
        bw_lut.SetTableRange(-768, 1200)
        bw_lut.SetSaturationRange(0, 0)
        bw_lut.SetHueRange(0, 0)
        bw_lut.SetValueRange(0, 1)
        bw_lut.Build()

        # add slices
        sagittal_colors = vtk.vtkImageMapToColors()
        sagittal_colors.SetInputData(image_data)
        sagittal_colors.SetLookupTable(bw_lut)
        sagittal_colors.Update()

        sagittal = vtk.vtkImageActor()
        sagittal.GetMapper().SetInputConnection(sagittal_colors.GetOutputPort())
        sagittal.SetDisplayExtent(0, dims[0], int(dims[1] / 2), int(dims[1] / 2), 0, dims[2])

        axial_colors = vtk.vtkImageMapToColors()
        axial_colors.SetInputData(image_data)
        axial_colors.SetLookupTable(bw_lut)
        axial_colors.Update()

        axial = vtk.vtkImageActor()
        axial.GetMapper().SetInputConnection(axial_colors.GetOutputPort())
        axial.SetDisplayExtent(0, dims[0], 0, dims[1], int(dims[2] / 2), int(dims[2] / 2))

        coronal_colors = vtk.vtkImageMapToColors()
        coronal_colors.SetInputData(image_data)
        coronal_colors.SetLookupTable(bw_lut)
        coronal_colors.Update()

        coronal = vtk.vtkImageActor()
        coronal.GetMapper().SetInputConnection(coronal_colors.GetOutputPort())
        coronal.SetDisplayExtent(int(dims[0] / 2), int(dims[0] / 2), 0, dims[1], 0, dims[2])

        return [axial, coronal, sagittal]

