import pandas as pd

def load_incident_data(file_path: str) -> pd.DataFrame:
    """
    Load the raw incident event log CSV file into a pandas DataFrame.
    
    Args:
        file_path (str): Path to the raw CSV file.
        
    Returns:
        pd.DataFrame: The loaded data.
    """
    return pd.read_csv(file_path)

if __name__ == "__main__":
    df = load_incident_data('data/raw/incident_event_log.csv')
    print(f"Loaded dataset with shape: {df.shape}")
