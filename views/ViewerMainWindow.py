from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QMainWindow, QLabel, QMenu, QAction
from PyQt5.QtCore import Qt

from controllers.FileMenuController import FileMenuController
from controllers.ProcessMenuController import ProcessMenuController
from controllers.AppMenuController import AppMenuController
from views.SceneWidget import SceneWidget


class ViewerMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Visualizador Qt - VTK")
        self.resize(1280, 800)

        self.status_label = QLabel("Basic Image Viewer")

        self.file_menu_controller = FileMenuController(self)
        self.process_menu_controller = ProcessMenuController(self)
        self.app_menu_controller = AppMenuController(self)

        # Actions for menus
        
        # --------- file_menu_controller ----------
        self.open_mesh_act = QAction("&Open STL Mesh", self)
        self.open_nifti_volume_act = QAction("&Open NIFTI", self)
        self.open_dicom_volume_act = QAction("&Open DICOM", self)
        self.open_dicomdir_volume_act = QAction("&Open DICOMDIR", self)
        self.exit_act = QAction("&Exit", self)
        
        # --------- process_menu_controller ----------
        self.segment_lungs_act = QAction("Lungs Segmentation", self)
        self.segment_lesions_act = QAction("Lesion Segmentation", self)
        self.create_mesh_act = QAction("Generate Mesh From Label", self)
        self.registration_act = QAction("Registration", self)
        self.segment_lobes_act =  QAction("Lobes Segmentation", self)
        self.severity_assessment_act =  QAction("Severity Assessment", self)
        
        # --------- app_menu_controller ----------
        self.load_models_act = QAction("Load Models", self)
        self.complete_assessment_act = QAction("Complete severity assesment", self)
        
        # create interface menus
        self.create_status_bar()
        self.create_actions()
        self.create_menus()

        self.scene_widget = SceneWidget()
        self.setCentralWidget(self.scene_widget.frame)

    def create_actions(self):
        
        # -------------------- File Menu --------------------
        self.open_mesh_act.setStatusTip("Open Mesh")
        self.open_mesh_act.triggered.connect(self.file_menu_controller.open_stl_mesh)
        
        self.open_nifti_volume_act.setShortcuts(QKeySequence.Open)
        self.open_nifti_volume_act.setStatusTip("Open Volume")
        self.open_nifti_volume_act.triggered.connect(self.file_menu_controller.open_nifti_volume)

        self.open_dicom_volume_act.setStatusTip("Open Volume")
        self.open_dicom_volume_act.triggered.connect(self.file_menu_controller.open_dicom_volume)
        
        self.open_dicomdir_volume_act.setStatusTip("Open Volume")
        self.open_dicomdir_volume_act.triggered.connect(self.file_menu_controller.open_DICOMDIR)

        self.exit_act.setShortcut(Qt.CTRL + Qt.Key_Q)
        self.exit_act.setStatusTip("Exit the application")
        self.exit_act.triggered.connect(self.file_menu_controller.close_all)


        
        # -------------------- Proces Menu --------------------
        self.segment_lungs_act.setStatusTip("Generate labelmap with deep learning")
        self.segment_lungs_act.triggered.connect(self.process_menu_controller.segment_lungs)
        
        self.segment_lesions_act.setStatusTip("Generate labelmap with deep learning")
        self.segment_lesions_act.triggered.connect(self.process_menu_controller.segment_lesions)
        
        self.create_mesh_act.setStatusTip("Generate mesh from labeled volume")
        self.create_mesh_act.triggered.connect(self.process_menu_controller.generate_mesh)

        self.registration_act.setStatusTip("Register two opened meshes")
        self.registration_act.triggered.connect(self.process_menu_controller.registration)
        
        self.segment_lobes_act.setStatusTip("Creates labelmap from mesh")
        self.segment_lobes_act.triggered.connect(self.process_menu_controller.segment_lobes)
        
        self.severity_assessment_act.setStatusTip("Compute the severity of Covid-19 patients")
        self.severity_assessment_act.triggered.connect(self.process_menu_controller.severity_assessment)
        
        # -------------------- App Menu --------------------
        self.load_models_act.setStatusTip("Load deeplearning and atlas models")
        self.load_models_act.triggered.connect(self.app_menu_controller.load_models)
        
        self.complete_assessment_act.setStatusTip("Create Report of severity in Covd-19 patients")
        self.complete_assessment_act.triggered.connect(self.app_menu_controller.complete_assessment)

    def create_menus(self):
        file_menu = QMenu("File", self)
        file_menu.addAction(self.open_mesh_act)
        file_menu.addSeparator()
        file_menu.addAction(self.open_nifti_volume_act)
        file_menu.addAction(self.open_dicom_volume_act)
        file_menu.addAction(self.open_dicomdir_volume_act)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_act)

        process_menu = QMenu("Process", self)
        process_menu.addAction(self.segment_lungs_act)
        process_menu.addAction(self.segment_lesions_act)
        process_menu.addAction(self.create_mesh_act)
        process_menu.addAction(self.registration_act)
        process_menu.addAction(self.segment_lobes_act)
        process_menu.addAction(self.severity_assessment_act)
        
        app_menu = QMenu("App", self)
        app_menu.addAction(self.load_models_act)
        app_menu.addAction(self.complete_assessment_act)

        self.menuBar().addMenu(file_menu)
        self.menuBar().addMenu(process_menu)
        self.menuBar().addMenu(app_menu)

    def create_status_bar(self):
        self.status_label.setAlignment(Qt.AlignVCenter)
        self.statusBar().addWidget(self.status_label)

    def get_scene_widget(self) -> SceneWidget:
        return self.scene_widget
