# utils.py
import pandas as pd
import os

SUPPORTED_EXT = [".csv", ".xls", ".xlsx", ".json"]

def load_dataframe_from_file(path):
    """
    Loads file into pandas DataFrame. Supports CSV, Excel (.xls/.xlsx), JSON.
    Returns DataFrame.
    """
    _, ext = os.path.splitext(path.lower())
    if ext == ".csv":
        return pd.read_csv(path)
    if ext in (".xls", ".xlsx"):
        return pd.read_excel(path)
    if ext == ".json":
        return pd.read_json(path)
    raise ValueError(f"Unsupported file type: {ext}. Supported: {SUPPORTED_EXT}")

def map_columns_case_insensitive(df, required_cols):
    """
    Given a df and a list of required column names (canonical),
    returns a dict mapping canonical->actual column in df (or None)
    """
    df_cols_lower = {c.lower(): c for c in df.columns}
    mapping = {}
    for rc in required_cols:
        lc = rc.lower()
        if lc in df_cols_lower:
            mapping[rc] = df_cols_lower[lc]
        else:
            # try approximate / replace spaces/ dots / underscores
            candidates = {c.lower().replace(".", "").replace(" ", "").replace("_",""): c for c in df.columns}
            key = lc.replace(".", "").replace(" ", "").replace("_","")
            mapping[rc] = candidates.get(key)
    return mapping

def save_dataframe_to_file(df, path):
    """
    Save a pandas DataFrame to CSV / Excel / JSON depending on extension.
    """
    if df is None:
        raise ValueError("DataFrame is None")
    _, ext = os.path.splitext(path.lower())
    if ext == ".csv":
        df.to_csv(path, index=False)
    elif ext in (".xls", ".xlsx"):
        df.to_excel(path, index=False)
    elif ext == ".json":
        df.to_json(path, orient="records", date_format="iso")
    else:
        raise ValueError("Unsupported export extension. Use .csv, .xls/.xlsx or .json")
