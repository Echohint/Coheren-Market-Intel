import streamlit as st
import pandas as pd
import altair as alt
from dotenv import load_dotenv
from src.database import fetch_jobs

# Set page wide config
st.set_page_config(page_title="Coherent Market Intel", page_icon="📊", layout="wide")

st.title("📊 Coherent Market Intel: RemoteOK Dashboard")
st.markdown("### A premium intelligence board for remote data engineering jobs.")

# Load environment variables
load_dotenv()

@st.cache_data(ttl=600)
def load_data():
    raw_data = fetch_jobs()
    if not raw_data:
        return pd.DataFrame()
    return pd.DataFrame(raw_data)

df = load_data()

if df.empty:
    st.warning("No data found in Supabase. Please run the scraper (`python main.py`) first or check .env credentials.")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filter Jobs")

unique_roles = df['role'].unique()
selected_role = st.sidebar.selectbox("Select Role", options=["All"] + list(unique_roles))

unique_companies = df['company'].unique()
selected_companies = st.sidebar.multiselect("Select Companies", options=unique_companies, default=[])

# Apply filters
filtered_df = df.copy()
if selected_role != "All":
    filtered_df = filtered_df[filtered_df['role'] == selected_role]
if selected_companies:
    filtered_df = filtered_df[filtered_df['company'].isin(selected_companies)]

# --- METRICS ROW ---
st.markdown("### Quick Insights")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Target Jobs", len(filtered_df))
with col2:
    st.metric("Unique Companies Hiring", filtered_df['company'].nunique())
with col3:
    avg_salary_text = "N/A"
    if 'average_salary' in filtered_df.columns:
        avg_base = filtered_df['average_salary'].mean()
        if pd.notnull(avg_base):
            avg_salary_text = f"${int(avg_base/1000)}k"
    st.metric("Average Estimated Salary", avg_salary_text)

# --- CHARTS ---
st.markdown("---")
c1, c2 = st.columns(2)

with c1:
    st.subheader("🔥 Top 10 In-Demand Skills")
    if 'tags' in filtered_df.columns:
        tags_df = filtered_df[['tags']].explode('tags').dropna()
        if not tags_df.empty:
            tags_count = tags_df['tags'].value_counts().reset_index().head(10)
            tags_count.columns = ['Skill', 'Count']
            chart = alt.Chart(tags_count).mark_bar(color='#4F8BF9').encode(
                x='Count:Q',
                y=alt.Y('Skill:N', sort='-x'),
                tooltip=['Skill', 'Count']
            ).properties(height=350)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.write("No tags data available.")

with c2:
    st.subheader("💰 Jobs by Salary Range")
    if 'average_salary' in filtered_df.columns and filtered_df['average_salary'].notnull().any():
        sal_chart = alt.Chart(filtered_df).mark_bar(color='#20C997').encode(
            x=alt.X('average_salary:Q', bin=alt.Bin(maxbins=15), title="Salary Range ($)"),
            y=alt.Y('count():Q', title="Number of Jobs"),
            tooltip=['count()']
        ).properties(height=350)
        st.altair_chart(sal_chart, use_container_width=True)
    else:
        st.info("Not enough numeric salary data to plot histogram.")

# --- DATA TABLE ---
st.markdown("---")
st.markdown("### 📋 Job Listings Explorer")
display_df = filtered_df[['role', 'company', 'location', 'salary', 'tags', 'date', 'url']].copy()
# Format tags display
if 'tags' in display_df.columns:
    display_df['tags'] = display_df['tags'].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)

st.dataframe(display_df, use_container_width=True, hide_index=True)
