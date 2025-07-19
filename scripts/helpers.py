# Read XPT file
def read_xpt(filename):
    return pd.read_sas(filename, format="xport", encoding="utf-8")

# Decode byte columns to string
def decode_byte_columns(df):
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].apply(lambda x: x.decode("utf-8") if isinstance(x, bytes) else x)
    return df


