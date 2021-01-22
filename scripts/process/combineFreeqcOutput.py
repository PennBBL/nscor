### This script combines each type of freeqc output into a csv
###
### Ellyn Butler
### January 21, 2021

import glob
import csv
import pandas as pd
from datetime import datetime


datatypes = ['aparc_area_lh', 'aparc_area_rh', 'aparc_meancurv_lh', 'aparc_meancurv_rh',
    'aparc_thickness_lh', 'aparc_thickness_rh', 'aparc_volume_lh', 'aparc_volume_rh',
    'aseg_stats', 'lh_a2009s_area', 'lh_a2009s_meancurv', 'lh_a2009s_thickness',
    'lh_a2009s_volume', 'lh_DKTatlas_area', 'lh_DKTatlas_meancurv', 'lh_DKTatlas_thickness',
    'lh_DKTatlas_volume', 'quality', 'rh_a2009s_area', 'rh_a2009s_meancurv',
    'rh_a2009s_thickness', 'rh_a2009s_volume', 'rh_DKTatlas_area', 'rh_DKTatlas_meancurv',
    'rh_DKTatlas_thickness', 'rh_DKTatlas_volume', 'wmparc_stats']

basedir = '/project/bbl_projects/nscor/data/processed/T1'
for datatype in datatypes:
    files = glob.glob(basedir+'/freeqc/sub*/ses*/*'+datatype+'.csv')
    df = pd.concat((pd.read_csv(f, header = 0) for f in files))
    if 'bblid' not in df.columns:
        df = df.rename(columns={'/scripts/idcols.py':'bblid'})
    df.to_csv(basedir+'/tabulated/'+datatype+'_'+datetime.today().strftime('%Y-%m-%d')+'.csv', index=False)
