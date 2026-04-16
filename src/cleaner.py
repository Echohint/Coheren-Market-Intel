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
    df['average_salary'] = df['salary'].apply(clean_salary)
    
    # Fill empty locations and salaries
    df['location'] = df['location'].replace({'': 'Remote'})
    df['salary'] = df['salary'].replace({'': 'Not Specified'})
    
    # Fill NA for average_salary
    # Supabase allows NULL/None natively, so we ensure pure NaN becomes None
    df['average_salary'] = df['average_salary'].where(pd.notnull(df['average_salary']), None)
    
    logger.info("Cleaning complete.")
    return df.to_dict(orient='records')

if __name__ == "__main__":
    test_data = [{"id":"123", "salary": "$100k - $150k", "location": "", "tags": ["python"]}]
    print(clean_data(test_data))
