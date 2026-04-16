import streamlit as st
import pandas as pd
import altair as alt
from dotenv import load_dotenv
from src.database import fetch_jobs

# Set page wide config
st.set_page_config(page_title="Coherent Market Intel", page_icon="📡", layout="wide", initial_sidebar_state="collapsed")

# --- Custom CSS for Premium, Mobile-Responsive UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Outfit', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Responsive Metric Card Styling */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e1e2d 0%, #151521 100%);
        border: 1px solid #33334d;
        padding: 20px 25px;
        border-radius: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        text-align: center;
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
        text-align: center;
    }
    
    /* Job Card UI Mobile Responsive */
    .job-card {
        background: #1e1e2d;
        border: 1px solid #33334d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transition: border 0.2s ease;
    }
    .job-card:hover {
        border-color: #20C997;
    }
    .job-card h3 {
        color: #fff;
        margin-top: 0;
        font-size: 1.4rem;
    }
    .job-card .company {
        color: #4F8BF9;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 15px;
    }
    .job-card .meta {
        color: #a0a0a0;
        font-size: 0.95rem;
        margin-bottom: 5px;
    }
    .job-card .tags {
        margin-top: 15px;
        margin-bottom: 20px;
    }
    .job-card .tag-badge {
        display: inline-block;
        background: #2a2a3e;
        color: #20C997;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        margin-right: 8px;
        margin-bottom: 8px;
        border: 1px solid #3a3a4e;
    }
    
    /* Interactive Button */
    .apply-btn {
        background: linear-gradient(90deg, #4F8BF9 0%, #20C997 100%);
        color: #fff !important;
        text-decoration: none !important;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
        transition: opacity 0.3s;
        text-align: center;
        width: max-content;
    }
    .apply-btn:hover {
        opacity: 0.85;
    }
    
    /* Media Query for Mobile */
    @media (max-width: 768px) {
        h1 {
            font-size: 2rem !important;
        }
        .apply-btn {
            width: 100%;
            display: block;
        }
        div[data-testid="metric-container"] {
            margin-bottom: 15px;
        }
    }
    
</style>
""", unsafe_allow_html=True)

st.title("📡 Coherent Market Intel")
st.markdown("<p style='font-size: 1.2rem; color: #a0a0a0; text-align: center;'>An interactive, real-time intelligence board tracking remote engineering opportunities.</p>", unsafe_allow_html=True)

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
    st.markdown("## ⚙️ Filter Parameters")
    st.markdown("Refine your market view.")
    
    unique_roles = df['role'].unique() if 'role' in df.columns else []
    selected_role = st.selectbox("🎯 Target Role", options=["All"] + list(unique_roles))
    
    unique_companies = df['company'].unique() if 'company' in df.columns else []
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
    st.markdown("### 🏆 High-Level Metrics")
    col1, col2, col3 = st.columns(3)
    
    avg_salary_text = "N/A"
    if 'salary_numeric' in filtered_df.columns:
        # Convert everything reliably to float to process
        numeric_series = pd.to_numeric(filtered_df['salary_numeric'], errors='coerce').dropna()
        if not numeric_series.empty:
            avg_base = numeric_series.median()
            if avg_base > 0:
                avg_salary_text = f"${int(avg_base):,}"
            
    with col1:
        st.metric("Total Opportunities", len(filtered_df))
    with col2:
        st.metric("Unique Employers", filtered_df['company'].nunique() if 'company' in filtered_df.columns else 0)
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
        if 'salary_numeric' in filtered_df.columns:
            valid_salary_df = filtered_df[pd.to_numeric(filtered_df['salary_numeric'], errors='coerce') > 0]
            if not valid_salary_df.empty:
                sal_chart = alt.Chart(valid_salary_df).mark_bar(cornerRadiusTop=4, color='#7189FF').encode(
                    x=alt.X('salary_numeric:Q', bin=alt.Bin(maxbins=15), title="Compensation Range ($)", axis=alt.Axis(labelAngle=-45, grid=False)),
                    y=alt.Y('count():Q', title="Number of Roles", axis=alt.Axis(grid=True, gridColor="#33334d")),
                    tooltip=[
                        alt.Tooltip('count()', title='Roles Count'),
                        alt.Tooltip('salary_numeric', bin=True, title='Salary Bucket')
                    ]
                ).configure_view(strokeWidth=0).properties(height=380)
                
                st.altair_chart(sal_chart, use_container_width=True)
            else:
                st.info("Insufficient scalar data for compensation mapping. Most roles did not post exact numbers.")
        else:
             st.info("No salary data present.")

with tab2:
    st.markdown("### 📋 Interactive Job Board")
    st.markdown("Review the raw intelligence data directly. Click 'Apply Now' to be redirected to the actual job posting.")
    
    if filtered_df.empty:
        st.warning("No jobs match your current filters.")
    else:
        for index, row in filtered_df.iterrows():
            # Format Tags
            tags_html = ""
            if isinstance(row.get('tags'), list):
                for tag in row['tags']:
                    tags_html += f"<span class='tag-badge'>{tag}</span>"
            elif isinstance(row.get('tags'), str):
                tags_html += f"<span class='tag-badge'>{row['tags']}</span>"
            else:
                tags_html = "<span class='tag-badge'>Any Stack</span>"
                
            salary_disp = row.get('salary', 'Not Specified')
            if not salary_disp: salary_disp = 'Not Specified'
            
            location_disp = row.get('location', 'Remote')
            if not location_disp: location_disp = 'Remote'
            
            card_html = f"""
            <div class="job-card">
                <h3>{row.get('role', 'Unknown Role')}</h3>
                <div class="company">{row.get('company', 'Unknown Company')}</div>
                <div class="meta">📍 <strong>Location:</strong> {location_disp} | 💰 <strong>Compensation:</strong> {salary_disp}</div>
                <div class="tags">
                    {tags_html}
                </div>
                <a href="{row.get('url', '#')}" target="_blank" class="apply-btn">Apply Now 🚀</a>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
