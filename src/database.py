import os
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Supabase credentials not found in environment.")
    return create_client(url, key)

def upsert_jobs(jobs: list):
    """
    Upserts the list of cleaned job dicts into the 'jobs' table.
    Expects 'id' as the primary key.
    """
    if not jobs:
        logger.info("No jobs to insert.")
        return
        
    try:
        supabase = get_supabase_client()
        # Perform upsert
        response = supabase.table('jobs').upsert(jobs).execute()
        logger.info(f"Successfully upserted {len(jobs)} jobs to Supabase.")
        return response
    except Exception as e:
        logger.error(f"Error communicating with Supabase: {e}")

def fetch_jobs():
    """
    Fetches all jobs from the 'jobs' table for Streamlit.
    """
    try:
        supabase = get_supabase_client()
        response = supabase.table('jobs').select('*').order('date', desc=True).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error fetching from Supabase: {e}")
        return []
