import time
import hashlib
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_job_hash(url):
    return hashlib.md5(url.encode()).hexdigest()

def scrape_jobs(url="https://remoteok.com/remote-data-engineer-jobs"):
    logger.info(f"Starting generic scrape for {url}")
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # Use a realistic user agent to avoid basic blocks
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    jobs = []
    
    try:
        driver.get(url)
        logger.info("Waiting for page completion...")
        time.sleep(5)  # Let dynamic content load
        
        # RemoteOK structure: rows with class 'job'
        job_elements = driver.find_elements(By.CSS_SELECTOR, "tr.job")
        logger.info(f"Found {len(job_elements)} job elements.")
        
        for el in job_elements:
            try:
                # Role and Company
                role = el.find_element(By.CSS_SELECTOR, "h2[itemprop='title']").text.strip()
                company = el.find_element(By.CSS_SELECTOR, "h3[itemprop='name']").text.strip()
                
                # Fetch Link to generate id
                link_el = el.find_element(By.CSS_SELECTOR, "td.company_and_position a.preventLink")
                job_url = link_el.get_attribute("href")
                job_id = get_job_hash(job_url)
                
                # Location and Salary are enclosed in div.location
                location_elements = el.find_elements(By.CSS_SELECTOR, "div.location")
                location = ""
                salary = ""
                for loc in location_elements:
                    text = loc.text.strip()
                    if ("$" in text or "€" in text or "£" in text) or ("k" in text.lower() and "-" in text):
                        salary = text
                    else:
                        location = text
                        
                # Tags
                tags_el = el.find_elements(By.CSS_SELECTOR, "td.tags .action-add-tag")
                tags = [t.text.strip() for t in tags_el if t.text.strip()]
                
                # Date (datetime attribute isn't strictly there always, fallback to text)
                try:
                    date_field = el.find_element(By.CSS_SELECTOR, "td.time time")
                    date = date_field.get_attribute("datetime")
                except:
                    date_field = el.find_element(By.CSS_SELECTOR, "td.time")
                    date = date_field.text.strip()
                
                jobs.append({
                    "id": job_id,
                    "role": role,
                    "company": company,
                    "location": location,
                    "salary": salary,
                    "tags": tags,
                    "date": date,
                    "url": job_url
                })
            except Exception as e:
                # Often table headers / ads share elements without attributes
                pass
                
        logger.info(f"Successfully extracted {len(jobs)} items.")
        return jobs
        
    finally:
        driver.quit()

if __name__ == "__main__":
    jobs = scrape_jobs()
    if jobs:
        print("First extracted job:")
        print(jobs[0])
