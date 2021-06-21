COVID severity score assessment using deep learning

# COVID 3D severity

This system has the basic user interface to assisst medical staff in computing of severity scrore of COVID-19 patiens using 3D-CT.

Implemented Tools:

- 2D and segmntation of lungs and covid lesions using deep learning
- Registration of 3D lobe segmentation template
- Segmentation of lobes (fine ICP registration)
- Severity score computation
- Ineractive tools for 3D rendering
- PDF report creation with severity sore

## Installation

The develop of this tool was made on [Anaconda](https://www.anaconda.com), so is not necessary but the easiest way to get an environment with all the libraries with its own versions.

### Required extra librarys

|NAME|VERSION|
|:---:|:---:|
|vtk|9.0.1|
|pydicom|1.3.0|
|pillow|7.0.0|
|SimpleITK|1.2.4|
|Tensorflow|2.1.0|
|Keras|2.3.1|
|SKImage|0.17.2|
|Open-CV|4.1.2.30|
|Scipy|1.3.1|
|Matplotlib|3.2.1|

__NOTE: Use python 3.7 or below__

### Get ready all requirements

Once you have installed Anaconda you should follow the next steps.

- Create a new environment __(Python <= 3.7)__
- Add a new channel: Conda-Forge

Using pip from terminal:

~~~bash
conda create --name NEW_ENV python==3.7
pip install pydicom==1.3.0
pip install pillow==7.0.0
pip install vtk==9.0.1
pip install SimpleITK
pip install Scikit-Image==0.17.2
pip intall opencv-python==4.1.2.30
pip install Matplotlib
pip install Scipy==1.3.1
conda install tensorflow==2.1.0
conda install Keras==2.3.1 
~~~

If you have any doubts, comments or want access to the DL and Mesh models please contact 
fabian_torres@cvicom.unam.mx



