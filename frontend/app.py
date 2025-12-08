"""
Air Quality & Health Risk Predictor - Interactive Dashboard
Professional UI/UX with HCI Best Practices + Explainability
"""
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="AQI Predictor Pro",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Professional Color Palette (WCAG AA Compliant)
COLORS = {
    'primary': '#1e3a8a',
    'secondary': '#0ea5e9',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'dark': '#1f2937',
    'light': '#f9fafb',
}

# AQI Colors (Improved for visibility)
AQI_COLORS = {
    'good': '#22c55e',
    'moderate': '#eab308',
    'unhealthy_sensitive': '#f97316',
    'unhealthy': '#ef4444',
    'very_unhealthy': '#a855f7',
    'hazardous': '#7f1d1d'
}

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        letter-spacing: -0.5px;
    }
    
    .subtitle {
        text-align: center;
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        border: 2px solid #e5e7eb;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.3s;
    }
    
    .info-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
    
    .aqi-display {
        text-align: center;
        padding: 3rem 2rem;
        border-radius: 1.5rem;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s;
        position: relative;
        overflow: hidden;
    }
    
    .aqi-value {
        font-size: 5rem;
        font-weight: 800;
        margin: 0;
        line-height: 1;
        position: relative;
        z-index: 1;
    }
    
    .aqi-label {
        font-size: 1.2rem;
        margin-top: 0.5rem;
        font-weight: 600;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    .badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .badge-good { background: #22c55e; color: white; }
    .badge-moderate { background: #eab308; color: #1f2937; }
    .badge-unhealthy-sensitive { background: #f97316; color: white; }
    .badge-unhealthy { background: #ef4444; color: white; }
    .badge-very-unhealthy { background: #a855f7; color: white; }
    .badge-hazardous { background: #7f1d1d; color: white; }
    
    .disclaimer-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 5px solid #f59e0b;
        padding: 1.25rem;
        border-radius: 0.75rem;
        margin-bottom: 2rem;
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
        display: inline-block;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 0.75rem;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
    }
    
    .feature-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1rem;
        border-radius: 0.75rem;
        border-left: 4px solid #667eea;
        margin-bottom: 0.5rem;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def get_aqi_color(aqi):
    """Get color based on AQI value"""
    if aqi <= 50:
        return AQI_COLORS['good']
    elif aqi <= 100:
        return AQI_COLORS['moderate']
    elif aqi <= 150:
        return AQI_COLORS['unhealthy_sensitive']
    elif aqi <= 200:
        return AQI_COLORS['unhealthy']
    elif aqi <= 300:
        return AQI_COLORS['very_unhealthy']
    else:
        return AQI_COLORS['hazardous']

def get_aqi_badge_class(category):
    """Get badge class for AQI category"""
    mapping = {
        "Good": "badge-good",
        "Moderate": "badge-moderate",
        "Unhealthy for Sensitive Groups": "badge-unhealthy-sensitive",
        "Unhealthy": "badge-unhealthy",
        "Very Unhealthy": "badge-very-unhealthy",
        "Hazardous": "badge-hazardous"
    }
    return mapping.get(category, "badge-moderate")

def call_api(endpoint, method="GET", data=None):
    """Call API endpoint with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"⚠️ API Error: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Backend API is not running")
        st.info("💡 Start backend: `python backend/app/main.py`")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timeout")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

# Main App
def main():
    st.markdown('<h1 class="main-header">🌍 Air Quality Intelligence Platform</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">ML-Powered Air Quality Prediction & Health Risk Assessment</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="disclaimer-box">
        <strong>📊 Demo Mode:</strong> Showcasing ML pipeline with XGBoost model trained on historical data from 10 cities.
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("## 🎯 Navigation")
        page = st.radio(
            "",
            ["🏠 Dashboard", "🌆 City Analysis", "📊 Forecast", "🏥 Health Assessment", "🔍 Explainability", "📈 Analytics"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### 🔗 System Status")
        health = call_api("/health")
        if health and health.get("status") == "healthy":
            st.success("✅ Connected")
            st.caption(f"📊 Records: {health.get('test_records', 0):,}")
            if health.get('explainability_loaded'):
                st.caption("🔍 Explainability: Active")
        else:
            st.error("❌ Disconnected")
    
    if page == "🏠 Dashboard":
        home_page()
    elif page == "🌆 City Analysis":
        city_dashboard_page()
    elif page == "📊 Forecast":
        forecast_page()
    elif page == "🏥 Health Assessment":
        health_risk_page()
    elif page == "🔍 Explainability":
        explainability_page()
    elif page == "📈 Analytics":
        statistics_page()

def home_page():
    st.markdown('<h2 class="section-header">Welcome to AQI Intelligence</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h3 style="color: #667eea;">🤖 ML-Powered</h3>
            <p style="color: #6b7280;">XGBoost model trained on 3+ months of historical data</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h3 style="color: #667eea;">🏥 Health Insights</h3>
            <p style="color: #6b7280;">Personalized risk assessments and recommendations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-card">
            <h3 style="color: #667eea;">📊 Trend Analysis</h3>
            <p style="color: #6b7280;">Identify patterns and forecast air quality trends</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown('<h2 class="section-header">📊 Global Overview</h2>', unsafe_allow_html=True)
    
    stats = call_api("/api/stats")
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Average AQI", f"{stats['average_aqi']:.1f}")
        
        with col2:
            st.metric("Cities", stats['cities_count'])
        
        with col3:
            st.metric("Peak AQI", f"{stats['max_aqi']:.0f}")
        
        with col4:
            st.metric("Best AQI", f"{stats['min_aqi']:.0f}")
        
        if 'category_distribution' in stats:
            st.markdown("---")
            categories = stats['category_distribution']
            
            col1, col2 = st.columns([3, 2])
            
            with col1:
                fig = go.Figure(data=[go.Bar(
                    x=list(categories.keys()),
                    y=list(categories.values()),
                    marker=dict(
                        color=[get_aqi_color(25), get_aqi_color(75), get_aqi_color(125), 
                               get_aqi_color(175), get_aqi_color(250), get_aqi_color(400)]
                    ),
                    text=list(categories.values()),
                    textposition='outside'
                )])
                fig.update_layout(
                    title="Records by AQI Category",
                    height=400,
                    template="plotly_white",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[go.Pie(
                    labels=list(categories.keys()),
                    values=list(categories.values()),
                    hole=0.5,
                    marker=dict(
                        colors=[get_aqi_color(25), get_aqi_color(75), get_aqi_color(125),
                               get_aqi_color(175), get_aqi_color(250), get_aqi_color(400)]
                    )
                )])
                fig.update_layout(title="Distribution", height=400, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

def city_dashboard_page():
    st.markdown('<h2 class="section-header">🌆 City Air Quality Analysis</h2>', unsafe_allow_html=True)
    
    cities_data = call_api("/api/cities")
    if not cities_data:
        return
    
    cities = cities_data.get('cities', [])
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_city = st.selectbox("🏙️ Select City", cities)
    
    with col2:
        analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True)
    
    if analyze_btn:
        with st.spinner(f"Analyzing {selected_city}..."):
            data = call_api(f"/api/current/{selected_city.lower()}")
            
            if data:
                st.markdown("---")
                
                col1, col2, col3 = st.columns([2, 2, 3])
                
                with col1:
                    aqi_value = data['aqi']
                    color = get_aqi_color(aqi_value)
                    st.markdown(f"""
                    <div class="aqi-display" style="background: {color}22; border: 3px solid {color};">
                        <h1 class="aqi-value" style="color: {color};">{aqi_value:.0f}</h1>
                        <p class="aqi-label" style="color: {color};">Air Quality Index</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    badge_class = get_aqi_badge_class(data["category"])
                    st.markdown(f"""
                    <div class="info-card" style="text-align: center;">
                        <h3 style="color: #6b7280;">Status</h3>
                        <span class="badge {badge_class}">{data['category']}</span>
                        <h3 style="color: #6b7280; margin-top: 1.5rem;">Risk Level</h3>
                        <p style="font-size: 1.5rem; font-weight: 700; color: {color};">{data['risk_level']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown("### 🎯 Outdoor Activity")
                    st.info(data['outdoor_activity'])
                    
                    st.markdown("### 😷 Mask Recommendation")
                    st.warning(data['mask_recommendation'])
                
                st.markdown("---")
                st.markdown("### 💬 Health Advisory")
                st.info(data['health_message'])
                
                st.markdown("### ✅ Recommendations")
                for i, rec in enumerate(data['recommendations'], 1):
                    with st.expander(f"📌 Recommendation {i}", expanded=(i==1)):
                        st.write(rec)

def forecast_page():
    st.markdown('<h2 class="section-header">📊 Air Quality Forecast</h2>', unsafe_allow_html=True)
    
    cities_data = call_api("/api/cities")
    if not cities_data:
        return
    
    cities = cities_data.get('cities', [])
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        selected_city = st.selectbox("🏙️ Select City", cities, key="forecast_city")
    
    with col2:
        hours = st.slider("⏱️ Hours", 6, 24, 12, step=1)
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        forecast_btn = st.button("📈 Forecast", type="primary", use_container_width=True)
    
    if forecast_btn:
        with st.spinner(f"Generating {hours}-hour forecast..."):
            forecast = call_api(f"/api/forecast/{selected_city.lower()}?hours={hours}")
            
            if forecast:
                df = pd.DataFrame(forecast['forecast'])
                
                # Dynamic title
                st.markdown(f"""
                <div style="text-align: center; margin: 2rem 0;">
                    <h3 style="color: #667eea; font-size: 1.8rem; font-weight: 700;">
                        {hours}-Hour Air Quality Forecast
                    </h3>
                    <p style="color: #6b7280;">{selected_city} • {datetime.now().strftime('%B %d, %Y')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Chart
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df['hour'],
                    y=df['aqi'],
                    mode='lines+markers',
                    line=dict(color='#667eea', width=4),
                    marker=dict(size=10, color=df['aqi'], colorscale=[
                        [0, AQI_COLORS['good']],
                        [0.2, AQI_COLORS['moderate']],
                        [0.4, AQI_COLORS['unhealthy_sensitive']],
                        [0.6, AQI_COLORS['unhealthy']],
                        [0.8, AQI_COLORS['very_unhealthy']],
                        [1, AQI_COLORS['hazardous']]
                    ], showscale=True),
                    fill='tozeroy',
                    hovertemplate='<b>Hour %{x}</b><br>AQI: %{y:.1f}<extra></extra>'
                ))
                
                fig.add_hline(y=50, line_dash="dot", line_color=AQI_COLORS['good'])
                fig.add_hline(y=100, line_dash="dot", line_color=AQI_COLORS['moderate'])
                fig.add_hline(y=150, line_dash="dot", line_color=AQI_COLORS['unhealthy_sensitive'])
                
                fig.update_layout(
                    xaxis_title="Hours from Now",
                    yaxis_title="AQI",
                    height=500,
                    template="plotly_white",
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Best/worst times
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                best_aqi = df.iloc[forecast['best_hour']]['aqi']
                worst_aqi = df.iloc[forecast['worst_hour']]['aqi']
                
                with col1:
                    st.markdown(f"""
                    <div class="info-card" style="border-left: 5px solid {AQI_COLORS['good']};">
                        <h3 style="color: {AQI_COLORS['good']};">✅ Best Time</h3>
                        <p style="font-size: 1.5rem; font-weight: 700;">Hour {forecast['best_hour']}</p>
                        <p style="color: #6b7280;">AQI: {best_aqi:.0f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="info-card" style="border-left: 5px solid {AQI_COLORS['unhealthy']};">
                        <h3 style="color: {AQI_COLORS['unhealthy']};">⚠️ Avoid</h3>
                        <p style="font-size: 1.5rem; font-weight: 700;">Hour {forecast['worst_hour']}</p>
                        <p style="color: #6b7280;">AQI: {worst_aqi:.0f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with st.expander("📋 Hourly Details"):
                    st.dataframe(df[['hour', 'aqi', 'category', 'risk_level']], use_container_width=True, hide_index=True)

def health_risk_page():
    st.markdown('<h2 class="section-header">🏥 Health Risk Assessment</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 AQI Input")
        aqi_input = st.number_input("Enter AQI", 0, 500, 100, 5)
        
        color = get_aqi_color(aqi_input)
        st.markdown(f"""
        <div style="padding: 1rem; background: {color}22; border-left: 5px solid {color}; border-radius: 0.5rem;">
            <p style="margin: 0; color: {color}; font-weight: 600;">Level: {aqi_input}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 👥 Vulnerable Groups")
        groups_data = call_api("/api/vulnerable-groups")
        if groups_data:
            groups = groups_data['vulnerable_groups']
            selected_groups = st.multiselect(
                "Select if applicable",
                groups,
                format_func=lambda x: x.replace('_', ' ').title()
            )
    
    if st.button("🔍 Assess Risk", type="primary", use_container_width=True):
        with st.spinner("Analyzing..."):
            data = {
                "aqi": aqi_input,
                "vulnerable_groups": selected_groups if selected_groups else None
            }
            
            risk = call_api("/api/health-risk", method="POST", data=data)
            
            if risk:
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                
                color = get_aqi_color(risk['aqi'])
                badge_class = get_aqi_badge_class(risk['aqi_category'])
                
                with col1:
                    st.markdown(f"""
                    <div class="aqi-display" style="background: {color}22; border: 2px solid {color}; padding: 2rem;">
                        <h2 style="font-size: 3rem; color: {color};">{risk['aqi']:.0f}</h2>
                        <p>AQI</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="info-card" style="text-align: center;">
                        <h4>Category</h4>
                        <span class="badge {badge_class}">{risk['aqi_category']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="info-card" style="text-align: center;">
                        <h4>Risk Level</h4>
                        <p style="font-size: 1.8rem; font-weight: 700; color: {color};">{risk['risk_level']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.info(risk['health_message'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"**Activity:** {risk['outdoor_activity_level']}")
                with col2:
                    st.warning(f"**Mask:** {risk['mask_recommendation']}")
                
                st.markdown("### ✅ Recommendations")
                for rec in risk['recommendations']:
                    st.write(f"• {rec}")
                
                if risk.get('vulnerable_group_warnings'):
                    st.markdown("### ⚠️ Group Warnings")
                    for group, warning in risk['vulnerable_group_warnings'].items():
                        if warning:
                            with st.expander(f"{group.replace('_', ' ').title()}"):
                                st.warning(warning)

def explainability_page():
    st.markdown('<h2 class="section-header">🔍 Model Explainability</h2>', unsafe_allow_html=True)
    st.markdown("Understand how the AI model makes predictions")
    
    # Check if explainability is available
    metadata = call_api("/api/explainability/metadata")
    
    if not metadata:
        st.warning("⚠️ Explainability features are not available. Run `generate_shap_values.py` first.")
        return
    
    tab1, tab2, tab3 = st.tabs(["📊 Feature Importance", "🏙️ City Explanation", "ℹ️ Model Info"])
    
    # Tab 1: Global Feature Importance
    with tab1:
        st.markdown("### 🎯 What Features Matter Most?")
        st.markdown("These features have the greatest impact on air quality predictions:")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            top_n = st.slider("Show top features", 5, 20, 10)
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            refresh_btn = st.button("🔄 Refresh", type="secondary", use_container_width=True)
        
        importance_data = call_api(f"/api/explainability/feature-importance?top_n={top_n}")
        
        if importance_data:
            # Create horizontal bar chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                y=importance_data['features'][::-1],  # Reverse for better visualization
                x=importance_data['importance_pct'][::-1],
                orientation='h',
                marker=dict(
                    color=importance_data['importance'][::-1],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Importance")
                ),
                text=[f"{x:.1f}%" for x in importance_data['importance_pct'][::-1]],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Importance: %{x:.2f}%<extra></extra>'
            ))
            
            fig.update_layout(
                title=f"Top {top_n} Most Important Features",
                xaxis_title="Importance (%)",
                yaxis_title="Feature",
                height=max(400, top_n * 35),
                template="plotly_white",
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Feature details
            st.markdown("---")
            st.markdown("### 📋 Feature Details")
            
            top_features = call_api(f"/api/explainability/top-features?n={top_n}")
            
            if top_features:
                for i, feature in enumerate(top_features['top_features'], 1):
                    with st.expander(f"#{i} {feature['name'].replace('_', ' ').title()}", expanded=(i <= 3)):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Importance", f"{feature['importance']:.4f}")
                        
                        with col2:
                            st.metric("Contribution", f"{feature['importance_pct']:.2f}%")
                        
                        with col3:
                            st.metric("Rank", f"#{feature['rank']}")
                        
                        st.markdown(f"**Description:** {feature['description']}")
    
    # Tab 2: City-Specific Explanation
    with tab2:
        st.markdown("### 🏙️ Explain Prediction for a City")
        st.markdown("See which features contributed to a specific city's AQI prediction")
        
        cities_data = call_api("/api/cities")
        if cities_data:
            cities = cities_data.get('cities', [])
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                selected_city = st.selectbox("🏙️ Select City", cities, key="explain_city")
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                explain_btn = st.button("🔍 Explain", type="primary", use_container_width=True)
            
            if explain_btn:
                with st.spinner(f"Analyzing {selected_city}..."):
                    explanation = call_api(f"/api/explainability/explain/{selected_city.lower()}")
                    
                    if explanation:
                        st.markdown("---")
                        
                        # Prediction summary
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            aqi_value = explanation['prediction']
                            color = get_aqi_color(aqi_value)
                            st.markdown(f"""
                            <div class="aqi-display" style="background: {color}22; border: 2px solid {color}; padding: 2rem;">
                                <h2 style="font-size: 3rem; color: {color};">{aqi_value:.0f}</h2>
                                <p>Predicted AQI</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            badge_class = get_aqi_badge_class(explanation['aqi_category'])
                            st.markdown(f"""
                            <div class="info-card" style="text-align: center;">
                                <h4>Category</h4>
                                <span class="badge {badge_class}">{explanation['aqi_category']}</span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown(f"""
                            <div class="info-card" style="text-align: center;">
                                <h4>Features Used</h4>
                                <p style="font-size: 2rem; font-weight: 700; color: #667eea;">{explanation['feature_count']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Top contributing features
                        st.markdown("---")
                        st.markdown("### 🔝 Top Contributing Features")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### ⬆️ Increasing AQI")
                            if explanation['top_positive']:
                                for feature in explanation['top_positive'][:5]:
                                    st.markdown(f"""
                                    <div class="feature-card">
                                        <strong>{feature['feature'].replace('_', ' ').title()}</strong><br>
                                        Value: {feature['value']:.2f} • Importance: {feature.get('importance', 0):.4f}
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.info("No positive contributors")
                        
                        with col2:
                            st.markdown("#### ⬇️ Decreasing AQI")
                            if explanation['top_negative']:
                                for feature in explanation['top_negative'][:5]:
                                    st.markdown(f"""
                                    <div class="feature-card" style="border-left-color: #10b981;">
                                        <strong>{feature['feature'].replace('_', ' ').title()}</strong><br>
                                        Value: {feature['value']:.2f} • Importance: {feature.get('importance', 0):.4f}
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.info("No negative contributors")
                        
                        # All features table
                        with st.expander("📋 All Features"):
                            features_df = pd.DataFrame(explanation['top_features'])
                            features_df = features_df.rename(columns={
                                'feature': 'Feature',
                                'value': 'Value',
                                'importance': 'Importance'
                            })
                            st.dataframe(features_df, use_container_width=True, hide_index=True)
    
    # Tab 3: Model Information
    with tab3:
        st.markdown("### ℹ️ Model Information")
        
        if metadata and 'metadata' in metadata:
            meta = metadata['metadata']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="info-card">
                    <h4>📊 Model Type</h4>
                    <p style="font-size: 1.2rem; font-weight: 600; color: #667eea;">{}</p>
                </div>
                """.format(meta.get('model_type', 'N/A')), unsafe_allow_html=True)
                
                st.markdown("""
                <div class="info-card">
                    <h4>🔢 Total Features</h4>
                    <p style="font-size: 1.2rem; font-weight: 600; color: #667eea;">{}</p>
                </div>
                """.format(meta.get('n_features', 'N/A')), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="info-card">
                    <h4>📈 Test Samples</h4>
                    <p style="font-size: 1.2rem; font-weight: 600; color: #667eea;">{:,}</p>
                </div>
                """.format(meta.get('test_samples', 0)), unsafe_allow_html=True)
                
                st.markdown("""
                <div class="info-card">
                    <h4>🔍 Explainer Type</h4>
                    <p style="font-size: 1.2rem; font-weight: 600; color: #667eea;">{}</p>
                </div>
                """.format(meta.get('explainer_type', 'N/A')), unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 🏆 Top 10 Most Important Features")
            
            if 'top_features' in meta:
                top_10 = meta['top_features'][:10]
                for i, feature in enumerate(top_10, 1):
                    st.markdown(f"""
                    <div class="feature-card">
                        <strong>#{i}</strong> {feature.replace('_', ' ').title()}
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 📖 About Explainability")
            st.info("""
            **Model explainability** helps understand how the AI makes predictions:
            
            - **Feature Importance**: Shows which measurements have the most impact
            - **SHAP Values**: Explains individual predictions in detail
            - **Transparency**: Builds trust by showing the decision-making process
            
            This system uses gradient boosting feature importance to rank the contribution 
            of each environmental factor to air quality predictions.
            """)

def statistics_page():
    st.markdown('<h2 class="section-header">📈 Analytics</h2>', unsafe_allow_html=True)
    
    stats = call_api("/api/stats")
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total", f"{stats['total_predictions']:,}")
        with col2:
            st.metric("Avg AQI", f"{stats['average_aqi']:.1f}")
        with col3:
            st.metric("Max AQI", f"{stats['max_aqi']:.0f}")
        with col4:
            st.metric("Cities", stats['cities_count'])
        
        if 'category_distribution' in stats:
            st.markdown("---")
            categories = stats['category_distribution']
            
            col1, col2 = st.columns([3, 2])
            
            with col1:
                fig = go.Figure(data=[go.Bar(
                    y=list(categories.keys()),
                    x=list(categories.values()),
                    orientation='h',
                    marker=dict(color=[get_aqi_color(25), get_aqi_color(75), get_aqi_color(125),
                                      get_aqi_color(175), get_aqi_color(250), get_aqi_color(400)])
                )])
                fig.update_layout(title="Category Distribution", height=400, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure(data=[go.Pie(
                    labels=list(categories.keys()),
                    values=list(categories.values()),
                    hole=0.6,
                    marker=dict(colors=[get_aqi_color(25), get_aqi_color(75), get_aqi_color(125),
                                       get_aqi_color(175), get_aqi_color(250), get_aqi_color(400)])
                )])
                fig.update_layout(title="Percentages", height=400, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📊 Statistics")
        stats_df = pd.DataFrame([
            {"Metric": "Total Predictions", "Value": f"{stats['total_predictions']:,}"},
            {"Metric": "Average AQI", "Value": f"{stats['average_aqi']:.2f}"},
            {"Metric": "Median AQI", "Value": f"{stats['median_aqi']:.2f}"},
            {"Metric": "Maximum AQI", "Value": f"{stats['max_aqi']:.2f}"},
            {"Metric": "Minimum AQI", "Value": f"{stats['min_aqi']:.2f}"},
            {"Metric": "Cities", "Value": str(stats['cities_count'])}
        ])
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

# Run app
if __name__ == "__main__":
    main()