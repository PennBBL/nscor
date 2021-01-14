### This script downloads previously not downloaded raw data from NASA_821559
### on flywheel to PMACS
###
### Ellyn Butler
### January 6, 2020


import subprocess as sub
import os
import flywheel
import json
import shutil
import re
import time
#import pandas as pd
#import pytz
import datetime
import zipfile
#import numpy as np



#outdir = '/Users/butellyn/Documents/nscor/data/raw/' # path on local computer
#outdir = '/home/butellyn/nscor/data/raw/' # tmp path on PMACS
#outdir = '/project/bbl_projects/nscor/data/raw/' # Path on PMACS

fw = flywheel.Client()
proj = fw.lookup('bbl/NASA_821559') #NSCOR_831353
subjects = proj.subjects()

if not os.path.exists(outdir):
    os.mkdir(outdir)

for subj in subjects:
    sublabel = subj['label']
    if not os.path.exists(outdir+'sub-'+sublabel):
        os.mkdir(outdir+'sub-'+sublabel)
    for ses in subj.sessions():
        ses = ses.reload()
        seslabel = ses['label']
        sesdir = outdir+'sub-'+sublabel+'/ses-'+seslabel+'/'
        if not os.path.exists(sesdir):
            os.mkdir(sesdir)
        # Check if output directory is empty
        # if so, download the session zip and unzip it
        if len(os.listdir(sesdir)) == 0:
            if len(ses.files) > 0:
                for file in ses.files: # January 6, 2020: Files do not include niftis...
                    filename = file['name']
                    ses.download_file(filename, sesdir+filename)
                    # Unzip files
                    with zipfile.ZipFile(sesdir+filename,"r") as zip_ref:
                        zip_ref.extractall(sesdir)
                    # Move all of the files into the created session directory
                    if os.path.exists(sesdir+sublabel):
                        file_names = os.listdir(sesdir+sublabel) #line "22"
                        for file_name in file_names:
                            shutil.move(os.path.join(sesdir+sublabel, file_name), sesdir)
                        os.rmdir(sesdir+sublabel)
                    else:
                        os.system('echo sub-'+sublabel+' ses-'+seslabel+' does not have expected files >> '+outdir+'info.txt')
                for acq in ses.acquisitions(): # January 6, 2020: Files do not include niftis...
                    for file in acq['files']:
                        filename = file['name']
                        acq.download_file(filename, sesdir+filename)
                        # Unzip files
                        #with zipfile.ZipFile(sesdir+filename,"r") as zip_ref:
                        #    zip_ref.extractall(sesdir)
            else:
                print('sub-'+sublabel+' ses-'+seslabel+' has zero files')
        else:
            print('sub-'+sublabel+' ses-'+seslabel+' has previously downloaded content')

# Check the number of files for each subject
for subj in subjects:
    sublabel = subj['label']
    for ses in subj.sessions():
        seslabel = ses['label']
        print('sub-'+sublabel+' ses-'+seslabel+' has '+str(len(ses.files))+' files')
