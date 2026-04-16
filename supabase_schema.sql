-- Execute this script in your Supabase SQL Editor to create the necessary table

CREATE TABLE public.jobs (
    id text not null primary key,
    role text,
    company text,
    location text,
    salary text,
    average_salary numeric,
    tags text[],
    date text,
    url text
);

-- Note: average_salary is calculated by pandas during the ETL pipeline.
