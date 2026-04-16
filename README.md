# 📡 Coherent Market Intel

An end-to-end B2B SaaS Intelligence Dashboard tracking remote software engineering opportunities.

## 🚀 One-Command Setup

To run this platform locally via your virtual environment:

1. Clone the repository and install dependencies:
```bash
pip install -r requirements.txt
```
2. Disable Row Level Security in your connected Supabase:
   *(SQL Editor -> `ALTER TABLE job_listings DISABLE ROW LEVEL SECURITY;`)*
3. Run the Scraper (Populates your database instantly with 500+ records):
```bash
python main.py
```
4. Launch the Interactive Dashboard:
```bash
streamlit run app.py
```

## 🧠 Bonus Requirement: AI/ML Intelligent Matchmaker

### The Feature
We implemented a **Content-Based NLP Recommendation Engine** directly into the dashboard. Job seekers paste their technical profile (or resume), and the system uses `TfidfVectorizer` and `cosine_similarity` to mathematically calculate semantic overlap against the corpus of jobs. It returns the "Top 5" roles with a distinct Match Percentage score.

### Why We Chose This Approach
For a dashboard designed to handle thousands of constantly updating records without hanging the UI, computational efficiency is paramount.
1. **Lightweight & Native**: TF-IDF requires zero paid external APIs (unlike expensive OpenAI wrappers) and runs natively in `scikit-learn` incredibly fast.
2. **Instant Scalability**: It calculates vector distance against pandas dataframes in milliseconds, maintaining the seamless snappiness expected from professional B2B products.
3. **Immediate User Value**: Data filters are standard, but predicting a user's *contextual* fit to unstructured job postings provides genuine high-tier intelligence to the board.

### Trade-offs Considered
1. **Semantic Awareness vs Exact Matches**: TF-IDF relies on keyword frequency. If a user types "React.js" and a job lists "Frontend modern SPA framework", the cosine similarity will score lower than an LLM would because it lacks deep semantic entity linking.
2. **Compute vs Accuracy**: We opted against fine-tuning a deep transformer model (like strict BERT) or requiring external vector databases (like Pinecone) primarily to respect the Assignment constraints: maintaining an easy "one-command" setup without burdening the evaluator's local workstation hardware. The speed/accuracy tradeoff heavily favors TF-IDF for rapid dashboard deployment.

## 🛠️ Architecture
- **Selenium Headless**: Orchestrated concurrent scraping via `ThreadPoolExecutor` targeting `data-engineer`, `sde`, and `junior` roles.
- **Supabase**: REST endpoints utilized instead of python SDK to circumvent native Windows C++ compiler constraints.
- **Streamlit Frontend**: Advanced `glassmorphism` aesthetic injections, fully responsive layout, and Top Horizontal Navigation via `streamlit-option-menu`.