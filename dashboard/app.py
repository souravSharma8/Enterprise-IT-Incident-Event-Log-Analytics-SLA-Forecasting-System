import streamlit as st
from dashboard.api_client import get_analytics, predict_incident, get_similar_incidents
from dashboard.charts import plot_volume_over_time, plot_distribution, plot_sla_pie

st.set_page_config(page_title="IT Incident Intelligence", layout="wide")

st.title("IT Incident Intelligence System")

# Fetch analytics data once
@st.cache_data(ttl=300)
def load_analytics():
    try:
        return get_analytics()
    except Exception as e:
        st.error(f"Failed to fetch analytics from API: {e}")
        return None

analytics_data = load_analytics()

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Incident Analytics", "SLA Analytics", "Prediction & Similarity"])

if analytics_data:
    # Tab 1: Overview
    with tab1:
        st.header("System Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        total_incidents = analytics_data.get('total_incidents', 0)
        avg_res = analytics_data.get('average_resolution_hours', 0)
        
        sla_counts = {item['made_sla']: item['count'] for item in analytics_data.get('sla_counts', [])}
        sla_met = sla_counts.get(True, 0)
        sla_breached = sla_counts.get(False, 0)
        
        col1.metric("Total Incidents", total_incidents)
        col2.metric("SLA Met", sla_met)
        col3.metric("SLA Breached", sla_breached)
        col4.metric("Avg Resolution (Hrs)", f"{avg_res:.1f}" if avg_res else "N/A")

    # Tab 2: Incident Analytics
    with tab2:
        st.header("Incident Analytics")
        st.plotly_chart(plot_volume_over_time(analytics_data.get('volume_over_time', [])), use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(plot_distribution(analytics_data.get('category_dist', []), 'category', "Top Categories"), use_container_width=True)
            st.plotly_chart(plot_distribution(analytics_data.get('impact_dist', []), 'impact', "Impact Distribution"), use_container_width=True)
            st.plotly_chart(plot_distribution(analytics_data.get('assignment_dist', []), 'assignment_group', "Top Assignment Groups"), use_container_width=True)
        with col2:
            st.plotly_chart(plot_distribution(analytics_data.get('subcategory_dist', []), 'subcategory', "Top Subcategories"), use_container_width=True)
            st.plotly_chart(plot_distribution(analytics_data.get('urgency_dist', []), 'urgency', "Urgency Distribution"), use_container_width=True)
            st.plotly_chart(plot_distribution(analytics_data.get('location_dist', []), 'location', "Top Locations"), use_container_width=True)

    # Tab 3: SLA Analytics
    with tab3:
        st.header("SLA Analytics")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(plot_sla_pie(analytics_data.get('sla_counts', [])), use_container_width=True)

# Tab 4: Prediction
with tab4:
    st.header("Predict SLA & Find Similar Incidents")
    
    with st.form("predict_form"):
        col1, col2 = st.columns(2)
        with col1:
            contact_type = st.selectbox("Contact Type", ["Phone", "Email", "Self service", "Direct opening", "Missing"])
            category = st.text_input("Category", "Software")
            subcategory = st.text_input("Subcategory", "OS")
            u_symptom = st.text_input("Symptom", "Crash")
            location = st.text_input("Location", "Location 1")
        with col2:
            impact = st.selectbox("Impact", ["1 - High", "2 - Medium", "3 - Low", "Missing"])
            urgency = st.selectbox("Urgency", ["1 - High", "2 - Medium", "3 - Low", "Missing"])
            assignment_group = st.text_input("Assignment Group", "Group 1")
            opened_hour = st.number_input("Opened Hour (0-23)", min_value=0, max_value=23, value=9)
            day_of_week = st.number_input("Day of Week (0-6)", min_value=0, max_value=6, value=0)
            month = st.number_input("Month (1-12)", min_value=1, max_value=12, value=1)
            
        submitted = st.form_submit_button("Predict & Find")
        
    if submitted:
        payload = {
            "contact_type": contact_type,
            "category": category,
            "subcategory": subcategory,
            "u_symptom": u_symptom,
            "impact": impact,
            "urgency": urgency,
            "location": location,
            "assignment_group": assignment_group,
            "opened_hour": opened_hour,
            "day_of_week": day_of_week,
            "month": month
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Prediction Results")
            try:
                pred_res = predict_incident(payload)
                risk_level = pred_res['risk_level']
                color = "green" if risk_level == "LOW" else "orange" if risk_level == "MEDIUM" else "red"
                
                st.markdown(f"**SLA Breach Risk:** <span style='color:{color}'>{pred_res['sla_breach_probability']*100:.1f}% ({risk_level})</span>", unsafe_allow_html=True)
                st.markdown(f"**Est. Resolution Time:** {pred_res['estimated_resolution_hours']:.1f} hours")
            except Exception as e:
                st.error(f"Prediction failed: {e}")
                
        with col2:
            st.subheader("Similar Historical Incidents")
            try:
                sim_res = get_similar_incidents(payload)
                st.table(sim_res)
            except Exception as e:
                st.error(f"Similarity search failed: {e}")
