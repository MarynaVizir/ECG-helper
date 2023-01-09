# ECG-helper
> This is a desktop app that helps a doctor or medical student interpret an ECG.
> Live demo [_here_](https://drive.google.com/file/d/1l918vuPMfPAD7McZbHtgl5_2v2l-ELs-/view?usp=share_link). 

## Table of Contents
* [General Info](#general-information)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Setup](#setup)
* [Usage](#usage)
* [Project Status](#project-status)
* [Room for Improvement](#room-for-improvement)
* [Contact](#contact)
<!-- * [License](#license) -->


## General Information
- For several years I worked as a doctor of the admitting 
department at the regional hospital. In the regime of night 
shifts mostly. During that period realized that no matter 
how experienced a doctor is, every time, looking at the 
cardiogram of a new patient suspected of having an acute 
heart attack, he tries not to suddenly miss the only 
millimeter, which is crucial. And it could happen at 3 AM 
and after 20 or more other cases... That's why even then
I hoped for the development of at least some kind of 
automated interpretation to be more insured and confident. 
Of course, the doctor's interpretation should be decisive, 
no matter how perfect the program is.
I currently teach at a medical university. I work only with 
foreign English-speaking students who just dream that 
everything will be as automated as possible by the time 
of their independent practice)
This is how this project was born, the long-standing idea 
of which I just couldn't help but try to implement. I hope it 
will someday help both my former colleagues and my former 
students. 
- The **_purpose_** is an additional automatic interpretation of 
the electrocardiogram from its picture.


## Technologies Used
- Python - version 3.10.5
- opencv-python - version 4.6.0.66 
- Pillow - version 9.3.0
- numpy - version 1.23.5 


## Features
The ready features here:
- Myocardial infarction (STEMI using measurement of J-point elevation)
- 


## Setup
In order to setup the project install all dependencies listed 
in _**'requirements.txt'**_  file at your local environment.
Use the command:

`$ pip install -r requirements.txt`


## Usage
Run **_'ecg_app.py'_**  then to use the application.
For trial, one cardiogram sample was added to the project, 
so select the file **_'ecg_for_test.png'_**  during 
the request when the application is running.


## Project Status
Project is: _in progress_ . 


## Room for Improvement

Room for improvement:
- Finding the separate cardiac cycle
- Filling the gaps in line with averages

To do:
- Assessment for arrhythmias
- Assessment for hypertrophy


## Contact
Created by [MarynaVizir](https://github.com/MarynaVizir). 
My [LinkedIn](https://www.linkedin.com/in/maryna-vizir-55402321a).
Feel free to contact me!
