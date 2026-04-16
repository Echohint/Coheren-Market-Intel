import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.database import fetch_jobs

# Set page wide config
st.set_page_config(page_title="Coherent Market Intel", page_icon="🟢", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #0b0f19;
    }
    
    /* Header Status Indicator */
    .header-container {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 5px;
    }
    .status-dot {
        height: 12px;
        width: 12px;
        background-color: #20C997;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px #20C997;
    }
    
    /* Hide default Streamlit artifacts */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Executive Glassmorphism */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        border: 1px solid #4F8BF9;
    }
    div[data-testid="metric-container"] label {
        color: #a0a0a0;
        font-weight: 600;
        font-size: 1.1rem;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #ffffff;
        font-size: 2.2rem;
        font-weight: 700;
    }
    
    /* Responsive NavBar Overrides */
    .nav-item .nav-link.active {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid #4F8BF9 !important;
    }
    
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-container">
    <h1 style='margin: 0; padding: 0;'>Coherent Market Intel</h1>
    <span class="status-dot" title="Live Sync Active"></span>
</div>
<p style='color: #a0a0a0; font-size: 1.1rem; margin-top: -10px; margin-bottom: 25px;'>Professional B2B SaaS Intelligence Board</p>
""", unsafe_allow_html=True)

# 1. HORIZONTAL NAVBAR
selected = option_menu(
    menu_title=None,  # Hide the main title
    options=["Market Overview", "Analytics Hub", "Job Explorer", "🤖 AI Matchmaker"],
    icons=["bar-chart", "globe", "search", "robot"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#0b0f19", "border": "1px solid #33334d", "border-radius": "12px", "margin-bottom": "30px"},
        "icon": {"color": "#4F8BF9", "font-size": "18px"}, 
        "nav-link": {"font-size": "16px", "text-align": "center", "margin":"0px", "--hover-color": "rgba(255, 255, 255, 0.05)", "color": "#ffffff"},
        "nav-link-selected": {"background-color": "rgba(79, 139, 249, 0.2)", "border": "1px solid #4F8BF9"},
    }
)

load_dotenv()

@st.cache_data(ttl=600)
def load_data():
    raw_data = fetch_jobs()
    if not raw_data:
        return pd.DataFrame()
    df = pd.DataFrame(raw_data)
    if 'salary_numeric' in df.columns:
        df['salary_numeric'] = pd.to_numeric(df['salary_numeric'], errors='coerce')
    # Clean Upgrade strings from location explicitly here in case old data persists
    if 'location' in df.columns:
        df['location'] = df['location'].apply(lambda x: 'Unspecified' if 'upgrade' in str(x).lower() else x)
    return df

with st.spinner("Synchronizing with Vector Store..."):
    df = load_data()

if df.empty:
    st.error("No data found. Ensure the scraper has run.")
    st.stop()

# --- GLOBAL FILTERS ---
all_tags = []
if 'tags' in df.columns:
    df['tags'] = df['tags'].apply(lambda x: x if isinstance(x, list) else [])
    for tags in df['tags']:
        all_tags.extend(tags)
unique_tags = list(set(all_tags))

min_sal = 0
max_sal = 300000
if 'salary_numeric' in df.columns and not df['salary_numeric'].dropna().empty:
    min_sal = int(df['salary_numeric'].min())
    max_sal = int(df['salary_numeric'].max()) + 10000

with st.expander("🔍 Advanced Search & Filter Options", expanded=True):
    col_f1, col_f2, col_f3 = st.columns([1.5, 2, 1.5])
    with col_f1:
        search_query = st.text_input("Search Roles or Companies...", "")
    with col_f2:
        selected_tags = st.multiselect("Require Tech Stacks / Skills", options=unique_tags, default=[])
    with col_f3:
        s_min, s_max = st.slider("Compensation Threshold ($)", min_value=0, max_value=max_sal, value=(0, max_sal), step=10000)

filtered_df = df.copy()

if search_query:
    filtered_df = filtered_df[
        filtered_df['role'].str.contains(search_query, case=False, na=False) |
        filtered_df['company'].str.contains(search_query, case=False, na=False)
    ]

if selected_tags:
    filtered_df = filtered_df[filtered_df['tags'].apply(lambda tags: any(item in tags for item in selected_tags))]

if 'salary_numeric' in filtered_df.columns:
    filtered_df = filtered_df[
        (filtered_df['salary_numeric'].isna()) | 
        ((filtered_df['salary_numeric'] >= s_min) & (filtered_df['salary_numeric'] <= s_max))
    ]

# Render functionalities based on NavBar Selection
if selected == "Market Overview":
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Extracted Roles", f"{len(filtered_df):,}")
    with col2:
        if 'salary_numeric' in filtered_df.columns and not filtered_df['salary_numeric'].dropna().empty:
            avg_sal = filtered_df['salary_numeric'].dropna().mean()
            st.metric("Avg Market Salary", f"${int(avg_sal):,}")
        else:
            st.metric("Avg Market Salary", "N/A")
    with col3:
        if not filtered_df['location'].dropna().empty:
            top_loc = filtered_df['location'].mode()[0]
        else:
            top_loc = "Remote"
        st.metric("Top Global Location", top_loc)
    with col4:
        st.metric("Unique Employers", filtered_df['company'].nunique()) 

    st.markdown("<br>", unsafe_allow_html=True)
    
    cw1, cw2 = st.columns([6, 4])
    with cw1:
        st.markdown("### 🔥 Skill Demand Vectors")
        if not filtered_df.empty and 'tags' in filtered_df.columns:
            tdf = filtered_df[['tags']].explode('tags').dropna()
            if not tdf.empty:
                t_count = tdf['tags'].value_counts().reset_index().head(10)
                t_count.columns = ['Skill', 'Frequency']
                fig = px.bar(t_count, x='Frequency', y='Skill', orientation='h', color='Frequency', color_continuous_scale='Tealgrn')
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white', margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("No skills data.")
    
    with cw2:
        st.markdown("### 💼 Workplace Infrastructure")
        if not filtered_df.empty:
            loc_counts = filtered_df['location'].apply(lambda x: 'Remote' if 'remote' in str(x).lower() else 'Hybrid/On-site').value_counts().reset_index()
            loc_counts.columns = ['Type', 'Count']
            fig_donut = px.pie(loc_counts, values='Count', names='Type', hole=0.6, color_discrete_sequence=['#4F8BF9', '#20C997'])
            fig_donut.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white', margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig_donut, use_container_width=True)

elif selected == "Analytics Hub":
    st.markdown("### 💰 Compensation Volume Distribution")
    if 'salary_numeric' in filtered_df.columns:
        valid_sal = filtered_df[filtered_df['salary_numeric'] > 0]
        if not valid_sal.empty:
            fig_hist = px.histogram(valid_sal, x='salary_numeric', nbins=20, color_discrete_sequence=['#7189FF'])
            fig_hist.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white', margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("Insufficient scalar data for compensation mapping.")

    st.markdown("<br>### 🌍 Geographic Hiring Map", unsafe_allow_html=True)
    if not filtered_df.empty:
        loc_df = filtered_df['location'].value_counts().reset_index().head(15)
        loc_df.columns = ['Location', 'Opportunities']
        fig_loc = px.bar(loc_df, x='Location', y='Opportunities', color='Opportunities', color_continuous_scale='Blues')
        fig_loc.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_loc, use_container_width=True)

elif selected == "Job Explorer":
    st.markdown("### 🔍 Advanced Job Parsing Data")
    
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Lead File (CSV)",
        data=csv,
        file_name='coherent_b2b_leads.csv',
        mime='text/csv',
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    display_cols = ['role', 'company', 'location', 'salary_numeric', 'tags', 'url']
    
    if not filtered_df.empty:
        # Dynamic Pagination System (LIMIT/OFFSET paradigm) 
        page_size = 100
        total_items = len(filtered_df)
        total_pages = (total_items - 1) // page_size + 1
        
        pg_col1, pg_col2, pg_col3 = st.columns([1, 3, 1])
        with pg_col1:
            page = st.number_input(f"Navigate Page (Max {total_pages})", min_value=1, max_value=total_pages, value=1, step=1)
            
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        with pg_col2:
            st.markdown(f"<p style='margin-top: 35px; color: #a0a0a0;'>Displaying records {start_idx + 1} to {min(end_idx, total_items)} out of <b>{total_items}</b> total market insights.</p>", unsafe_allow_html=True)
            
        st.dataframe(filtered_df[display_cols].iloc[start_idx:end_idx], use_container_width=True, hide_index=True)
    else:
        st.warning("No data found according to your current constraints.")

elif selected == "🤖 AI Matchmaker":
    st.markdown("### 🤖 NLP Job Matchmaking Engine")
    st.markdown("Powered by **TF-IDF & Cosine Similarity**. Paste your skills or resume below to mathematically match with the top opportunities in the database.")
    
    user_profile = st.text_area("Your Tech Profile / Resume:", height=150, placeholder="e.g. 5+ years experience in Python, specialized in distributed systems, SQL databases, and Pandas. Looking for Senior roles.")
    
    if st.button("Calculate Matches 🚀") and user_profile:
        if not filtered_df.empty:
            with st.spinner("Executing Vector Calculations..."):
                # Combine role, tags, and location for robust semantic context
                def make_document(row):
                    tags = " ".join(row.get('tags', [])) if isinstance(row.get('tags'), list) else str(row.get('tags', ''))
                    return f"{row.get('role', '')} {row.get('company', '')} {tags} {row.get('location', '')}"
                
                job_docs = filtered_df.apply(make_document, axis=1).tolist()
                
                # Prepend user profile to corpus
                full_corpus = [user_profile] + job_docs
                
                # TF-IDF calculation
                vectorizer = TfidfVectorizer(stop_words='english')
                tfidf_matrix = vectorizer.fit_transform(full_corpus)
                
                # Cosine Similarity between user_profile (index 0) and all jobs (index 1 to end)
                cosine_sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
                
                # Attach scores to dataframe
                scored_df = filtered_df.copy()
                scored_df['match_score'] = cosine_sims * 100 # percentage
                
                # Filter out zeroes and sort
                top_matches = scored_df[scored_df['match_score'] > 0].sort_values(by='match_score', ascending=False).head(5)
                
            if top_matches.empty:
                st.warning("No significant semantic overlap found with current market listings. Try broadening your keywords.")
            else:
                st.success(f"Discovered {len(top_matches)} Highly Correlated Opportunities!")
                
                for _, row in top_matches.iterrows():
                    score = row['match_score']
                    salary_disp = row.get('salary', 'Not Specified')
                    location_disp = row.get('location', 'Remote')
                    
                    tags_html = ""
                    if isinstance(row.get('tags'), list):
                        for tag in row['tags']:
                            tags_html += f"<span class='tag-badge'>{tag}</span>"
                    
                    card_html = f"""
                    <div class="job-card" style="border-left: 4px solid #20C997; margin-bottom: 20px;">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <h3>{row.get('role', 'Unknown')}</h3>
                                <div class="company">{row.get('company', 'Unknown')}</div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.8rem; font-weight: 700; color: #20C997;">{score:.1f}%</div>
                                <div style="color: #a0a0a0; font-size: 0.8rem;">Match Index</div>
                            </div>
                        </div>
                        <div class="meta">📍 {location_disp} | 💰 {salary_disp}</div>
                        <div class="tags">{tags_html}</div>
                        <a href="{row.get('url', '#')}" target="_blank" class="apply-btn">View Opportunity</a>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.error("The database is currently empty. Please clear filters or sync market data.")

