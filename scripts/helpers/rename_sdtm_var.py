
"""
Module: read_and_merge

Functions:
1. rename_sdtm_var
   - Renames SDTM variables based on a mapping dictionary.  
   - Optionally fills missing values in renamed columns (fill_value)
   - Useful for flags and other standard SDTM-derived variables in ADaM.
"""


def rename_sdtm_var(df, rename_map, fill_value=None):
    df = df.rename(columns=rename_map)
    if fill_value is not None:
        for new_col in rename_map.values():
            if new_col in df.columns:
                df[new_col] = df[new_col].fillna(fill_value)
    return df