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
import pandas as pd
import pytz
import datetime
import zipfile
import numpy as np



#outdir = '/Users/butellyn/Documents/nscor/data/raw/'
outdir = '/project/nscor/data/raw/' # Path on PMACS

fw = flywheel.Client()
proj = fw.lookup('bbl/NASA_821559')
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
        sesdir = outdir+'sub-'+sublabel+'/ses-'+seslabel
        if not os.path.exists(sesdir):
            os.mkdir(sesdir)
        # Check if output directory is empty
        # if so, download the session zip and unzip it
        if len(os.listdir(sesdir)) == 0:
            if len(ses.files) > 0:
                for file in ses.files:
                    filename = file['name']
                    ses.download_file(filename, sesdir+filename)
                    # Unzip files
                    with zipfile.ZipFile(sesdir+filename,"r") as zip_ref:
                        zip_ref.extractall(sesdir)
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
