import time
import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_job_hash(url):
    return hashlib.md5(url.encode()).hexdigest()

def scrape_category(url):
    logger.info(f"Starting scrape for {url}")
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    jobs = []
    
    try:
        driver.get(url)
        logger.info(f"[{url}] Waiting for page completion and scrolling for ~200+ jobs...")
        
        # Scroll 5 times to load infinite data
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
        # RemoteOK structure: rows with class 'job'
        job_elements = driver.find_elements(By.CSS_SELECTOR, "tr.job")
        logger.info(f"[{url}] Found {len(job_elements)} job elements.")
        
        for el in job_elements:
            try:
                role = el.find_element(By.CSS_SELECTOR, "h2[itemprop='title']").text.strip()
                company = el.find_element(By.CSS_SELECTOR, "h3[itemprop='name']").text.strip()
                
                link_el = el.find_element(By.CSS_SELECTOR, "td.company_and_position a.preventLink")
                job_url = link_el.get_attribute("href")
                job_id = get_job_hash(job_url)
                
                location_elements = el.find_elements(By.CSS_SELECTOR, "div.location")
                location = ""
                salary = ""
                for loc in location_elements:
                    text = loc.text.strip()
                    if "upgrade" in text.lower():
                        continue # Skip upgrade warnings
                    if ("$" in text or "€" in text or "£" in text) or ("k" in text.lower() and "-" in text):
                        salary = text
                    else:
                        location = text
                        
                tags_el = el.find_elements(By.CSS_SELECTOR, "td.tags .action-add-tag")
                tags = [t.text.strip() for t in tags_el if t.text.strip()]
                
                jobs.append({
                    "id": job_id,
                    "role": role,
                    "company": company,
                    "location": location,
                    "salary": salary,
                    "tags": tags,
                    "url": job_url
                })
            except Exception as e:
                pass
                
        logger.info(f"[{url}] Extracted {len(jobs)} items.")
        return jobs
        
    finally:
        driver.quit()

def scrape_jobs(urls=None):
    """
    Scalability Feature: Uses ThreadPoolExecutor to concurrently scrape multiple category pages.
    """
    if not urls:
        urls = ["https://remoteok.com/remote-data-engineer-jobs"]
        
    all_jobs = []
    # Using 3 workers to prevent hitting RemoteOK rate limits and high RAM usage
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(scrape_category, url): url for url in urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                jobs = future.result()
                all_jobs.extend(jobs)
            except Exception as exc:
                logger.error(f"[{url}] Generated an exception: {exc}")
                
    logger.info(f"Successfully extracted {len(all_jobs)} total items across all categories.")
    return all_jobs

if __name__ == "__main__":
    jobs = scrape_jobs()
    if jobs:
        print("First extracted job:")
        print(jobs[0])
