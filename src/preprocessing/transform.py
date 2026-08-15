import pandas as pd
import os

def transform_events_to_incidents(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms the event-level log into an incident-level log.
    Groups events by 'number'.
    Extracts the first event for creation-time state.
    Extracts the last event for final/resolved state (prefixed with 'final_').
    """
    # Ensure it's sorted chronologically by sys_updated_at
    # If sys_updated_at is missing, fallback to preserving original order 
    # (which might be chronologically grouped but we sort to be safe)
    if 'sys_updated_at' in df.columns:
        df_sorted = df.sort_values(by=['number', 'sys_updated_at'])
    else:
        df_sorted = df.copy()

    # Get the first event for each incident
    df_first = df_sorted.groupby('number', as_index=False).first()
    
    # Get the last event for each incident
    df_last = df_sorted.groupby('number', as_index=False).last()
    
    # Prefix columns for the last event with 'final_' (except 'number')
    rename_dict = {col: f'final_{col}' for col in df_last.columns if col != 'number'}
    df_last = df_last.rename(columns=rename_dict)
    
    # Merge the first and last events on 'number'
    incidents_full = pd.merge(df_first, df_last, on='number', how='inner')
    
    return incidents_full

if __name__ == "__main__":
    from src.data.load_data import load_incident_data
    from src.preprocessing.clean import clean_data
    
    df = load_incident_data('data/raw/incident_event_log.csv')
    df_clean = clean_data(df)
    
    incidents_full = transform_events_to_incidents(df_clean)
    
    os.makedirs('data/processed', exist_ok=True)
    incidents_full.to_csv('data/processed/incidents_full.csv', index=False)
    print(f"Saved incidents_full.csv with shape: {incidents_full.shape}")
