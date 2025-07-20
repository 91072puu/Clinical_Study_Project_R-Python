
# ## This notebook is for practicing creating ADSL from SDTMs using Python.

# ### Functions to merge Main domain and SUPP 

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read XPT file
def read_xpt(filename):
    return pd.read_sas(filename, format="xport", encoding="utf-8")

# Decode byte columns to string
def decode_byte_columns(df):
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].apply(lambda x: x.decode("utf-8") if isinstance(x, bytes) else x)
    return df

# Merge main domain and its corresponding SUPP-- dataset
def merge_supp(main_df, supp_df, domain_name):
    if supp_df is None or supp_df.empty:
        return main_df

    supp_df = supp_df[supp_df['RDOMAIN'] == domain_name].copy()

    # if no IDVAR then pivot by USUBJID
    if 'IDVAR' not in supp_df.columns or supp_df['IDVAR'].isna().all() or all(supp_df['IDVAR'].str.strip() == ''):
        supp_pivot = (
            supp_df.pivot_table(index="USUBJID", columns="QNAM", values="QVAL", aggfunc="first")
            .reset_index()
        )
        merged = pd.merge(main_df, supp_pivot, on="USUBJID", how="left")
    else:
        # pivot by USUBJID IDVAR
        merged = main_df.copy()
        for idvar in supp_df['IDVAR'].dropna().unique():
            if idvar.strip() == "":
                continue

            temp = supp_df[supp_df['IDVAR'] == idvar].copy()

            if idvar in main_df.columns:
                temp["IDVARVAL"] = temp["IDVARVAL"].astype(main_df[idvar].dtype)

            temp = temp.rename(columns={"IDVARVAL": idvar})

            supp_pivot = (
                temp.pivot_table(index=["USUBJID", idvar], columns="QNAM", values="QVAL", aggfunc="first")
                .reset_index()
            )
            merged = pd.merge(merged, supp_pivot, on=["USUBJID", idvar], how="left")

    return merged

# Main function to read and merge SDTMs and SUPP--
def read_and_merge(domains):
    dataframes = {}
    supp_domains = {}

    for domain in domains:
        main_df = decode_byte_columns(read_xpt(f"{domain}.xpt"))
        dataframes[domain] = main_df

        supp_file = f"SUPP{domain}.xpt"
        try:
            supp_df = decode_byte_columns(read_xpt(supp_file))
            supp_domains[domain] = supp_df
        except FileNotFoundError:
            supp_domains[domain] = None

    for domain in domains:
        supp_df = supp_domains.get(domain)
        if supp_df is not None and not supp_df.empty:
            dataframes[domain] = merge_supp(dataframes[domain], supp_df, domain_name=domain)

    return dataframes



# ### Creating ADSL vars

# In[9]:


# Read data
domains = ["DM", "EX", "DS"]
merged_data = read_and_merge(domains)

dm = merged_data["DM"]
ex = merged_data["EX"]
ds = merged_data["DS"]


# TRTSDT / TRTEDT
ex['exstdtc_dt'] = pd.to_datetime(ex['EXSTDTC'], errors='coerce')
ex['exendtc_dt'] = pd.to_datetime(ex['EXENDTC'], errors='coerce')

trt_dates = ex.groupby('USUBJID').agg(
    TRTSDT=('exstdtc_dt','min'),
    TRTEDT=('exendtc_dt','max')
).reset_index()

# Merge to DM
adsl_temp = pd.merge(dm, trt_dates, on="USUBJID", how="left")

# Rename
adsl_temp = adsl_temp.rename(columns={'ARM': 'TRT01P', 'ACTARM': 'TRT01A'})

# AGEGRP1
adsl_temp['AGEGRP1'] = pd.cut(adsl_temp['AGE'],
                              bins=[0, 65, 75, np.inf],
                              labels = ['<65', '65-74', '75+'],
                              include_lowest=True) #if there is 0 years old (not for this data...)

# FASFL
adsl_temp['FASFL'] = np.where(adsl_temp['TRTSDT'].notna(), 'Y', 'N')

# Final ADSL
adsl_vars = [
    'STUDYID', 'USUBJID', 'SUBJID', 'AGEU', 'AGE', 'AGEGRP1', 
    'SEX', 'RACE', 'TRTSDT', 'TRTEDT', 'TRT01P', 'TRT01A', 'FASFL'
]
ADSL = adsl_temp[adsl_vars].copy()

#Duplicate check
assert ADSL['USUBJID'].is_unique, "There are duplicate USUBJID in ADSL!"



# ### Data checks
#Data checks
#print(ds.head())
#print(dm.columns)
#list(dm.columns)



# Data types
#print(adsl.dtypes)

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

