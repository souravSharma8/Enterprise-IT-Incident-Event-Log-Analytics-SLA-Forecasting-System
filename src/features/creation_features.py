import pandas as pd
import os

def create_modeling_dataset(incidents_full: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts features available ONLY at incident creation to prevent data leakage.
    Adds two ML targets: 'made_sla' and 'resolution_time_hours'.
    """
    # Define columns that are safe to use as features
    # 'assignment_group' and 'assigned_to' are included but will contain nulls if 
    # unassigned at creation.
    feature_cols = [
        'number', 'contact_type', 'location', 'category', 'subcategory', 
        'u_symptom', 'impact', 'urgency', 'priority', 'caller_id', 
        'opened_by', 'assignment_group', 'assigned_to', 'opened_at'
    ]
    
    # Ensure columns exist before selecting
    available_features = [col for col in feature_cols if col in incidents_full.columns]
    
    # Select features
    features_df = incidents_full[available_features].copy()
    
    # Derive time features from opened_at
    if 'opened_at' in features_df.columns:
        features_df['opened_hour'] = features_df['opened_at'].dt.hour
        features_df['day_of_week'] = features_df['opened_at'].dt.dayofweek
        features_df['month'] = features_df['opened_at'].dt.month
        # Drop 'opened_at' if you don't want a datetime object in the final features
        # (Usually models prefer the extracted components)
        features_df = features_df.drop(columns=['opened_at'])
        
    # Add targets
    # 1. Classification target: made_sla (from the final state)
    if 'final_made_sla' in incidents_full.columns:
        features_df['target_made_sla'] = incidents_full['final_made_sla']
        
    # 2. Regression target: resolution_time_hours (from final_resolved_at - opened_at)
    if 'final_resolved_at' in incidents_full.columns and 'opened_at' in incidents_full.columns:
        res_time = incidents_full['final_resolved_at'] - incidents_full['opened_at']
        features_df['target_resolution_time_hours'] = res_time.dt.total_seconds() / 3600.0
        
    return features_df

if __name__ == "__main__":
    incidents_full = pd.read_csv('data/processed/incidents_full.csv', parse_dates=['opened_at', 'final_resolved_at'])
    
    # If the CSV has 'pd.NA' or NaN as strings, we might need to handle them,
    # but pandas read_csv handles empty strings correctly for floats/dates.
    
    features_df = create_modeling_dataset(incidents_full)
    
    os.makedirs('data/processed', exist_ok=True)
    features_df.to_csv('data/processed/incidents_at_creation.csv', index=False)
    print(f"Saved incidents_at_creation.csv with shape: {features_df.shape}")
