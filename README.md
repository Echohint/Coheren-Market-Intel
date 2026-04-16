<div align="center">
  <h1>📡 Coherent Market Intel</h1>
  <p><strong>A Premium B2B SaaS Intelligence Board for Remote Engineering Opportunities</strong></p>
  <p>🌐 <b>Live Deployment:</b> <a href="https://coheren-market-intel-vytwo8afus8q8tunmcbdpr.streamlit.app/">coheren-market-intel-vytwo8afus8q8tunmcbdpr.streamlit.app</a></p>
  
  [![Python](https://img.shields.io/badge/Python-3.14-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
  [![Selenium](https://img.shields.io/badge/Selenium-WebScraping-green.svg?style=flat-square&logo=selenium)](https://www.selenium.dev/)
  [![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg?style=flat-square&logo=streamlit)](https://streamlit.io/)
  [![Supabase](https://img.shields.io/badge/Supabase-Database-1E4C40.svg?style=flat-square&logo=supabase)](https://supabase.com/)
  [![Scikit-Learn](https://img.shields.io/badge/scikit--learn-Machine%20Learning-orange?style=flat-square&logo=scikit-learn)](https://scikit-learn.org/)
</div>

<hr/>

## 📖 Project Overview

**Coherent Market Intel** is an end-to-end data pipeline and visual intelligence tool built for technical recruiters and high-tier job seekers. 

The application autonomously scrapes hundreds of live Remote engineering listings, processes the unstructured textual data using Pandas, and securely persists the analytics into a Supabase PostgreSQL database via a REST integration.

The consumer-facing output is a flawlessly responsive, "Antigravity" Streamlit dashboard providing dynamic geographic insights, Plotly compensation histograms, and an integrated **Machine Learning Recommendation Engine**.

---

## ✨ Core Features

- **Automated Concurrency Engine:** Utilizes Python's `ThreadPoolExecutor` and headless Selenium to concurrently scrape `Data Engineering`, `Software Development`, and `Junior` job markets simultaneously.
- **Glassmorphism UI:** A highly-responsive, strictly professional B2B-styled interface utilizing custom CSS, mobile media queries, and top-level horizontal navigation.
- **Interactive Analytics:** Generates real-time visual insights using `Plotly` (Global Geographic Hiring Maps, Salary Distributions, Work-Type parameters).
- **Data Export & Pagination:** Deep-dive Job Explorer with dynamic UI pagination limits (`LIMIT/OFFSET` equivalent chunks) and one-click lead extraction to `CSV`.
- **🤖 Intelligent Job Matcher:** Integrated Natural Language Processing (NLP) layer that natively maps unstructured user resumes to mathematical correlations with active hiring roles.

---

## 🧠 Approach to Intelligence (AI/ML)

Rather than solely offering manual dropdown filters, the platform provides deeper value through a semantic **AI Job Matcher**. By leveraging `scikit-learn`, the application natively executes **Content-Based Filtering**.

**Why this approach?** 
Dashboard scalability relies heavily on execution speed. Running `TF-IDF` Vectorization against a `Cosine Similarity` matrix allows the Streamlit app to process semantic overlapping mathematically in milliseconds natively within memory. It requires absolutely zero wait time or connection to paid external LLM APIs (like OpenAI), providing immediate, high-value accuracy ("You are an 89.2% match for this role") without compromising bandwidth constraints.

**Trade-offs Considered:**
While TF-IDF is computationally brilliant and completely open-source, it relies heavily on keyword frequency. If an applicant writes "React.js" and the job description asks for "Modern SPAs", the math may score lower than a massive Deep Learning Transformer (such as BERT) would because it lacks deep semantic entity linking. However, we specifically opted against requiring massive local Vector Databases (like Pinecone) or pulling HuggingFace dependencies to prioritize a totally frictionless, local **One-Command Setup** for rapid evaluation.

---

## 🚀 Environment Setup Instructions

### 1. Environment Initialization
Clone the repository and install the fundamental dependencies securely inside a virtual environment:
```bash
python -m venv venv

# Activate Environment (Windows):
.\venv\Scripts\Activate.ps1
# Activate Environment (Mac/Linux):
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt
```

### 2. Database Integration
Ensure your local `.env` file contains your Supabase authentication keys. To ensure the automated Python bot can insert records, strictly disable **Row Level Security (RLS)** temporarily:
```sql
-- Run inside Supabase SQL Editor:
ALTER TABLE job_listings DISABLE ROW LEVEL SECURITY;
```

### 3. Pipeline Execution
Launch the backend data orchestrator. This master script will concurrently instantiate Selenium WebDrivers to extract roughly 500+ global jobs, clean the numerical artifacts, and bulk-upsert them via the Supabase PostgREST API:
```bash
python main.py
```

### 4. Dashboard Deployment
Initialize the front-end interface dashboard natively in your browser. *(Note: Ensure the virtual environment is active!)*
```bash
streamlit run app.py
```