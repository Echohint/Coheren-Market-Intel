import os
import logging
import requests

logger = logging.getLogger(__name__)

def get_supabase_headers() -> dict:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Supabase credentials not found in environment.")
    
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

def upsert_jobs(jobs: list):
    """
    Upserts the list of cleaned job dicts into the 'job_listings' table using REST API.
    Expects 'id' as the primary key.
    """
    if not jobs:
        logger.info("No jobs to insert.")
        return
        
    url = os.getenv("SUPABASE_URL")
    if not url:
        return
        
    endpoint = f"{url}/rest/v1/job_listings"
    headers = get_supabase_headers()
    
    try:
        response = requests.post(endpoint, headers=headers, json=jobs)
        if response.status_code in [200, 201]:
            logger.info(f"Successfully upserted {len(jobs)} jobs to Supabase via REST API.")
            return response.json()
        elif response.status_code == 204:
            logger.info(f"Successfully upserted {len(jobs)} jobs to Supabase via REST API.")
            return []
        else:
            logger.error(f"Error from Supabase API ({response.status_code}): {response.text}")
    except Exception as e:
        logger.error(f"Exception communicating with Supabase: {e}")

def fetch_jobs():
    """
    Fetches all jobs from the 'job_listings' table for Streamlit using REST API.
    """
    url = os.getenv("SUPABASE_URL")
    if not url:
        return []
        
    endpoint = f"{url}/rest/v1/job_listings?order=date.desc"
    headers = get_supabase_headers()
    headers.pop("Prefer", None)  # Remove Prefer header for GET request
    
    try:
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error fetching from Supabase ({response.status_code}): {response.text}")
            return []
    except Exception as e:
        logger.error(f"Exception fetching from Supabase: {e}")
        return []
