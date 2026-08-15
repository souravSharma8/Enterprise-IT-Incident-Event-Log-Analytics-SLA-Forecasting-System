import pandas as pd
from typing import Tuple

def split_chronologically(df: pd.DataFrame, incidents_full_path: str = 'data/processed/incidents_full.csv', fraction: float = 0.8) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits the incidents_at_creation dataset chronologically into train and test sets.
    Uses 'opened_at' from incidents_full.csv for sorting.
    """
    # Load full incidents to get 'opened_at'
    full_df = pd.read_csv(incidents_full_path, usecols=['number', 'opened_at'])
    full_df['opened_at'] = pd.to_datetime(full_df['opened_at'], format='%d/%m/%Y %H:%M', errors='coerce')
    
    # Merge opened_at into our modeling dataframe
    df_merged = df.merge(full_df, on='number', how='left')
    
    # Sort chronologically
    df_sorted = df_merged.sort_values('opened_at').reset_index(drop=True)
    
    # Drop 'opened_at' since it's not a modeling feature
    df_sorted = df_sorted.drop(columns=['opened_at'])
    
    # Split based on fraction
    split_idx = int(len(df_sorted) * fraction)
    train_df = df_sorted.iloc[:split_idx].copy()
    test_df = df_sorted.iloc[split_idx:].copy()
    
    return train_df, test_df

if __name__ == "__main__":
    df = pd.read_csv('data/processed/incidents_at_creation.csv')
    train, test = split_chronologically(df)
    print(f"Train size: {len(train)}, Test size: {len(test)}")
