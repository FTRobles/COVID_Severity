import vtk

from views import ViewerMainWindow

from severity_assessment.SeverityAssessmentClass import SeverityAssessment

from services.Files import Files
from services.SegmentationClass import Segmentation
from services.VTKMeshFromLabelsClass import VTKMeshFromLabels 
from services.VTKLabelsFromMeshClass import VTKLabelsFromMesh 
from services.VTKMeshRegistrationClass import VTKMeshRegistration

class ProcessMenuController(object):

    def __init__(self, main_window: ViewerMainWindow):
        self.main_window = main_window
        self.vtk_lungs = vtk.vtkImageData()
        self.vtk_lesions = vtk.vtkImageData()
        self.n_labels = 2
        self.lung_models = []
        self.lesion_models = []
        self.lobes_models = []
        
        self.colors_patient = [[144/255,238/255,144/255],
                    [111/255,184/255,210/255],
                    [255/255,255/255,255/255],
                    [255/255,0/255,0/255]]

    def registration(self, action):
        
        print("Quiero registrar dos mallas")
        
        scene_widget = self.main_window.scene_widget
        
        mesh_registration = VTKMeshRegistration(scene_widget)
        mesh_registration.readAtlasLungs()
        mesh_registration.setPatientLungs(self.lung_models)
        mesh_registration.registerLungs()
        mesh_registration.readAtlasLobes()
        self.lobes_models = mesh_registration.registerAtlasLobes()
        

    def generate_mesh(self, action):
        
        scene_widget = self.main_window.scene_widget
        
        labels_to_mesh = VTKMeshFromLabels()
        masks = labels_to_mesh.getLabelMasks(self.vtk_lungs,self.n_labels)
        
        for i in range(self.n_labels):
                
            model = labels_to_mesh.getModelFromMask(masks[i])
            labels_to_mesh.displayModel(scene_widget,model,opacity=0.4,rgb=self.colors_patient[i])
            self.lung_models.append(model)
            
        masks = labels_to_mesh.getLabelMasks(self.vtk_lesions,self.n_labels)
            
        for i in range(self.n_labels):
                
            model = labels_to_mesh.getModelFromMask(masks[i])
            labels_to_mesh.displayModel(scene_widget,model,opacity=1,rgb=self.colors_patient[i+2])
            self.lesion_models.append(model)
                
        return


    def segment_lungs(self, action):
        
        print('Segment Lungs')
        
        dims = (256,256)

        model = "lungs_segmentation/RESNET_LUNG_Both_2_tf1x.json"
        weights = "lungs_segmentation/RESNET_LUNG_Both_2.h5"
        
        vtk_volume = self.main_window.file_menu_controller.vtk_volume
        segmentation = Segmentation(dims)
        segmentation.loadModel(model)
        segmentation.loadWeights(weights)
        self.vtk_lungs = segmentation.segmentVolume(vtk_volume)
        segmentation.saveSegmentation(self.vtk_lungs,"Resultados/Lungs_segmentation")
        
        return
    
    def segment_lesions(self, action):
        
        print('Segment Lesions')
        
        dims = (512,512)
        
        model = "lesion_segmentation/COVID_Les_model.json"
        weights = "lesion_segmentation/COVID_Les_weights_2.h5"
        
        vtk_volume = self.main_window.file_menu_controller.vtk_volume
        segmentation = Segmentation(dims)
        segmentation.loadModel(model)
        segmentation.loadWeights(weights)
        self.vtk_lesions = segmentation.segmentVolume(vtk_volume,masks=self.vtk_lungs)
        segmentation.saveSegmentation(self.vtk_lungs,"Resultados/Lesions_segmentation")
        
        return
    
    def segment_lobes(self, action):
        
        vtk_volume = self.main_window.file_menu_controller.vtk_volume
        mesh_to_labels = VTKLabelsFromMesh(vtk_volume)
        self.vtk_lobes = mesh_to_labels.getOneMaskFromModels(self.lobes_models)
        Segmentation.saveSegmentation(self.vtk_lobes,"Resultados/Lobes_segmentation")
        
        return
    
    def severity_assessment(self, action):
        
        vtk_volume = self.main_window.file_menu_controller.vtk_volume
        assess = SeverityAssessment(vtk_volume,self.vtk_lungs,self.vtk_lobes,self.vtk_lesions)
        total_percentage, phenotype = assess.overallAssessment()
        lobes_percentage, lobes_severity = assess.lobarAssessment()
        severity_score = assess.computeSeverityScore()
        
        scene_widget = self.main_window.scene_widget
        assess.displayAssessment(scene_widget)
        assess.createReport()
        
        
        
        return
        