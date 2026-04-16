CREATE TABLE job_listings (
    id TEXT PRIMARY KEY,
    role TEXT,
    company TEXT,
    location TEXT,
    salary TEXT,
    salary_numeric INT,
    tags TEXT[],
    url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
