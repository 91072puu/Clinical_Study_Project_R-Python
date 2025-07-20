
# ---------------------------------------------------
# This notebook is for practicing creating ADSL from SDTMs using Python.
# ---------------------------------------------------

# ---------------------------------------------------
# 1. Import libraries
# ---------------------------------------------------
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from helpers.read_and_merge import read_and_merge


# ---------------------------------------------------
# 2. Data Handling - ADSL vars -
# ---------------------------------------------------

# Read data
merged_data = read_and_merge(["dm", "ex", "ds"])

dm = merged_data["dm"]
ex = merged_data["ex"]
ds = merged_data["ds"]


# TRTSDT / TRTEDT
ex['exstdtc_dt'] = pd.to_datetime(ex['EXSTDTC'], errors='coerce')
ex['exendtc_dt'] = pd.to_datetime(ex['EXENDTC'], errors='coerce')

trt_dates = ex.groupby('USUBJID').agg(
    TRTSDT=('exstdtc_dt','min'),
    TRTEDT=('exendtc_dt','max')
).reset_index()

# Merge to DM
adsl_full = pd.merge(dm, trt_dates, on="USUBJID", how="left")

# Rename
adsl_full = adsl_full.rename(columns={'ARM': 'TRT01P', 'ACTARM': 'TRT01A'})

# AGEGRP1
adsl_full['AGEGRP1'] = pd.cut(adsl_full['AGE'],
                              bins=[0, 65, 75, np.inf],
                              labels = ['<65', '65-74', '75+'],
                              include_lowest=True) #if there is 0 years old (not for this data...)

# FASFL
adsl_full['FASFL'] = np.where(adsl_full['TRTSDT'].notna(), 'Y', 'N')

# Final ADSL
adsl_vars = [
    'STUDYID', 'USUBJID', 'SUBJID', 'AGEU', 'AGE', 'AGEGRP1', 
    'SEX', 'RACE', 'TRTSDT', 'TRTEDT', 'TRT01P', 'TRT01A', 'FASFL'
]
ADSL = adsl_full[adsl_vars].copy()

#Duplicate check
assert ADSL['USUBJID'].is_unique, "There are duplicate USUBJID in ADSL!"


# ---------------------------------------------------
# 3. Data checks
# ---------------------------------------------------

# ### Data checks
#Data checks
#print(ds.head())
#print(dm.columns)
#list(dm.columns)



# Data types
print(ADSL.dtypes)

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

dm['AGE'].hist(bins=20)
plt.xlabel('Age')
plt.ylabel('Count')
plt.title('Age Distribution')
plt.show()

# ---------------------------------------------------
# 4. Save as CSV 
# ---------------------------------------------------
script_dir = os.path.dirname(__file__)
ADSL.to_csv(os.path.join(script_dir, "adsl.csv"), index=False)


