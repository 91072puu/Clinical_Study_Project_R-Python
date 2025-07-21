
# ---------------------------------------------------
# This script is for practicing creating ADSL from SDTMs using Python.
# ---------------------------------------------------

# ---------------------------------------------------
# 1. Import libraries
# ---------------------------------------------------
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from helpers.read_and_merge import read_and_merge
from helpers.ADAM_useful_functions import rename_sdtm_var



# ---------------------------------------------------
# 2. Data Handling - ADSL vars -
# ---------------------------------------------------

# Read data
merged_data = read_and_merge(["DM", "EX", "DS"])

dm = merged_data["DM"]
ex = merged_data["EX"]
ds = merged_data["DS"]



# ----------------------------
# 2.1 SDTM.EX data handling
# ----------------------------

# TRTSDT / TRTEDT
ex['exstdtc_dt'] = pd.to_datetime(ex['EXSTDTC'], errors='coerce')
ex['exendtc_dt'] = pd.to_datetime(ex['EXENDTC'], errors='coerce')

trt_dates = ex.groupby('USUBJID').agg(
    TRTSDT=('exstdtc_dt','min'),
    TRTEDT=('exendtc_dt','max')
).reset_index()

# Merge to DM
adsl_full = pd.merge(dm, trt_dates, on="USUBJID", how="left")



# ----------------------------
# 2.2 SDTM.DS data handling
# ----------------------------
# Derive EOSSTT
ds_disp = ds[ds['DSCAT'] == 'DISPOSITION EVENT'].copy()
eos_map = {
    'COMPLETED': 'COMPLETED',
    'ADVERSE EVENT': 'DISCONTINUED',
    'WITHDRAWAL BY SUBJECT': 'DISCONTINUED',
    'LOST TO FOLLOW-UP': 'DISCONTINUED',
    'DEATH': 'COMPLETED'
}
ds_disp['EOSSTT'] = ds_disp['DSDECOD'].map(eos_map)

print(ds_disp['DSDECOD'].unique())

# Drop duplicates
ds_eos = ds_disp[['USUBJID', 'EOSSTT']].drop_duplicates(subset='USUBJID')

# Merge DS vars to adsl_full
adsl_full = pd.merge(adsl_full, ds_eos, on="USUBJID", how="left")

# Duplicate checks
#before = ds_disp['USUBJID'].nunique()  
#after = ds_eos['USUBJID'].nunique()
#print(f"Before drop_duplicates: {before}, After: {after}")



# ----------------------------
# 2.3 SDTM.DM data handling
# ----------------------------

# TRT01P and TRT01A Rename ARM/ACTARM
adsl_full = adsl_full.rename(columns={'ARM': 'TRT01P', 'ACTARM': 'TRT01A'})

#TRT01AN/TRT01PN
mapping = {
    'Xanomeline High Dose': 1,
    'Xanomeline Low Dose': 2,
    'Placebo': 3,
    'Screen Failure': 99
}

adsl_full['TRT01AN'] = adsl_full['TRT01A'].map(mapping)
adsl_full['TRT01PN'] = adsl_full['TRT01P'].map(mapping)


# AGEGRP1
adsl_full['AGEGRP1'] = pd.cut(adsl_full['AGE'],
                              bins=[0, 65, 75, np.inf],
                              labels = ['<65', '65-74', '75+'], 
                              include_lowest=True) #if there is 0 years old (not for this data...)

# FASFL - as no randomization date 
adsl_full['FASFL'] = np.where(adsl_full['TRTSDT'].notna(), 'Y', 'N')

# Flags set to SUPPDM values - looks like we can use rename for this study
rename_map = {'SAFETY': 'SAFFL', 'ITT': 'ITTFL', 'EFFICACY': 'EFFFL', 
            'COMPLT8':'COMPFL8','COMPLT16':'COMPFL16','COMPLT24':'COMPFL24'}

adsl_full = rename_sdtm_var(adsl_full, rename_map,fill_value='N')


# ---------------------------------------------------
# 3. Output ADSL
# ---------------------------------------------------

# Define variable names
adsl_vars = [
    'STUDYID', 'USUBJID', 'SUBJID', 'AGE', 'AGEU', 'AGEGRP1', 
    'SEX', 'RACE', 'TRTSDT', 'TRTEDT', 'TRT01P', 'TRT01PN', 'TRT01A', 'TRT01AN', 
    'FASFL', 'SAFFL', 'ITTFL', 'EFFFL', 'COMPFL8', 'COMPFL16','COMPFL24',
    'EOSSTT'
]

# Create ADSL
ADSL = adsl_full[adsl_vars].copy()

#Duplicate check
assert ADSL['USUBJID'].is_unique, "There are duplicate USUBJID in ADSL!"



# ---------------------------------------------------
# 4. Save as CSV 
# ---------------------------------------------------
script_dir = os.path.dirname(__file__)
ADSL.to_csv(os.path.join(script_dir, "adsl.csv"), index=False)
ds.to_csv(os.path.join(script_dir, "ds.csv"), index=False)
dm.to_csv(os.path.join(script_dir, "dm.csv"), index=False)




# ---------------------------------------------------
# 5. Random notes for Data checks
# ---------------------------------------------------

# ### Data checks
#Data checks
#print(ADSL.head())
#print(ADSL.columns)
#list(dm.columns)


# Data types
#print(ADSL.dtypes)

# Check missing values
#print(adsl.isnull().sum())

# Check unique values
#print(suppdm['QNAM'].unique())
#print(adsl['RACE'].unique())

# Check summary stats
#print(adsl.describe())

# Check value counts by categories
#print(adsl['AGEGRP1'].value_counts())

#Descriptive stat.
#print(dm['AGE'].describe())

#histogram

#dm['AGE'].hist(bins=20)
#plt.xlabel('Age')
#plt.ylabel('Count')
#plt.title('Age Distribution')
#plt.show()




