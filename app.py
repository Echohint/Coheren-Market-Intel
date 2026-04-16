import streamlit as st
import pandas as pd
import altair as alt
from dotenv import load_dotenv
from src.database import fetch_jobs

# Set page wide config
st.set_page_config(page_title="Coherent Market Intel", page_icon="📡", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for Premium UI ---
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Hide Streamlit menus */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Metric Card Styling */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e1e2d 0%, #151521 100%);
        border: 1px solid #33334d;
        padding: 20px 25px;
        border-radius: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(113, 137, 255, 0.15);
        border: 1px solid #4F8BF9;
    }
    div[data-testid="metric-container"] label {
        color: #9aa0a6;
        font-weight: 600;
        font-size: 1.1rem;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #fff;
        font-size: 2.2rem;
        font-weight: 700;
    }
    
    /* Titles and text */
    h1 {
        background: -webkit-linear-gradient(45deg, #4F8BF9, #20C997);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        letter-spacing: -1px;
    }
    
    /* Search Bar Input styling */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 8px !important;
        border: 1px solid #33334d !important;
        background-color: #1e1e2d !important;
        color: #fff !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📡 Coherent Market Intel")
st.markdown("<p style='font-size: 1.2rem; color: #a0a0a0;'>An interactive, real-time intelligence board tracking remote data engineering opportunities.</p>", unsafe_allow_html=True)

# Load environment variables
load_dotenv()

@st.cache_data(ttl=600)
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
    st.markdown("## ⚙️ Filter Parameters")
    st.markdown("Refine your market view.")
    
    unique_roles = df['role'].unique()
    selected_role = st.selectbox("🎯 Target Role", options=["All"] + list(unique_roles))
    
    unique_companies = df['company'].unique()
    selected_companies = st.multiselect("🏢 Target Companies", options=unique_companies, default=[])

    st.markdown("---")
    st.markdown("🛠️ **Core Technologies**:")
    st.markdown("`Python` | `Selenium` | `Streamlit` | `Pandas`")

# Apply filters
filtered_df = df.copy()
if selected_role != "All":
    filtered_df = filtered_df[filtered_df['role'] == selected_role]
if selected_companies:
    filtered_df = filtered_df[filtered_df['company'].isin(selected_companies)]

tab1, tab2 = st.tabs(["📊 Market Overview", "📋 Detailed Listings"])

with tab1:
    # --- METRICS ROW ---
    st.markdown("### 🏆 High-Level Metrics")
    col1, col2, col3 = st.columns(3)
    
    # Safely compute median instead of mean for better accuracy
    avg_salary_text = "N/A"
    if 'salary_numeric' in filtered_df.columns:
        valid_salaries = filtered_df['salary_numeric'].dropna()
        if not valid_salaries.empty:
            avg_base = valid_salaries.median()
            avg_salary_text = f"${int(avg_base):,}"
            
    with col1:
        st.metric("Total Opportunities", len(filtered_df))
    with col2:
        st.metric("Unique Employers", filtered_df['company'].nunique())
    with col3:
        st.metric("Median Salary", avg_salary_text)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- CHARTS ---
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🔥 Top 10 In-Demand Skills")
        if 'tags' in filtered_df.columns:
            tags_df = filtered_df[['tags']].explode('tags').dropna()
            if not tags_df.empty:
                tags_count = tags_df['tags'].value_counts().reset_index().head(10)
                tags_count.columns = ['Skill', 'Count']
                
                # Dynamic color scheme
                chart = alt.Chart(tags_count).mark_bar(cornerRadiusEnd=4).encode(
                    x=alt.X('Count:Q', title=None, axis=alt.Axis(grid=False)),
                    y=alt.Y('Skill:N', sort='-x', title=None, axis=alt.Axis(labelFontWeight='bold')),
                    color=alt.Color('Count:Q', scale=alt.Scale(scheme='tealblues'), legend=None),
                    tooltip=['Skill', 'Count']
                ).configure_view(strokeWidth=0).properties(height=380)
                
                st.altair_chart(chart, use_container_width=True)
            else:
                st.write("No skill tags available.")

    with c2:
        st.markdown("### 💰 Compensation Distribution")
        if 'salary_numeric' in filtered_df.columns and filtered_df['salary_numeric'].notnull().any():
            sal_chart = alt.Chart(filtered_df).mark_bar(cornerRadiusTop=4, color='#7189FF').encode(
                x=alt.X('salary_numeric:Q', bin=alt.Bin(maxbins=20), title="Compensation Range ($)", axis=alt.Axis(labelAngle=-45, grid=False)),
                y=alt.Y('count():Q', title="Number of Roles", axis=alt.Axis(grid=True, gridColor="#33334d")),
                tooltip=[
                    alt.Tooltip('count()', title='Roles Count'),
                    alt.Tooltip('salary_numeric', bin=True, title='Salary Bucket')
                ]
            ).configure_view(strokeWidth=0).properties(height=380)
            
            st.altair_chart(sal_chart, use_container_width=True)
        else:
            st.info("Insufficient scalar data for compensation mapping.")

with tab2:
    st.markdown("### 📋 Interactive Database Explorer")
    st.markdown("Review the raw intelligence data directly.")
    
    display_df = filtered_df[['role', 'company', 'location', 'salary', 'tags', 'url']].copy()
    if 'tags' in display_df.columns:
        display_df['tags'] = display_df['tags'].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
        
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "role": st.column_config.TextColumn("Job Title", width="large"),
            "company": "Company",
            "location": "Job Location",
            "salary": "Stated Range",
            "tags": "Required Tech",
            "url": st.column_config.LinkColumn("Apply Link")
        }
    )
