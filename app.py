import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
from dotenv import load_dotenv
from src.database import fetch_jobs
import re

# Set page wide config
st.set_page_config(page_title="Coherent Market Intel", page_icon="🟢", layout="wide", initial_sidebar_state="expanded")

CYAN = "#00f2fe"
DARK_BG = "#0b0f19"
PANEL_BG = "#131823"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="css"]  {{
        font-family: 'Inter', sans-serif;
    }}
    
    /* Overall Backgrounds */
    .stApp {{
        background-color: {DARK_BG};
    }}
    section[data-testid="stSidebar"] > div:first-child {{
        background-color: {PANEL_BG};
        border-right: 1px solid #2a3140;
    }}
    
    /* Top Header Bar Simulation */
    .top-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 20px;
        border-bottom: 1px solid #2a3140;
        margin-bottom: 30px;
    }}
    .top-header .logo {{
        color: {CYAN};
        font-size: 1.6rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }}
    .top-header .search-mock {{
        background: #1c2230;
        border-radius: 6px;
        padding: 8px 16px;
        width: 400px;
        color: #8b949e;
        border: 1px solid #2a3140;
        font-size: 0.9rem;
    }}
    .top-header .controls {{
        display: flex;
        gap: 15px;
        color: #8b949e;
        align-items: center;
        font-weight: 600;
        font-size: 0.9rem;
    }}
    
    /* Hide Default Streamlit Nav/Footer */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Custom Metric Cards */
    .kpi-card {{
        background-color: transparent;
        border: 1px solid #2a3140;
        border-radius: 4px;
        padding: 24px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        background: linear-gradient(180deg, #131823 0%, rgba(19, 24, 35, 0.5) 100%);
    }}
    .kpi-title {{
        color: #8b949e;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 25px;
    }}
    .kpi-value {{
        color: #ffffff;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 25px;
    }}
    .kpi-cyan-bar {{
        height: 4px;
        background-color: {CYAN};
        width: 30px;
        border-radius: 2px;
        box-shadow: 0 0 10px {CYAN};
    }}
    
    /* Title Stylings */
    .main-title {{
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 5px;
    }}
    .main-title span {{
        color: {CYAN};
        text-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
    }}
    .sub-title {{
        color: #8b949e;
        font-size: 0.95rem;
        margin-bottom: 30px;
    }}
    
    /* Streamlit overrides for inputs */
    div[data-baseweb="select"] > div {{
        background-color: #1c2230 !important;
        border-color: #2a3140 !important;
        color: white;
    }}
    .stTextInput input {{
        background-color: #1c2230 !important;
        border-color: #2a3140 !important;
        color: white;
    }}
    .stSlider div[data-testid="stThumbValue"] {{
        color: {CYAN} !important;
    }}
    .stSlider div[role="slider"] {{
        background-color: {CYAN} !important;
        box-shadow: 0 0 8px {CYAN} !important;
    }}
    .stSlider div[data-testid="stTickBar"] > div {{
        background-color: {CYAN} !important;
    }}
    
    /* Multi Select Pills Force Cyan */
    span[data-baseweb="tag"] {{
        background-color: {CYAN} !important;
        color: #000 !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
    }}
    
    /* Generate Report Button */
    .report-btn {{
        background-color: {CYAN};
        color: #000;
        font-weight: 700;
        width: 100%;
        padding: 12px;
        text-align: center;
        border-radius: 4px;
        margin-top: 50px;
        cursor: pointer;
        transition: 0.3s;
        border: none;
    }}
    .report-btn:hover {{
        box-shadow: 0 0 15px {CYAN};
    }}
    
    /* Job Card for Apply Buttons */
    .job-card {{
        background: transparent;
        border-bottom: 1px solid #2a3140;
        padding: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: 0.2s;
    }}
    .job-card:hover {{
        background: #1c2230;
    }}
    .job-info h4 {{
        margin: 0;
        color: #fff;
        font-size: 1.05rem;
        font-weight: 600;
    }}
    .job-info p {{
        margin: 4px 0 0 0;
        color: #8b949e;
        font-size: 0.85rem;
    }}
    .job-info p span.company {{
        color: #fff;
        font-weight: 600;
    }}
    .apply-btn {{
        background: transparent;
        color: {CYAN} !important;
        text-decoration: none !important;
        padding: 6px 12px;
        border-radius: 4px;
        border: 1px solid {CYAN};
        font-size: 0.85rem;
        transition: 0.2s;
        font-weight: 600;
    }}
    .apply-btn:hover {{
        background: {CYAN};
        color: #000 !important;
    }}
    </style>
""", unsafe_allow_html=True)

# 1. TOP HEADER FAKE NAVBAR
st.markdown(f"""
<div class="top-header">
    <div class="logo">Coherent Intelligence</div>
    <div class="search-mock">🔍 Global Intelligence Search...</div>
    <div class="controls">🔔 &nbsp; ⚙️ &nbsp; 👤 ADMIN</div>
</div>
""", unsafe_allow_html=True)

load_dotenv()

@st.cache_data(ttl=600)
def load_data():
    raw_data = fetch_jobs()
    if not raw_data:
        return pd.DataFrame()
    df = pd.DataFrame(raw_data)
    if 'salary_numeric' in df.columns:
        df['salary_numeric'] = pd.to_numeric(df['salary_numeric'], errors='coerce')
    if 'location' in df.columns:
        df['location'] = df['location'].apply(lambda x: 'Unspecified' if 'upgrade' in str(x).lower() else x)
    return df

with st.spinner("Synchronizing with Market..."):
    df = load_data()

if df.empty:
    st.error("No data found. Ensure the scraper has run.")
    st.stop()

# --- SIDEBAR (COMMAND CENTER + FILTERS) ---
with st.sidebar:
    st.markdown(f"<h3 style='color: {CYAN}; letter-spacing: -0.5px;'>COMMAND CENTER</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8b949e; font-size: 0.8rem; margin-top: -15px; margin-bottom: 30px;'>MARKET INTEL V2.4</p>", unsafe_allow_html=True)
    
    # Fake nav links
    st.markdown(f"""
        <div style='color: #fff; margin-bottom: 25px; font-weight: 600;'><span style='color: {CYAN}; margin-right: 15px;'>📈</span> MARKET OVERVIEW</div>
        <div style='color: #8b949e; margin-bottom: 25px;'><span style='margin-right: 15px;'>📊</span> COMPETITOR ANALYSIS</div>
        <div style='color: #8b949e; margin-bottom: 25px;'><span style='margin-right: 15px;'>👥</span> TALENT MAPPING</div>
        <div style='color: #8b949e; margin-bottom: 25px;'><span style='margin-right: 15px;'>💵</span> SALARY BENCHMARKS</div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border-color: #2a3140; margin: 40px 0;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #8b949e; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px;'>Discovery Filters</h4>", unsafe_allow_html=True)
    
    search_query = st.text_input("SEARCH ROLES & ENTITIES", label_visibility="collapsed", placeholder="e.g. Lead Engineer, NVIDIA")
    
    st.markdown("<h4 style='color: #8b949e; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px; margin-top: 20px;'>Core Skill Matrix</h4>", unsafe_allow_html=True)
    all_tags = []
    if 'tags' in df.columns:
        df['tags'] = df['tags'].apply(lambda x: x if isinstance(x, list) else [])
        for tags in df['tags']:
            all_tags.extend([tag.upper() for tag in tags])
    unique_tags = list(set(all_tags))
    selected_tags = st.multiselect("CORE SKILL MATRIX", options=unique_tags, default=[], label_visibility="collapsed")
    
    min_sal = 0
    max_sal = 350000
    if 'salary_numeric' in df.columns and not df['salary_numeric'].dropna().empty:
        min_sal = int(df['salary_numeric'].min())
        max_sal = int(df['salary_numeric'].max()) + 10000
    
    st.markdown(f"<div style='display: flex; justify-content: space-between;'><p style='color: #ffffff; font-size: 0.75rem; font-weight: 600; margin-bottom: -30px;'>SALARY BAND (USD)</p><p style='color: {CYAN}; font-size: 0.75rem; font-weight: 600; margin-bottom: -30px;'>$120k - $285k</p></div>", unsafe_allow_html=True)
    s_min, s_max = st.slider("", min_value=0, max_value=max_sal, value=(0, max_sal), step=10000, key="salary_slider")
    
    st.markdown(f"<button class='report-btn'>GENERATE REPORT</button>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8b949e; font-size: 0.7rem; margin-top: 20px; font-style: italic;'>Filtering across remote data points in real-time.</p>", unsafe_allow_html=True)

# --- FILTERING LOGIC ---
filtered_df = df.copy()

if search_query:
    filtered_df = filtered_df[
        filtered_df['role'].str.contains(search_query, case=False, na=False) |
        filtered_df['company'].str.contains(search_query, case=False, na=False)
    ]

if selected_tags:
    filtered_df = filtered_df[filtered_df['tags'].apply(lambda tags: any(item.upper() in selected_tags for item in tags))]

if 'salary_numeric' in filtered_df.columns:
    filtered_df = filtered_df[
        (filtered_df['salary_numeric'].isna()) | 
        ((filtered_df['salary_numeric'] >= s_min) & (filtered_df['salary_numeric'] <= s_max))
    ]

# --- MAIN CONTENT ---
st.markdown("<div class='main-title'>Market Dynamics <span>Live</span></div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Deep-dive intelligence for the Cloud infrastructure sector. Data refreshed seconds ago.</div>", unsafe_allow_html=True)

# METRICS ROW
c1, c2, c3, c4 = st.columns(4)

total_jobs = len(filtered_df)
avg_sal = filtered_df['salary_numeric'].dropna().median() if 'salary_numeric' in filtered_df.columns and not filtered_df['salary_numeric'].dropna().empty else 0
top_loc = filtered_df['location'].mode()[0] if not filtered_df['location'].dropna().empty else "Remote"
top_company = filtered_df['company'].mode()[0] if not filtered_df['company'].dropna().empty else "Unknown"

c1.markdown(f"""
<div class="kpi-card">
    <div class="kpi-title">MARKET VOLUME</div>
    <div class="kpi-value">{total_jobs}k</div>
    <div class="kpi-cyan-bar"></div>
</div>
""", unsafe_allow_html=True)

c2.markdown(f"""
<div class="kpi-card">
    <div class="kpi-title">MOMENTUM (AVG)</div>
    <div class="kpi-value">${int(avg_sal):,}</div>
    <div class="kpi-cyan-bar" style="width: 50px;"></div>
</div>
""", unsafe_allow_html=True)

c3.markdown(f"""
<div class="kpi-card">
    <div class="kpi-title">TOP HUB</div>
    <div class="kpi-value" style="font-size: 1.8rem; margin-top: 15px; margin-bottom: 25px;">{top_loc}</div>
    <div class="kpi-cyan-bar" style="width: 25px;"></div>
</div>
""", unsafe_allow_html=True)

c4.markdown(f"""
<div class="kpi-card">
    <div class="kpi-title">TOP RECRUITER</div>
    <div class="kpi-value" style="font-size: 1.5rem; margin-top: 18px; margin-bottom: 25px;">{top_company}</div>
    <div class="kpi-cyan-bar" style="width: 80px;"></div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# CHARTS ROW
ch1, ch2 = st.columns([6, 4])
with ch1:
    st.markdown(f"<div style='background: {PANEL_BG}; border: 1px solid #2a3140; border-radius: 4px; padding: 25px;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #fff; margin-top: 0; font-size: 1.1rem; font-weight: 600;'>Skill Demand Heatmap</h3>", unsafe_allow_html=True)
    if not filtered_df.empty and 'tags' in filtered_df.columns:
        tdf = filtered_df[['tags']].explode('tags').dropna()
        if not tdf.empty:
            t_count = tdf['tags'].apply(lambda x: x.upper()).value_counts().reset_index().head(5)
            t_count.columns = ['Skill', 'Frequency']
            fig = px.bar(t_count, x='Frequency', y='Skill', orientation='h')
            fig.update_traces(marker_color=CYAN, marker_line_width=0, opacity=1.0, width=0.2)
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                font_color='#fff', margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(showgrid=False, zeroline=False, visible=False),
                yaxis=dict(title=None, showgrid=False, tickfont=dict(size=11, color='#fff', weight='bold'))
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
             st.write("No skills data.")
    st.markdown("</div>", unsafe_allow_html=True)

with ch2:
    st.markdown(f"<div style='background: {PANEL_BG}; border: 1px solid #2a3140; border-radius: 4px; padding: 25px;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #fff; margin-top: 0; font-size: 1.1rem; font-weight: 600;'>Salary Distribution</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8b949e; font-size: 0.75rem; letter-spacing: 1px; text-transform: uppercase;'>SECTOR: ARTIFICIAL INTELLIGENCE</p>", unsafe_allow_html=True)
    if 'salary_numeric' in filtered_df.columns:
        valid_sal = filtered_df[filtered_df['salary_numeric'] > 0]
        if not valid_sal.empty:
            fig_hist = px.histogram(valid_sal, x='salary_numeric', nbins=12)
            fig_hist.update_traces(marker_color=CYAN, opacity=0.8)
            fig_hist.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                font_color='#8b949e', margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(title=False, showgrid=False, tickformat="$.0s"),
                yaxis=dict(title=False, showgrid=False, visible=False),
                bargap=0.3
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("Insufficient scalar data for compensation mapping.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# RECENT MARKET POSTINGS
st.markdown(f"""
<div style='display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;'>
    <div>
        <h3 style='color: #fff; margin: 0; font-size: 1.2rem; font-weight: 600;'>Recent Market Postings</h3>
        <p style='color: #8b949e; font-size: 0.85rem; margin: 5px 0 0 0;'>Showing {min(10, len(filtered_df))} of {len(filtered_df)} active opportunities.</p>
    </div>
    <div style='color: {CYAN}; font-size: 0.85rem; font-weight: 700; letter-spacing: 1px; cursor: pointer;'>
        EXPORT CSV 📥
    </div>
</div>
""", unsafe_allow_html=True)

# Functional Job Cards
if not filtered_df.empty:
    for _, row in filtered_df.head(10).iterrows():
        salary_text = row.get('salary') if pd.notnull(row.get('salary')) and row.get('salary') != '' else "Competitive"
        
        st.markdown(f"""
        <div class="job-card">
            <div class="job-info">
                <h4>{row.get('role', 'Unknown')}</h4>
                <p><span class="company">{row.get('company', 'Unknown')}</span> • {row.get('location', 'Remote')} • 💰 {salary_text}</p>
            </div>
            <a href="{row.get('url', '#')}" target="_blank" class="apply-btn">View Opportunity</a>
        </div>
        """, unsafe_allow_html=True)
else:
    st.warning("No listings match the current Discovery Filters.")
