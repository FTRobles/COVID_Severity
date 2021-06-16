import sys
import vtk

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QFrame
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class SceneWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)

        colors = vtk.vtkNamedColors()
        colors.SetColor("BkgColor", [51, 77, 102, 255])

        self.frame = QFrame()
        self.vtk_widget = QVTKRenderWindowInteractor(self.frame)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.vtk_widget)
        self.setLayout(self.layout)
        self.frame.setLayout(self.layout)

        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(colors.GetColor3d("BkgColor"))

        self.renderer_window = self.vtk_widget.GetRenderWindow()
        self.renderer_window.AddRenderer(self.renderer)

        self.iren = self.vtk_widget.GetRenderWindow().GetInteractor()
        self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.iren.Initialize()

        self.__add_axes()

    def __add_axes(self):
        transform = vtk.vtkTransform()
        transform.Translate(0.0, 0.0, 0.0)

        axes_actor = vtk.vtkAxesActor()

        axes_actor.SetTotalLength(60.0, 60.0, 60.0)
        axes_actor.SetUserTransform(transform)
        self.add_actor(axes_actor)

        self.axes_widget = vtk.vtkOrientationMarkerWidget()
        self.axes_widget.SetOrientationMarker(axes_actor)
        self.axes_widget.SetInteractor(self.iren)
        self.axes_widget.SetViewport(0.0, 0.0, 0.3, 0.3)
        self.axes_widget.EnabledOn()
        self.axes_widget.InteractiveOff()

        self.update_view()

    def update_view(self):
        self.renderer.ResetCamera()
        self.renderer_window.Render()

    def add_actor(self, vtk_actor):
        self.renderer.AddActor(vtk_actor)

    def add_volume(self, vtk_volume):
        self.renderer.AddVolume(vtk_volume)
    
    def add_corner_annotation(self,annotation):
        self.renderer.AddViewProp(annotation)
