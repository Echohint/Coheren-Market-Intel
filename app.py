import streamlit as st
import pandas as pd
import altair as alt
from dotenv import load_dotenv
from src.database import fetch_jobs

# Set page wide config
st.set_page_config(page_title="RemoteOK Analytics Board", page_icon="🌎", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for Premium RemoteOK-Like Mobile-Responsive UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Nunito', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Responsive Metric Card Styling */
    div[data-testid="metric-container"] {
        background: #ffffff;
        border: 1px solid #e1e4e8;
        padding: 20px 25px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    }
    div[data-testid="metric-container"] label {
        color: #586069;
        font-weight: 800;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #0073b1;
        font-size: 2.6rem;
        font-weight: 900;
    }
    
    /* Streamlit overrides for light/dark mode */
    .stApp {
        background-color: #f7f9fa;
    }
    
    /* RemoteOK Inspired Job Card Layout */
    .job-card-row {
        display: flex;
        align-items: center;
        background: #007bb5; /* Iconic RemoteOK Blue */
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        color: #ffffff;
        box-shadow: 0 6px 16px rgba(0, 123, 181, 0.2);
        transition: transform 0.2s ease, box-shadow 0.2s;
        border: 2px solid #006090;
    }
    .job-card-row:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 24px rgba(0, 123, 181, 0.4);
    }
    
    .card-logo {
        width: 70px;
        height: 70px;
        min-width: 70px;
        border-radius: 50%;
        background: #1e1e2d;
        color: #20C997;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
        font-size: 32px;
        margin-right: 20px;
        border: 3px solid rgba(255,255,255,0.2);
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);
    }
    
    .card-content {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .card-title {
        font-size: 1.4rem;
        font-weight: 900;
        margin: 0 0 4px 0;
        display: flex;
        align-items: center;
        gap: 8px;
        letter-spacing: -0.5px;
    }
    .verified-badge {
        background: #00e676;
        color: #004d40;
        font-size: 0.75rem;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 900;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    .card-company {
        font-size: 1.1rem;
        font-weight: 700;
        margin: 0 0 10px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .new-badge {
        font-size: 0.7rem;
        background: linear-gradient(90deg, #ff8a00, #e52e71);
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: 900;
    }
    
    .meta-pills {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }
    
    .meta-pill {
        background: #ffffff;
        color: #333;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 800;
        display: inline-flex;
        align-items: center;
    }
    
    .card-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        max-width: 400px;
        justify-content: flex-end;
        align-items: center;
        margin-right: 20px;
    }
    
    .tag-pill {
        background: #ffffff;
        color: #007bb5;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 900;
        white-space: nowrap;
    }
    
    .card-action {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .time-posted {
        font-size: 0.9rem;
        color: rgba(255,255,255,0.9);
        font-weight: 700;
    }
    
    .apply-btn {
        background: #ffffff;
        color: #007bb5 !important;
        padding: 12px 36px;
        border-radius: 10px;
        font-weight: 900;
        text-decoration: none !important;
        font-size: 1.15rem;
        transition: transform 0.2s, background 0.2s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .apply-btn:hover {
        background: #f0f0f0;
        transform: scale(1.05);
    }
    
    /* Header Area tweaks */
    .top-header {
        font-size: 1.2rem;
        font-weight: 800;
        text-align: center;
        background: white;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e1e4e8;
        margin-bottom: 20px;
        color: #333;
    }
    .top-header span {
        color: #ffffff;
        background: #007bb5;
        padding: 5px 12px;
        border-radius: 8px;
    }
    
    /* Media Query for Mobile Layout */
    @media (max-width: 1024px) {
        .job-card-row {
            flex-direction: column;
            align-items: flex-start;
        }
        .card-logo {
            margin-bottom: 15px;
        }
        .card-tags {
            justify-content: flex-start;
            margin: 20px 0;
            max-width: 100%;
        }
        .card-action {
            width: 100%;
            justify-content: space-between;
        }
        .apply-btn {
            width: 60%;
            text-align: center;
        }
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='top-header'>👉 Hiring for a Remote position? <span>Claim your 10% discount</span> and post a job on the 🏆 #1 Remote Jobs board.</div>", unsafe_allow_html=True)

# Load environment variables
load_dotenv()

def load_data():
    raw_data = fetch_jobs()
    if not raw_data:
        return pd.DataFrame()
    return pd.DataFrame(raw_data)

with st.spinner("Fetching live market data..."):
    df = load_data()

if df.empty:
    st.error("No data found. Ensure the scraper has run and your Supabase URL/Key are correctly set in the .env file.")
    st.stop()

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.markdown("## 🔍 Smart Filters")
    st.markdown("Sort by exactly what matters to you.")
    
    unique_roles = df['role'].unique() if 'role' in df.columns else []
    selected_role = st.selectbox("🌎 Select Role Level", options=["All Levels"] + list(unique_roles))
    
    unique_companies = df['company'].unique() if 'company' in df.columns else []
    selected_companies = st.multiselect("🏢 Filter by Company", options=unique_companies, default=[])

    st.markdown("---")
    st.markdown("🛠️ **Built via Selenium WebScraper**")

# Apply filters
filtered_df = df.copy()
if selected_role != "All Levels":
    filtered_df = filtered_df[filtered_df['role'] == selected_role]
if selected_companies:
    filtered_df = filtered_df[filtered_df['company'].isin(selected_companies)]


# --- CHARTS & METRICS VIEW ---
with st.expander("📊 View Interactive Market Analytics", expanded=False):
    st.markdown("### 🏆 Live Job Insights")
    col1, col2, col3 = st.columns(3)
    
    avg_salary_text = "N/A"
    if 'salary_numeric' in filtered_df.columns:
        numeric_series = pd.to_numeric(filtered_df['salary_numeric'], errors='coerce').dropna()
        if not numeric_series.empty:
            avg_base = numeric_series.median()
            if avg_base > 0:
                avg_salary_text = f"${int(avg_base):,}"
            
    with col1:
        st.metric("Tech Opportunities", len(filtered_df))
    with col2:
        st.metric("Hiring Startups", filtered_df['company'].nunique() if 'company' in filtered_df.columns else 0)
    with col3:
        st.metric("Median Salary", avg_salary_text)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🔥 Top In-Demand Tech Stacks")
        if 'tags' in filtered_df.columns:
            tags_df = filtered_df[['tags']].explode('tags').dropna()
            if not tags_df.empty:
                tags_count = tags_df['tags'].value_counts().reset_index().head(8)
                tags_count.columns = ['Skill', 'Count']
                
                chart = alt.Chart(tags_count).mark_bar(cornerRadiusEnd=4).encode(
                    x=alt.X('Count:Q', title=None, axis=alt.Axis(grid=False)),
                    y=alt.Y('Skill:N', sort='-x', title=None, axis=alt.Axis(labelFontWeight='bold')),
                    color=alt.Color('Count:Q', scale=alt.Scale(scheme='blues'), legend=None),
                    tooltip=['Skill', 'Count']
                ).configure_view(strokeWidth=0).properties(height=300)
                st.altair_chart(chart, use_container_width=True)
                
    with c2:
        st.markdown("#### 💰 Global Compensation Spread")
        if 'salary_numeric' in filtered_df.columns:
            valid_salary_df = filtered_df[pd.to_numeric(filtered_df['salary_numeric'], errors='coerce') > 0]
            if not valid_salary_df.empty:
                sal_chart = alt.Chart(valid_salary_df).mark_area(opacity=0.7, color='#007bb5').encode(
                    x=alt.X('salary_numeric:Q', bin=alt.Bin(maxbins=12), title="Compensation Range ($)"),
                    y=alt.Y('count():Q', title="Roles Count", axis=alt.Axis(grid=True)),
                    tooltip=[alt.Tooltip('count()', title='Count'), alt.Tooltip('salary_numeric', bin=True, title='Bucket')]
                ).configure_view(strokeWidth=0).properties(height=300)
                st.altair_chart(sal_chart, use_container_width=True)

# --- JOB BOARD FEED ---
st.markdown("### 📋 Remote & Flexible Jobs")

if filtered_df.empty:
    st.warning("No jobs match your current filters. Adjust your criteria.")
else:
    for index, row in filtered_df.iterrows():
        company_name = row.get('company', 'Company')
        logo_letter = company_name[0] if len(company_name) > 0 else "💼"
        
        # Format Tags
        tags_html = ""
        if isinstance(row.get('tags'), list):
            # Show up to 6 tags max
            for tag in row['tags'][:6]:
                tags_html += f"<div class='tag-pill'>{tag}</div>"
        elif isinstance(row.get('tags'), str):
            tags_html += f"<div class='tag-pill'>{row['tags']}</div>"
            
        salary_disp = row.get('salary', '')
        if not salary_disp: salary_disp = 'DOE'
        
        location_disp = row.get('location', '')
        if not location_disp: location_disp = 'Worldwide'
        
        card_html = f"""
        <div class="job-card-row">
            <div class="card-logo">{logo_letter}</div>
            
            <div class="card-content">
                <div class="card-title">{row.get('role', 'Senior Engineer')} <span class="verified-badge">VERIFIED</span></div>
                <div class="card-company">Level <span class="new-badge">NEW</span></div>
                <div class="meta-pills">
                    <span class="meta-pill">🌍 {location_disp}</span>
                    <span class="meta-pill">💰 {salary_disp}</span>
                </div>
            </div>
            
            <div class="card-tags">
                {tags_html}
            </div>
            
            <div class="card-action">
                <div class="time-posted">📎 4h</div>
                <a href="{row.get('url', '#')}" target="_blank" class="apply-btn">Apply</a>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
