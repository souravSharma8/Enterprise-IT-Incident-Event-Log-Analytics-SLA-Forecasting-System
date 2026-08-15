import pandas as pd
from src.db.connection import get_engine

def load_data_to_mysql():
    """
    Reads the processed CSVs and loads them into MySQL idempotently.
    Uses 'replace' or handles duplicates naively as per prompt scope.
    """
    engine = get_engine()

    print("Loading incidents_full.csv...")
    try:
        # Load the incidents (which contains creation and final states)
        df_full = pd.read_csv('data/processed/incidents_full.csv', parse_dates=['opened_at', 'final_resolved_at', 'final_closed_at'])
        
        # Prepare incidents table DataFrame
        incidents_df = pd.DataFrame({
            'incident_id': df_full['number'],
            'opened_at': df_full['opened_at'],
            'contact_type': df_full['contact_type'],
            'location': df_full['location'],
            'category': df_full['category'],
            'subcategory': df_full['subcategory'],
            'symptom': df_full['u_symptom'],
            'impact': df_full['impact'],
            'urgency': df_full['urgency'],
            'priority': df_full['priority'],
            'caller_id': df_full['caller_id'],
            'opened_by': df_full['opened_by'],
            'assignment_group': df_full['assignment_group'],
            'assigned_to': df_full['assigned_to'],
            'resolved_at': df_full['final_resolved_at'],
            'closed_at': df_full['final_closed_at'],
            'made_sla': df_full['final_made_sla'],
            # Derive resolution_time_hours if missing from full df, though we calculated it in features
            'resolution_time_hours': (df_full['final_resolved_at'] - df_full['opened_at']).dt.total_seconds() / 3600.0
        })
        
        # Truncate and replace
        print("Inserting into 'incidents' table...")
        incidents_df.to_sql('incidents', con=engine, if_exists='replace', index=False)
        print("Inserted incidents.")
        
    except FileNotFoundError:
        print("incidents_full.csv not found. Skipping main incidents table load.")

    print("Loading incident_event_log.csv for events history...")
    try:
        # Load the event log
        df_events = pd.read_csv('data/raw/incident_event_log.csv')
        df_events.replace('?', None, inplace=True)
        
        events_df = pd.DataFrame({
            'incident_id': df_events['number'],
            'event_timestamp': pd.to_datetime(df_events['sys_updated_at'], format='%d/%m/%Y %H:%M', errors='coerce'),
            'incident_state': df_events['incident_state'],
            'active': df_events['active'],
            'reassignment_count': pd.to_numeric(df_events['reassignment_count'], errors='coerce'),
            'reopen_count': pd.to_numeric(df_events['reopen_count'], errors='coerce'),
            'sys_mod_count': pd.to_numeric(df_events['sys_mod_count'], errors='coerce'),
            'assignment_group': df_events['assignment_group'],
            'assigned_to': df_events['assigned_to']
        })
        
        print("Inserting into 'incident_events' table...")
        # Since to_sql('replace') drops the table, we'd lose auto_increment PKs if we rely strictly on schema.sql
        # But for this simple implementation, replacing the table structure via pandas is pragmatic.
        events_df.to_sql('incident_events', con=engine, if_exists='replace', index_label='event_id')
        print("Inserted incident events.")
        
    except FileNotFoundError:
        print("incident_event_log.csv not found. Skipping events table load.")

if __name__ == "__main__":
    load_data_to_mysql()
