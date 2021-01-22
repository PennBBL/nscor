### This script downloads previously not downloaded raw data from NASA_821559
### on flywheel to PMACS
###
### Ellyn Butler
### January 14, 2021 - January 21, 2021


import subprocess as sub
import os
import flywheel
import json
import shutil
import re
import time
import pandas as pd
#import pytz
import datetime
import zipfile
import numpy as np



#outdir = '/Users/butellyn/Documents/nscor/data/raw/' # path on local computer
#outdir = '/home/butellyn/nscor/data/raw/' # tmp path on PMACS
outdir = '/project/bbl_projects/nscor/data/raw/' # Path on PMACS

fw = flywheel.Client()
proj = fw.lookup('13/NSCOR_831353') #NSCOR_831353
subjects = proj.subjects()

if not os.path.exists(outdir):
    os.mkdir(outdir)

labelmapping = {'FW_sublabel':[], 'FW_seslabel':[], 'sublabel':[], 'seslabel':[], 'date':[]}

for subj in subjects:
    FW_sublabel = subj['label']
    #if FW_sublabel in ['20475', '891296N', '891451N', '891462N']:
    #    break
    sublabel = FW_sublabel.replace('_', '')
    if not os.path.exists(outdir+'sub-'+sublabel):
        os.mkdir(outdir+'sub-'+sublabel)
    for ses in subj.sessions():
        labelmapping['FW_sublabel'].append(FW_sublabel)
        labelmapping['sublabel'].append(sublabel)
        ses = ses.reload()
        FW_seslabel = ses['label']
        labelmapping['FW_seslabel'].append(FW_seslabel)
        # Get which visit this one is
        sesdates = {'FW_seslabel':[], 'date':[]}
        for ses2 in subj.sessions():
            sesdates['FW_seslabel'].append(ses2['label'])
            if not ses2['timestamp'] is None:
                sesdates['date'].append(ses2['timestamp'].date())
            else:
                sesdates['date'].append(None)
        sesdates = pd.DataFrame.from_dict(sesdates)
        # Check if all the dates are there
        # If not, are pre and post in the seslabels?
        # If not, print problematic subject info to txt file
        if not sesdates['date'].isnull().values.any():
            sesdates = sesdates.sort_values(by=['date'])
            sesdates.index = list(range(sesdates.shape[0]))
            visit = sesdates.index[sesdates['FW_seslabel'] == FW_seslabel] + 1
            visit = visit.tolist()[0]
        elif 'Pre' in sesdates['FW_seslabel'][0] or 'Post' in sesdates['FW_seslabel'][0]:
            if 'Pre' in FW_seslabel:
                visit = 1
            else:
                visit = 2
        else:
            os.system('echo sub-'+sublabel+' is missing date and pre/post designation >> '+outdir+'dateinfo.txt')
            break
        seslabel = 'NSCOR' + str(visit)
        labelmapping['seslabel'].append(seslabel)
        if not ses['timestamp'] is None:
            labelmapping['date'].append(ses['timestamp'].date())
        else:
            labelmapping['date'].append(None)
        # Create the session level directory
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
                    # Check if the file is a zip file
                    if zipfile.is_zipfile(sesdir+filename):
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
            else:
                print('sub-'+sublabel+' ses-'+seslabel+' has zero files')
            if len(ses.acquisitions()) > 0:
                for acq in ses.acquisitions(): # January 6, 2020: Files do not include niftis...
                    for file in acq['files']:
                        filename = file['name']
                        acq.download_file(filename, sesdir+filename)
            else:
                print('sub-'+sublabel+' ses-'+seslabel+' has zero acquisitions')
        else:
            print('sub-'+sublabel+' ses-'+seslabel+' has previously downloaded content')

labelmapping_df = pd.DataFrame.from_dict(labelmapping)
labelmapping_df.to_csv('/project/bbl_projects/nscor/data/info/labelmapping.csv', index=False)

# Check the number of files for each subject
for subj in subjects:
    sublabel = subj['label']
    for ses in subj.sessions():
        seslabel = ses['label']
        print('sub-'+sublabel+' ses-'+seslabel+' has '+str(len(ses.files))+' files')
