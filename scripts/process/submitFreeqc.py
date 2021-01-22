### This script submits qsub jobs calling the singularity container for freeqc,
### and creates the output directory structure for freeqc on PMACS. This is done
### specifically with Kosha's freesurfer output, which was run outside of fMRIPrep,
### and does not have the BIDS compliant session labels. As such, the BIDS labels were
### supplied to the freeqc container, but the old ones will be merged in in the
### complete tabulated data.
###
### Ellyn Butler
### January 21, 2021

import os
import shutil
import re
import logging
import pandas as pd

indir = '/project/bbl_projects/nscor/data/processed/T1/freesurfer/'
outdir = '/project/bbl_projects/nscor/data/processed/T1/freeqc/'
subcol = 'sublabel'
freelic = '/project/ExtraLong/data/license.txt'

labels = pd.read_csv('/project/bbl_projects/nscor/data/info/labelmapping.csv') #WAIT TO RUN UNTIL UPDATED

for sublabel in labels['sublabel']:
    if not os.path.exists(outdir+'sub-'+sublabel):
        os.mkdir(outdir+'sub-'+sublabel)
    for seslabel in labels['seslabel'][labels['sublabel'] == sublabel]:
        if not os.path.exists(outdir+'sub-'+sublabel+'/ses-'+seslabel):
            os.mkdir(outdir+'sub-'+sublabel+'/ses-'+seslabel)
        # Is Kosha's directory named by the FW_sublabel? Or FW_seslabel?
        FW_sublabel = labels.loc[(labels['sublabel'] == sublabel) & (labels['seslabel'] == seslabel)]['FW_sublabel'].tolist()[0]
        FW_seslabel = labels.loc[(labels['sublabel'] == sublabel) & (labels['seslabel'] == seslabel)]['FW_seslabel'].tolist()[0]
        if FW_sublabel in os.listdir(indir):
            ses_indir = indir+FW_sublabel
        elif FW_seslabel in os.listdir(indir):
            ses_indir = indir+FW_seslabel
        elif FW_sublabel+'_'+FW_seslabel in os.listdir(indir):
            ses_indir = indir+FW_sublabel+'_'+FW_seslabel
        else:
            os.system('echo sub-'+sublabel+' ses-'+seslabel+' > '+outdir+'unmapableSessions.csv')
        ses_outdir = outdir+'sub-'+sublabel+'/ses-'+seslabel
        cmd = ['SINGULARITYENV_SUBCOL='+subcol, 'SINGULARITYENV_SUBNAME=sub-'+sublabel,
            'SINGULARITYENV_SESNAME=ses-'+seslabel, 'singularity', 'run', '--writable-tmpfs', '--cleanenv',
            '-B', ses_indir+':/input/data', '-B', freelic+':/input/license/license.txt',
            '-B', ses_outdir+':/output', '/project/ExtraLong/images/freeqc_0.0.9.sif']
            #0.0.10 is having a freesurfer license issue, but I did fix the sublabel column
        freeqc_script = ses_outdir+'/freeqc_run.sh'
        os.system('echo '+' '.join(cmd)+' > '+freeqc_script)
        os.system('chmod +x '+freeqc_script)
        os.system('bsub -o '+ses_outdir+'/jobinfo.log '+freeqc_script)


# Don't mount home to singularity
# 1. "singularity run as specific user"
# 2. Fake root
