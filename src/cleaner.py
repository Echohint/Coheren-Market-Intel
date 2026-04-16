import pandas as pd
import re
import logging

logger = logging.getLogger(__name__)

def clean_salary(salary_str):
    """
    Takes a string like '$100k - $200k' and extracts an average numeric salary.
    Returns None if no standard salary is found.
    """
    if not salary_str:
        return None
        
    salary_str = salary_str.lower().replace(",", "")
    
    # Extract all numbers from the string
    numbers = re.findall(r'(\d+)', salary_str)
    if not numbers:
        return None
        
    # Convert 'k' representations (e.g. 100k -> 100000)
    # Actually, the numbers list just contains '100' and '200'
    # We should detect 'k' in the original string next to the number if possible,
    # But usually remoteok outputs '$100k - $200k'.
    vals = []
    for num_str in numbers:
        val = int(num_str)
        # Check if the text implies 'k' (very rudimentary)
        if 'k' in salary_str:
            if val < 1000: # Assuming it's in thousands
                val *= 1000
        vals.append(val)
        
    if vals:
        avg_sal = sum(vals) / len(vals)
        return avg_sal
    return None

def clean_data(raw_jobs: list) -> list:
    """
    Intakes a list of dicts, cleans the data using Pandas, and outputs
    a clean list of dicts ready for Database insertion.
    """
    logger.info(f"Cleaning {len(raw_jobs)} records...")
    if not raw_jobs:
        return []
        
    df = pd.DataFrame(raw_jobs)
    
    # Ensure tags is a list of strings, although it should already be.
    df['tags'] = df['tags'].apply(lambda x: x if isinstance(x, list) else [])
    
    # Calculate average salary
    df['salary_numeric'] = df['salary'].apply(clean_salary)
    # Convert to standard INT (handle NaN properly)
    df['salary_numeric'] = df['salary_numeric'].fillna(0).astype(int)
    # Set back to None if 0 to avoid false values in DB if it allows null
    df['salary_numeric'] = df['salary_numeric'].replace({0: None})

    # Fill empty locations and salaries
    df['location'] = df['location'].replace({'': 'Remote'})
    df['salary'] = df['salary'].replace({'': 'Not Specified'})
    
    # Drop date to match user job_listings schema which uses created_at
    if 'date' in df.columns:
        df = df.drop(columns=['date'])
        
    logger.info("Cleaning complete.")
    return df.to_dict(orient='records')

if __name__ == "__main__":
    test_data = [{"id":"123", "salary": "$100k - $150k", "location": "", "tags": ["python"]}]
    print(clean_data(test_data))
