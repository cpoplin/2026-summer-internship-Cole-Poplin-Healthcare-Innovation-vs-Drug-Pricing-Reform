from google import genai
import os
from dotenv import load_dotenv
from edgar import set_identity, Company
import pandas as pd
from sqlalchemy import create_engine, text
import urllib.parse
import query_import as q
import util
load_dotenv()

# Set SEC User agent identity
name=os.getenv("NAME")
email=os.getenv("EMAIL")
set_identity(f"{name}, {email}")

#initiate gemini api connection
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

#open postgres db connection
user=os.getenv("PGUSER")
password=os.getenv("PGPASSWORD")
safe_password = urllib.parse.quote_plus(password)
host=os.getenv("PGHOST")
port=os.getenv("PGPORT")
dbname=os.getenv("PGDATABASE")
engine = create_engine(f"postgresql://{user}:{safe_password}@{host}:{port}/{dbname}")



def revenue_breakdown_and_rnd(company_name,year):
    print("Gathering 10-K data...")
    #Fetch 10-K for AAPL
    company_name = util.toStockTickerUtil(company_name.lower())
    company = Company(company_name)
    filings = company.get_filings(form="10-K", filing_date=f"{year}-01-01:{year}-12-31")
    filings = filings[0]
    tenk = filings.obj()
    mda = tenk["Item 7"]

    #ask gemini to process
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=[
            mda,
            """Analyze this document and extract the amount of revenue from each drug, 
            then class each drug as either small molecule or large molecule based on fda databases if necessary, 
            including antibody drug conjugates as large molecules.  Give two conclusive numbers 
            for this, as well as a third for the company's listed RND spend for the year as full integers 
            in the format: 
            Small molecule revenue:123456789; 
            Large molecule revenue:123456789;
            RND spend:123456789;"""
        ]
    )

    #extract the desired data
    import re
    response_str = response.text
    raw_small = response_str.split("Small molecule revenue:")[1].split(";")[0]
    raw_large = response_str.split("Large molecule revenue:")[1].split(";")[0]
    raw_rnd = response_str.split("RND spend:")[1].split(";")[0]

    small_molecule = int(re.sub(r"[^\d]", "", raw_small)) if re.sub(r"[^\d]", "", raw_small) else 0
    large_molecule = int(re.sub(r"[^\d]", "", raw_large)) if re.sub(r"[^\d]", "", raw_large) else 0
    rnd_spend = int(re.sub(r"[^\d]", "", raw_rnd)) if re.sub(r"[^\d]", "", raw_rnd) else 0
    print("Raw Output:")
    print(response_str)
    print("Small Molecule Revenue: $")
    print(small_molecule)
    print("Large Molecule Revenue: $")
    print(large_molecule)
    print("RND Spend: $")
    print(rnd_spend)

    #track token usage
    print(f"Prompt (Input) Tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Candidates (Output) Tokens: {response.usage_metadata.candidates_token_count}")
    print(f"Total Tokens: {response.usage_metadata.total_token_count}")


def query_and_return_total_patient_months_for_each_sector(company_name, year):
    with engine.connect() as conn:
        company_name = company_name.lower()
        variables = {
            "company_match": f"%{company_name}%",
            "year_start": f"{year}-01-01",
            "year_end": f"{year}-12-31"
        }
        result = conn.execute(text(q.text), variables)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

        # Convert patient_months_given_year to numeric for summation
        df['patient_months_given_year'] = pd.to_numeric(df['patient_months_given_year'], errors='coerce').fillna(0)

        # Classify each row as DRUG (small molecule) or BIOLOGICAL (large molecule / other) using batch ChEMBL API lookups
        unique_drugs = [d for d in df['drug_name'].dropna().unique() if isinstance(d, str)]
        type_map = util.get_molecule_types_batch(unique_drugs)

        def get_final_class(drug_name):
            mol_type = type_map.get(drug_name, "Drug not found in ChEMBL")
            if mol_type == "Small Molecule":
                return "DRUG"
            else:
                return "BIOLOGICAL"

        drug_class_map = {drug: get_final_class(drug) for drug in unique_drugs}
        df['intervention_type'] = df['drug_name'].map(drug_class_map).fillna(df['intervention_type'])

        print("\n--- Reclassified DataFrame (DRUG = Small Molecule, BIOLOGICAL = Large Molecule) ---")
        print(df)

        # Compute totals for BIOLOGICAL and DRUG
        large_molecule_total = df[df['intervention_type'] == 'BIOLOGICAL']['patient_months_given_year'].sum()
        small_molecule_total = df[df['intervention_type'] == 'DRUG']['patient_months_given_year'].sum()
        total_patient_months = large_molecule_total + small_molecule_total

        print(f"\nTotal Patient Months for Large Molecule: {large_molecule_total}")
        print(f"Total Patient Months for Small Molecule: {small_molecule_total}")
        print(f"Estimated percent of RND spent on small molecules: {small_molecule_total / total_patient_months * 100}%")
        print(f"Estimated percent of RND spent on large molecules: {large_molecule_total / total_patient_months * 100}%")
        
#something is wrong with the patient months calc I imagine, either that or pfizer
#is like the only one that properly lists DRUG vs BIOLOGIC
revenue_breakdown_and_rnd("eli lilly", 2020)
query_and_return_total_patient_months_for_each_sector("eli lilly", 2020)

