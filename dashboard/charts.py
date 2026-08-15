import plotly.express as px
import pandas as pd

def plot_volume_over_time(volume_data):
    df = pd.DataFrame(volume_data)
    if df.empty:
        return px.line(title="Incident Volume Over Time")
    fig = px.line(df, x='month', y='count', title="Incident Volume Over Time", markers=True)
    return fig

def plot_distribution(dist_data, x_col, title):
    df = pd.DataFrame(dist_data)
    if df.empty:
        return px.bar(title=title)
    df = df.sort_values('count', ascending=False).head(15) # Top 15
    fig = px.bar(df, x=x_col, y='count', title=title)
    return fig

def plot_sla_pie(sla_data):
    df = pd.DataFrame(sla_data)
    if df.empty:
        return px.pie(title="SLA Breakdown")
    df['made_sla_label'] = df['made_sla'].map({True: 'Met', False: 'Breached'})
    fig = px.pie(df, values='count', names='made_sla_label', title="SLA Breakdown", color='made_sla_label', color_discrete_map={'Met':'#2ecc71', 'Breached':'#e74c3c'})
    return fig
