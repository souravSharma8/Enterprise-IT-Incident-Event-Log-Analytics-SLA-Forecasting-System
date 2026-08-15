import pandas as pd
import numpy as np

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the raw incident event log.
    - Replaces '?' with pd.NA.
    - Converts timestamp columns to datetime.
    - Normalizes string fields by stripping whitespace.
    """
    df_clean = df.copy()
    
    # Replace '?' with NaN
    df_clean.replace('?', pd.NA, inplace=True)
    
    # Convert timestamp columns to datetime
    timestamp_cols = [
        'opened_at', 'sys_created_at', 'sys_updated_at', 
        'resolved_at', 'closed_at'
    ]
    for col in timestamp_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_datetime(df_clean[col], format='%d/%m/%Y %H:%M', errors='coerce')
            
    # Normalize string columns (strip whitespace)
    # Exclude identifiers from normalization just in case
    exclude_cols = ['number', 'sys_id']
    for col in df_clean.select_dtypes(include=['object', 'string']).columns:
        if col not in exclude_cols:
            df_clean[col] = df_clean[col].str.strip()
            
    return df_clean

if __name__ == "__main__":
    from src.data.load_data import load_incident_data
    df = load_incident_data('data/raw/incident_event_log.csv')
    df_clean = clean_data(df)
    print(f"Cleaned dataset. Shape: {df_clean.shape}")
