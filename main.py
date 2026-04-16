import os
from dotenv import load_dotenv
import logging
from src.scraper import scrape_jobs
from src.cleaner import clean_data
from src.database import upsert_jobs

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_pipeline():
    load_dotenv()
    logging.info("Starting ELT pipeline for RemoteOK...")
    
    # Set the target URLs to implement Fresher, SDE, and Data Engineering roles concurrently
    target_urls = [
        "https://remoteok.com/remote-data-engineer-jobs",
        "https://remoteok.com/remote-software-engineer-jobs",
        "https://remoteok.com/remote-junior-jobs"
    ]
    
    # Extract
    raw_data = scrape_jobs(target_urls)
    if not raw_data:
        logging.info("No data scraped. Exiting.")
        return
        
    # Transform
    clean_jobs = clean_data(raw_data)
    
    # Load
    upsert_jobs(clean_jobs)
    
    logging.info("Pipeline completed successfully!")

if __name__ == "__main__":
    run_pipeline()
