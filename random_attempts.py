from google import genai
import time
import os
from dotenv import load_dotenv
from edgar import set_identity, Company
import pandas as pd
from sqlalchemy import create_engine, text
import query_import as q
import urllib.parse
load_dotenv()


user=os.getenv("PGUSER")
password=os.getenv("PGPASSWORD")
safe_password = urllib.parse.quote_plus(password)
host=os.getenv("PGHOST")
port=os.getenv("PGPORT")
dbname=os.getenv("PGDATABASE")
engine = create_engine(f"postgresql://{user}:{safe_password}@{host}:{port}/{dbname}")

with engine.connect() as conn:
    variables = {
    "company_match": "%pfizer%",  # The % wildcards stay in the Python string value
    "year_start": "2025-01-01",
    "year_end": "2025-12-31",
}
    result = conn.execute(text(q.text), variables)
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    print(df)