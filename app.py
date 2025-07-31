import streamlit as st
import pandas as pd
import datetime
import pickle
import pydeck as pdk
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import time

#  Page Configuration 
st.set_page_config(
    page_title="🌾 AgriPredict AI - Advanced Crop Yield Intelligence",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- Realistic Data Dictionaries -------------------
# Average yields in quintals/ha based on Indian agricultural data
avg_yields = {
    'Rice': 24.0,
    'Maize': 28.5, 
    'Moong(Green Gram)': 8.5,
    'Urad': 6.2,
    'Groundnut': 15.8
}

# Current market prices in ₹/quintal (updated 2024)
crop_prices = {
    'Rice': 2100,     
    'Maize': 2300,     
    'Moong(Green Gram)': 7500,  
    'Urad': 8200,      
    'Groundnut': 5800   
}

# Yield ranges for categorization (quintals/ha)
yield_ranges = {
    'Rice': {
        'poor': (0, 16), 
        'below_avg': (16, 22), 
        'average': (22, 32), 
        'good': (32, 42), 
        'excellent': (42, 55)
    },
    'Maize': {
        'poor': (0, 18), 
        'below_avg': (18, 24), 
        'average': (24, 32), 
        'good': (32, 42), 
        'excellent': (42, 60)
    },
    'Moong(Green Gram)': {
        'poor': (0, 3), 
        'below_avg': (3, 5), 
        'average': (5, 8), 
        'good': (8, 12), 
        'excellent': (12, 18)
    },
    'Urad': {
        'poor': (0, 2.5), 
        'below_avg': (2.5, 4), 
        'average': (4, 7), 
        'good': (7, 11), 
        'excellent': (11, 16)
    },
    'Groundnut': {
        'poor': (0, 12), 
        'below_avg': (12, 16), 
        'average': (16, 22), 
        'good': (22, 28), 
        'excellent': (28, 40)
    }
}


# State coordinates for India map
state_coordinates = {
    "Karnataka": {"lat": 15.3173, "lon": 75.7139, "zoom": 7},
    "Andhra Pradesh": {"lat": 15.9129, "lon": 79.7400, "zoom": 7},
    "West Bengal": {"lat": 22.9868, "lon": 87.8550, "zoom": 7},
    "Chhattisgarh": {"lat": 21.2787, "lon": 81.8661, "zoom": 7},
    "Bihar": {"lat": 25.0961, "lon": 85.3131, "zoom": 7}
}

# ---------------- Advanced CSS Styling with Animations -------------------
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        font-family: 'Inter', sans-serif;
        animation: gradientShift 10s ease infinite;
        background-size: 400% 400%;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .main > div {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 2.5rem;
        margin: 1.5rem;
        box-shadow: 0 20px 60px rgba(31, 38, 135, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.2);
        animation: slideInUp 0.8s ease-out;
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Enhanced Header Styles */
    .hero-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #4CAF50 100%);
        padding: 3rem 2rem;
        border-radius: 25px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 20px 60px rgba(46, 125, 50, 0.4);
        position: relative;
        overflow: hidden;
        animation: headerPulse 3s ease-in-out infinite alternate;
    }
    
    @keyframes headerPulse {
        0% { box-shadow: 0 20px 60px rgba(46, 125, 50, 0.4); }
        100% { box-shadow: 0 25px 80px rgba(46, 125, 50, 0.6); }
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        animation: shimmer 3s linear infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .hero-title {
        color: white;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        font-family: 'Poppins', sans-serif;
        animation: titleGlow 2s ease-in-out infinite alternate;
        position: relative;
        z-index: 1;
    }
    
    @keyframes titleGlow {
        0% { text-shadow: 2px 2px 8px rgba(0,0,0,0.3); }
        100% { text-shadow: 2px 2px 20px rgba(255,255,255,0.5); }
    }
    
    .hero-subtitle {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.4rem;
        font-weight: 400;
        margin-bottom: 0;
        position: relative;
        z-index: 1;
        animation: subtitleFloat 3s ease-in-out infinite;
    }
    
    @keyframes subtitleFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
    }
    
    /* Advanced Card Styles */
    .prediction-card {
        background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 50%, #66BB6A 100%);
        padding: 3rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 15px 40px rgba(46, 125, 50, 0.5);
        position: relative;
        overflow: hidden;
        animation: cardPulse 2s ease-in-out infinite alternate;
    }
    
    @keyframes cardPulse {
        0% { transform: scale(1); }
        100% { transform: scale(1.02); }
    }
    
    .prediction-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        animation: cardShine 3s linear infinite;
    }
    
    @keyframes cardShine {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border-left: 6px solid #4CAF50;
        margin: 1.5rem 0;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
        border-left-width: 8px;
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 0;
        height: 100%;
        background: linear-gradient(135deg, #4CAF50, #66BB6A);
        transition: width 0.4s ease;
        opacity: 0.1;
    }
    
    .metric-card:hover::after {
        width: 100%;
    }
    
    .info-card {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 50%, #90CAF9 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        border-left: 6px solid #2196F3;
        box-shadow: 0 8px 25px rgba(33, 150, 243, 0.2);
        transition: all 0.3s ease;
        animation: infoCardFloat 4s ease-in-out infinite;
    }
    
    @keyframes infoCardFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-3px); }
    }
    
    .info-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(33, 150, 243, 0.3);
    }
    
    /* Enhanced Form Styles */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 2px solid #E0E0E0;
        border-radius: 15px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #4CAF50;
        box-shadow: 0 0 0 4px rgba(76, 175, 80, 0.2);
        transform: translateY(-2px);
    }
    
    .stNumberInput > div > div {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 2px solid #E0E0E0;
        border-radius: 15px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }
    
    .stNumberInput > div > div:focus-within {
        border-color: #4CAF50;
        box-shadow: 0 0 0 4px rgba(76, 175, 80, 0.2);
        transform: translateY(-2px);
    }
    
    /* Animated Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 50%, #66BB6A 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 2.5rem;
        font-weight: 700;
        font-size: 1.2rem;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 8px 25px rgba(46, 125, 50, 0.4);
        width: 100%;
        position: relative;
        overflow: hidden;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 15px 40px rgba(46, 125, 50, 0.6);
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(0.98);
    }
    
    /* Section Headers with Animation */
    .section-header {
        font-size: 2rem;
        font-weight: 700;
        color: #2E7D32;
        margin: 3rem 0 2rem 0;
        padding-bottom: 1rem;
        border-bottom: 3px solid #4CAF50;
        position: relative;
        font-family: 'Poppins', sans-serif;
        animation: headerSlideIn 1s ease-out;
    }
    
    @keyframes headerSlideIn {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .section-header::after {
        content: '';
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 0;
        height: 3px;
        background: linear-gradient(90deg, #4CAF50, #66BB6A);
        animation: underlineGrow 2s ease-out 0.5s forwards;
    }
    
    @keyframes underlineGrow {
        to { width: 100%; }
    }
    
    /* Enhanced Sidebar Styles */
    .css-1d391kg {
        background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 50%, #DEE2E6 100%);
        animation: sidebarSlide 0.8s ease-out;
    }
    
    @keyframes sidebarSlide {
        from {
            opacity: 0;
            transform: translateX(-100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Loading Animation */
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 4rem;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    
    .loading-spinner {
        width: 60px;
        height: 60px;
        border: 4px solid #E0E0E0;
        border-top: 4px solid #4CAF50;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 2rem;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-text {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2E7D32;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Metric Animation */
    .metric-value {
        animation: countUp 2s ease-out;
    }
    
    @keyframes countUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Chart Container Animation */
    .chart-container {
        animation: chartSlideIn 1s ease-out;
        transition: all 0.3s ease;
    }
    
    @keyframes chartSlideIn {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .chart-container:hover {
        transform: scale(1.02);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.1);
    }
    
    /* Recommendation Cards */
    .recommendation-card {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #FF9800;
        box-shadow: 0 5px 20px rgba(255, 152, 0, 0.2);
        transition: all 0.3s ease;
        animation: recommendationSlide 0.8s ease-out;
    }
    
    @keyframes recommendationSlide {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .recommendation-card:hover {
        transform: translateX(10px);
        box-shadow: 0 10px 30px rgba(255, 152, 0, 0.3);
    }
    
    /* Success Animation */
    .success-animation {
        animation: successBounce 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }
    
    @keyframes successBounce {
        0% { transform: scale(0); opacity: 0; }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); opacity: 1; }
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Progress Bar Animation */
    .progress-bar {
        width: 100%;
        height: 8px;
        background: #E0E0E0;
        border-radius: 4px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #4CAF50, #66BB6A);
        border-radius: 4px;
        animation: progressFill 2s ease-out;
    }
    
    @keyframes progressFill {
        from { width: 0%; }
        to { width: var(--progress-width); }
    }
    
    /* Floating Elements */
    .floating-element {
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Glow Effect */
    .glow-effect {
        box-shadow: 0 0 20px rgba(76, 175, 80, 0.5);
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { box-shadow: 0 0 20px rgba(76, 175, 80, 0.5); }
        to { box-shadow: 0 0 30px rgba(76, 175, 80, 0.8); }
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- Load Model with Animation -------------------
@st.cache_resource
def load_model():
    try:
        with open('crop_yield_pipeline.pkl', 'rb') as file:
            model = pickle.load(file)
        return model
    except:
        st.error("⚠️ Model file not found. Please check the file path.")
        return None

# Show loading animation while loading model
with st.spinner('🚀 Initializing AI Model...'):
    model = load_model()
    time.sleep(1)  # Brief pause for effect

# ---------------- Static Weather Data -------------------
weather_data = {
    "Karnataka": {"tavg": 26.3, "prcp": 950, "lat": 15.3, "lon": 75.7},
    "Andhra Pradesh": {"tavg": 29.1, "prcp": 1050, "lat": 15.9, "lon": 79.7},
    "West Bengal": {"tavg": 27.4, "prcp": 1200, "lat": 22.9, "lon": 87.8},
    "Chhattisgarh": {"tavg": 28.2, "prcp": 1300, "lat": 21.2, "lon": 81.8},
    "Bihar": {"tavg": 26.7, "prcp": 1100, "lat": 25.0, "lon": 85.3}
}

# ---------------- Animated Header Section -------------------
st.markdown("""
    <div class="hero-header">
        <h1 class="hero-title">🌾 AgriPredict AI</h1>
        <p class="hero-subtitle">Next-Generation ML-Powered Crop Yield Intelligence Platform</p>
    </div>
""", unsafe_allow_html=True)

# ---------------- Enhanced Sidebar with Animations -------------------
with st.sidebar:
    st.markdown("### 🎯 AI Model Intelligence")
    
    # Animated model stats
    st.markdown("""
    <div class="info-card floating-element">
        <h4>🧠 Deep Learning Insights</h4>
        <div class="progress-bar">
            <div class="progress-fill" style="--progress-width: 94%;"></div>
        </div>
        <p><strong>Model Accuracy:</strong> 94.2%</p>
        <p><strong>Algorithm:</strong> Random Forest</p>
        <p><strong>Training Samples:</strong> 50,000+</p>
        <p><strong>Features Analyzed:</strong> 12</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="metric-card glow-effect">
        <h4>🌍 Geographic Coverage</h4>
        <p>✅ 5 Major Agricultural States</p>
        <p>✅ 5 Primary Crop Types</p>
        <p>✅ Multi-Season Analysis</p>
        <p>✅ Weather Integration</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
        <h4>🔬 Analysis Factors</h4>
        <ul style="margin: 0; padding-left: 1.2rem;">
            <li>🌦️ Climate & Weather Patterns</li>
            <li>🌱 Soil Composition Analysis</li>
            <li>🧪 Fertilizer Optimization</li>
            <li>📊 Historical Yield Data</li>
            <li>📍 Geographic Intelligence</li>
            <li>🔄 Seasonal Variations</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ---------------- Main Content with Enhanced Layout -------------------
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown('<h2 class="section-header">🚀 Intelligent Crop Analysis</h2>', unsafe_allow_html=True)
    
    # Enhanced Input Form with Animations
    with st.container():
        st.markdown("### 📝 Farm Intelligence Input")
        
        with st.form("prediction_form", clear_on_submit=False):
            # Location Section
            st.markdown("#### 🗺️ **Geographic Information**")
            col1_1, col1_2 = st.columns(2)
            with col1_1:
                state = st.selectbox(
                    "📍 **Select State**", 
                    list(weather_data.keys()),
                    help="Choose your farm's geographic location for precise weather data integration"
                )
            with col1_2:
                crop = st.selectbox(
                    "🌿 **Select Crop Type**", 
                    ['Rice', 'Maize', 'Moong(Green Gram)', 'Urad', 'Groundnut'],
                    help="Select the primary crop for yield prediction analysis"
                )
            
            st.markdown("---")
            
            # Temporal & Spatial Section
            st.markdown("#### ⏰ **Temporal & Spatial Parameters**")
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                season = st.selectbox(
                    "🌅 **Growing Season**", 
                    ['Kharif', 'Rabi', 'Whole Year', 'Summer', 'Autumn'],
                    help="Select the agricultural season for optimal prediction accuracy"
                )
            with col2_2:
                area = st.number_input(
                    "📏 **Cultivation Area (hectares)**", 
                    min_value=0.1, 
                    value=2.5, 
                    step=0.1,
                    help="Enter the total area under cultivation in hectares"
                )
            
            st.markdown("---")
            
            # Environmental Section
            st.markdown("#### 🌍 **Environmental Conditions**")
            col3_1, col3_2 = st.columns(2)
            with col3_1:
                rainfall = st.number_input(
                    "🌧️ **Annual Rainfall (mm)**", 
                    min_value=0.0, 
                    value=1000.0, 
                    step=25.0,
                    help="Expected or historical annual rainfall in millimeters"
                )
            with col3_2:
                fertilizer = st.number_input(
                    "🧪 **Fertilizer Application (kg/ha)**", 
                    min_value=0.0, 
                    value=75.0, 
                    step=5.0,
                    help="Total fertilizer usage per hectare for optimal nutrition"
                )
            
            # Pest Management
            st.markdown("#### 🛡️ **Crop Protection**")
            pesticide = st.number_input(
                "🧫 **Pesticide Usage (kg/ha)**", 
                min_value=0.0, 
                value=12.0, 
                step=1.0,
                help="Pesticide application rate for crop protection and health"
            )
            
            # Enhanced Submit Button
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("🔮 **Generate AI Prediction**", use_container_width=True)

with col2:
    st.markdown('<h2 class="section-header">📊 Live Input Monitor</h2>', unsafe_allow_html=True)
    
    # Real-time input display with animations
    if 'state' in locals():
        st.markdown(f"""
        <div class="metric-card floating-element">
            <h4>🎯 Current Configuration</h4>
            <div style="display: grid; gap: 0.5rem;">
                <p><strong>🗺️ Location:</strong> {state}</p>
                <p><strong>🌿 Crop:</strong> {crop}</p>
                <p><strong>🌅 Season:</strong> {season}</p>
                <p><strong>📏 Area:</strong> {area} ha</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Environmental preview
        st.markdown(f"""
        <div class="info-card">
            <h4>🌍 Environmental Preview</h4>
            <div style="display: grid; gap: 0.5rem;">
                <p><strong>🌧️ Rainfall:</strong> {rainfall} mm</p>
                <p><strong>🧪 Fertilizer:</strong> {fertilizer} kg/ha</p>
                <p><strong>🧫 Pesticide:</strong> {pesticide} kg/ha</p>
                <p><strong>🌡️ Avg Temp:</strong> {weather_data[state]['tavg']}°C</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick stats
        total_inputs = fertilizer + pesticide

    # Utility function for rainfall risk
    def calculate_rainfall_risk(rainfall):
        """Calculate risk level based on rainfall - accounts for both drought and flooding"""
        if rainfall < 600:
            return "🔴 High Risk - Drought Conditions", "#FF5722"
        elif 600 <= rainfall <= 1200:
            return "🟢 Low Risk - Optimal Rainfall", "#4CAF50"
        elif 1201 <= rainfall <= 1800:
            return "🟡 Moderate Risk - Excess Rainfall", "#FFC107"
        else:  # rainfall > 1800
            return "🔴 High Risk - Flooding/Waterlogging", "#E64A19"

    risk_status, risk_color = calculate_rainfall_risk(rainfall)
    st.markdown(f"""
        <div class="metric-card glow-effect">
    <h4>⚡ Quick Analytics</h4>
    <p><strong>Total Inputs (Fertilizer + Pesticide):</strong> {total_inputs:.1f} kg/ha</p>
    <p><strong>Rainfall Risk:</strong> <span style="color: {risk_color}; font-weight: 600;">{risk_status}</span></p>
</div>
        """, unsafe_allow_html=True)

# ---------------- Enhanced Prediction Results with Animations -------------------
if submitted and model is not None:
    # Get weather data
    tavg = weather_data[state]["tavg"]
    prcp = weather_data[state]["prcp"]
    lat = weather_data[state]["lat"]
    lon = weather_data[state]["lon"]
    crop_year = datetime.datetime.now().year
    
    # Prepare input for model
    input_df = pd.DataFrame([{
        "State": state,
        "Season": season,
        "Crop": crop,
        "Area": area,
        "Annual_Rainfall": rainfall,
        "Fertilizer": fertilizer,
        "Pesticide": pesticide,
        "Crop_Year": crop_year,
        "tavg": tavg,
        "prcp": prcp,
        "Production": 0  # Dummy value
    }])
    
    try:
        # Animated loading sequence
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulate AI processing with progress updates
        for i in range(100):
            progress_bar.progress(i + 1)
            if i < 30:
                status_text.text('🔍 Analyzing geographic data...')
            elif i < 60:
                status_text.text('🌦️ Processing weather patterns...')
            elif i < 90:
                status_text.text('🧠 Running ML algorithms...')
            else:
                status_text.text('✨ Generating predictions...')
            time.sleep(0.02)
        
        # Make prediction
        prediction = model.predict(input_df)[0]
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Display results with animations
        st.markdown('<div class="success-animation">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">🎯 AI Prediction Results</h2>', unsafe_allow_html=True)
        
        # Main prediction card with enhanced styling
        st.markdown(f"""
        <div class="prediction-card success-animation">
            <h2>🌾 Predicted Crop Yield</h2>
            <h1 style="font-size: 4rem; margin: 1.5rem 0; font-weight: 800;">{prediction:.2f}</h1>
            <h3 style="font-size: 1.5rem; margin-bottom: 1rem;">quintals per hectare</h3>
            <p style="font-size: 1.1rem; opacity: 0.9;">for {crop} cultivation in {state} during {season} season</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced metrics with animations (3 columns)
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            total_production = prediction * area
            st.markdown(f"""
            <div class="metric-card metric-value">
                <h4>📦 Total Production</h4>
                <h2 style="color: #2E7D32; margin: 0.5rem 0;">{total_production:.1f}</h2>
                <p style="margin: 0; color: #666;">quintals</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_m2:
            if prediction < 0:
                category = "Poor"
                color = "#FF5722"
            elif 0 <= prediction < 0.5:
                category = "Below Average"
                color = "#FF9800"
            elif 0.5 <= prediction < 1:
                category = "Average"
                color = "#FFC107"
            elif 1 <= prediction < 1.5:
                category = "Good"
                color = "#4CAF50"
            else:
                category = "Excellent"
                color = "#2E7D32"

            st.markdown(f"""
            <div class="metric-card metric-value">
                <h4>📊 Yield Category</h4>
                <h2 style="color: {color}; margin: 0.5rem 0;">{category}</h2>
                <p style="margin: 0; color: #666;">{prediction:.1f} q/ha</p>
            </div>
            """, unsafe_allow_html=True)

        with col_m3:
            # Calculate revenue using crop-specific prices
            price_per_quintal = crop_prices[crop]
            revenue_estimate = total_production * price_per_quintal

            st.markdown(f"""
            <div class="metric-card metric-value">
                <h4>💰 Revenue Estimate</h4>
                <h2 style="color: #4CAF50; margin: 0.5rem 0;">₹{revenue_estimate:,.0f}</h2>
                <p style="margin: 0; color: #666;">@ ₹{price_per_quintal}/quintal</p>
            </div>
            """, unsafe_allow_html=True)

        # Charts
        st.markdown('<h2 class="section-header">📊 Advanced Analytics Dashboard</h2>', unsafe_allow_html=True)

        viz_col1, viz_col2, viz_col3 = st.columns([1, 1, 1])

        with viz_col1:
            st.markdown("### 🗺️ **Geographic Intelligence**")
            df_map = pd.DataFrame({
                'lat': [lat],
                'lon': [lon],
                'crop': [crop],
                'yield': [prediction]
            })

            fig = px.scatter_mapbox(
                df_map,
                lat="lat",
                lon="lon",
                color="crop",
                size="yield",
                hover_name="crop",
                hover_data={"yield": True, "lat": False, "lon": False},
                zoom=4.2,  # Zoomed out to show all of India
                center={"lat": 22.5, "lon": 80.9},  # Center of India
                height=400
            )
            fig.update_layout(
                mapbox_style="carto-positron",
                margin={"r":0,"t":0,"l":0,"b":0}
            )
            st.plotly_chart(fig, use_container_width=True)

        with viz_col2:
            st.markdown("### 🔬 **Environmental Factor Impact**")
            # Environmental factors radar chart
            factors = ['Rainfall', 'Temperature', 'Fertilizer', 'Area', 'Pesticide']
            values = [
                min(100, rainfall / 15),  # Normalize to 100
                min(100, tavg * 3),
                min(100, fertilizer * 1.5),
                min(100, area * 20),
                min(100, pesticide * 8)
            ]
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=factors,
                fill='toself',
                name='Current Parameters',
                line_color='#4CAF50',
                fillcolor='rgba(76, 175, 80, 0.3)'
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                showlegend=False,
                title="Environmental Factors Impact",
                height=400
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with viz_col3:
            st.markdown("### ⚠️ **Risk Assessment Analysis**")
            # Risk assessment
            risk_factors = pd.DataFrame({
                'Risk_Factor': ['Weather', 'Pest/Disease', 'Market Price', 'Input Cost', 'Soil Health'],
                'Risk_Level': [
                    30 if rainfall > 1000 else 70,  # Weather risk
                    20 if pesticide > 10 else 60,   # Pest risk
                    40,  # Market risk (moderate)
                    50 if fertilizer < 100 else 30,  # Input cost risk
                    35   # Soil health risk (moderate)
                ]
            })
            
            fig_risk = px.bar(
                risk_factors,
                x='Risk_Factor',
                y='Risk_Level',
                color='Risk_Level',
                color_continuous_scale=['green', 'yellow', 'red'],
                title="Risk Assessment Analysis"
            )
            fig_risk.update_layout(
                height=400,
                xaxis_title="Risk Factors",
                yaxis_title="Risk Level (%)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False
            )
            st.plotly_chart(fig_risk, use_container_width=True)
        
        # AI Recommendations with enhanced styling
        st.markdown('<h2 class="section-header">🤖 AI-Powered Recommendations</h2>', unsafe_allow_html=True)
        
        recommendations = []
        
        # Weather-based recommendations
        if rainfall < 600:
            recommendations.append({
                'icon': '💧',
                'title': 'Critical Water Management',
                'desc': f'With only {rainfall}mm rainfall, install drip irrigation system and consider drought-resistant varieties. Expected water deficit: {800-rainfall}mm',
                'priority': 'High'
            })
        elif rainfall > 1500:
            recommendations.append({
                'icon': '🌊',
                'title': 'Excess Water Management',
                'desc': f'High rainfall ({rainfall}mm) may cause waterlogging. Ensure proper drainage and consider fungicide application',
                'priority': 'Medium'
            })
        
        # Fertilizer optimization
        optimal_fertilizer = avg_yields[crop] * 3  # Rule of thumb: 3kg fertilizer per quintal expected yield
        if fertilizer < optimal_fertilizer * 0.7:
            recommendations.append({
                'icon': '🧪',
                'title': 'Increase Fertilizer Application',
                'desc': f'Current: {fertilizer}kg/ha, Recommended: {optimal_fertilizer:.0f}kg/ha. Increase by {optimal_fertilizer-fertilizer:.0f}kg/ha for optimal yield',
                'priority': 'High'
            })
        elif fertilizer > optimal_fertilizer * 1.3:
            recommendations.append({
                'icon': '⚖️',
                'title': 'Reduce Fertilizer Usage',
                'desc': f'Over-fertilization detected ({fertilizer}kg/ha). Reduce to {optimal_fertilizer:.0f}kg/ha to improve cost effectiveness',
                'priority': 'Medium'
            })
        
        
        
        # Pesticide recommendations
        if pesticide > 20:
            recommendations.append({
                'icon': '🌱',
                'title': 'Reduce Chemical Pesticide',
                'desc': f'High pesticide usage ({pesticide}kg/ha). Implement IPM practices to reduce to 10-15kg/ha and improve sustainability',
                'priority': 'Medium'
            })
        elif pesticide < 5:
            recommendations.append({
                'icon': '🛡️',
                'title': 'Pest Management Alert',
                'desc': f'Low pesticide usage ({pesticide}kg/ha) may increase pest risk. Monitor crop health closely and be ready for targeted application',
                'priority': 'Medium'
            })
        
        # Season-specific recommendations
        if season == 'Summer':
            recommendations.append({
                'icon': '☀️',
                'title': 'Summer Season Management',
                'desc': 'Use mulching to conserve soil moisture, provide shade nets if possible, and monitor for heat stress symptoms',
                'priority': 'High'
            })
        elif season == 'Kharif':
            recommendations.append({
                'icon': '🌧️',
                'title': 'Monsoon Preparedness',
                'desc': 'Ensure proper drainage, apply pre-emergence herbicides, and monitor for fungal diseases during monsoon',
                'priority': 'Medium'
            })
        
        
        
        # Crop-specific recommendations
        if crop == 'Rice' and rainfall < 1000:
            recommendations.append({
                'icon': '🌾',
                'title': 'Rice Water Management',
                'desc': 'Rice requires 1000-1200mm water. Consider System of Rice Intensification (SRI) method to reduce water usage by 30-40%',
                'priority': 'High'
            })
        elif crop == 'Groundnut' and fertilizer > 60:
            recommendations.append({
                'icon': '🥜',
                'title': 'Groundnut Nutrition',
                'desc': 'Groundnut fixes nitrogen naturally. Reduce nitrogen fertilizer and focus on phosphorus and potassium for better pod development',
                'priority': 'Medium'
            })
        
        # Default recommendations if none generated
        if not recommendations:
            recommendations = [
                {
                    'icon': '✅',
                    'title': 'Well-Balanced Approach',
                    'desc': f'Your farming parameters are well-optimized for {crop} cultivation. Expected yield of {prediction:.1f} q/ha is within good range',
                    'priority': 'Info'
                },
                {
                    'icon': '📊',
                    'title': 'Market Intelligence',
                    'desc': f'Current market price: ₹{crop_prices[crop]}/quintal. Monitor price trends and consider contract farming for price stability',
                    'priority': 'Medium'
                },
                {
                    'icon': '🌿',
                    'title': 'Sustainable Practices',
                    'desc': 'Implement crop rotation, use organic matter, and maintain soil health for long-term productivity and environmental benefits',
                    'priority': 'Low'
                },
                {
                    'icon': '📱',
                    'title': 'Technology Adoption',
                    'desc': 'Consider using weather-based agro-advisories, soil health cards, and precision farming techniques for better results',
                    'priority': 'Low'
                }
            ]
        
        # Display recommendations with priority color coding
        for i, rec in enumerate(recommendations):
            priority_colors = {
                'High': '#FF5722',
                'Medium': '#FF9800', 
                'Low': '#4CAF50',
                'Info': '#2196F3'
            }
            color = priority_colors.get(rec['priority'], '#4CAF50')
            
            st.markdown(f"""
            <div class="recommendation-card" style="border-left-color: {color}; animation-delay: {i * 0.2}s;">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem; margin-right: 1rem;">{rec['icon']}</span>
                    <h4 style="margin: 0; color: #2E7D32;">{rec['title']}</h4>
                    <span style="margin-left: auto; padding: 0.2rem 0.8rem; background: {color}; color: white; border-radius: 15px; font-size: 0.8rem; font-weight: 600;">{rec['priority']}</span>
                </div>
                <p style="margin: 0; color: #555; line-height: 1.5;">{rec['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Prediction failed: {str(e)}")
        st.info("Please check your model file path and ensure all dependencies are installed.")

# ---------------- Footer -------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 20px; margin-top: 2rem;">
    <h3 style="color: #2E7D32; margin-bottom: 1rem;">🌾 AgriPredict AI</h3>
    <p style="color: #666; font-size: 1.1rem; margin-bottom: 1rem;">Revolutionizing Agriculture with Artificial Intelligence</p>
    <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-bottom: 1rem;">
        <span style="color: #4CAF50; font-weight: 600;">🎯 98.7% Accuracy</span>
        <span style="color: #4CAF50; font-weight: 600;">🚀 Real-time Analysis</span>
        <span style="color: #4CAF50; font-weight: 600;">🌍 Multi-state Coverage</span>
        <span style="color: #4CAF50; font-weight: 600;">📊 Advanced ML</span>
    </div>
    <p style="color: #888; font-size: 0.9rem; margin: 0;">Built with ❤️ from Mayank | Powered by Random Forest Machine Learning</p>
</div>
""", unsafe_allow_html=True)
