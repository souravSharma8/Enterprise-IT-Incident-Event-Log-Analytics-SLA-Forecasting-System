import pandas as pd
import numpy as np
from src.preprocessing.clean import clean_data
from src.preprocessing.transform import transform_events_to_incidents
from src.features.creation_features import create_modeling_dataset

def test_clean_data_replaces_question_marks():
    df = pd.DataFrame({
        'number': ['INC001'],
        'assignment_group': ['?'],
        'opened_at': ['15/08/2026 10:00']
    })
    
    cleaned = clean_data(df)
    
    assert pd.isna(cleaned.loc[0, 'assignment_group'])

def test_transform_groups_events_and_extracts_correctly():
    df = pd.DataFrame({
        'number': ['INC001', 'INC001', 'INC001'],
        'sys_updated_at': ['15/08/2026 10:00', '15/08/2026 11:00', '15/08/2026 12:00'],
        'incident_state': ['New', 'Active', 'Resolved'],
        'made_sla': [True, True, False]
    })
    
    # Needs to be proper datetime for proper sorting if using sys_updated_at for sorting
    df['sys_updated_at'] = pd.to_datetime(df['sys_updated_at'], format='%d/%m/%Y %H:%M')
    
    incidents = transform_events_to_incidents(df)
    
    assert len(incidents) == 1
    # First event values
    assert incidents.loc[0, 'incident_state'] == 'New'
    # Last event values
    assert incidents.loc[0, 'final_incident_state'] == 'Resolved'
    assert incidents.loc[0, 'final_made_sla'] == False

def test_no_leakage_columns_in_creation_features():
    df = pd.DataFrame({
        'number': ['INC001', 'INC001'],
        'sys_updated_at': ['15/08/2026 10:00', '15/08/2026 12:00'],
        'category': ['Software', 'Hardware'],
        'incident_state': ['New', 'Resolved'],
        'opened_at': ['15/08/2026 09:00', '15/08/2026 09:00'],
        'resolved_at': [np.nan, '15/08/2026 12:00'],
        'made_sla': [True, False]
    })
    
    df['sys_updated_at'] = pd.to_datetime(df['sys_updated_at'], format='%d/%m/%Y %H:%M')
    df['opened_at'] = pd.to_datetime(df['opened_at'], format='%d/%m/%Y %H:%M')
    df['resolved_at'] = pd.to_datetime(df['resolved_at'], format='%d/%m/%Y %H:%M')
    
    incidents = transform_events_to_incidents(df)
    features = create_modeling_dataset(incidents)
    
    assert 'incident_state' not in features.columns
    assert 'final_incident_state' not in features.columns
    assert 'category' in features.columns
    assert 'target_made_sla' in features.columns
    assert 'target_resolution_time_hours' in features.columns
    
    assert features.loc[0, 'category'] == 'Software'  # Picked from first event
    assert features.loc[0, 'target_made_sla'] == False # Picked from last event
    assert features.loc[0, 'target_resolution_time_hours'] == 3.0 # 12:00 - 09:00
