import requests

def toStockTickerUtil(company_name):
    if company_name == "abbvie":
        return "ABBV"
    elif company_name == "eli lilly":
        return "LLY"
    elif company_name == "amgen":
        return "AMGN"
    elif company_name == "regeneron":
        return "REGN"
    elif company_name == "merck":
        return "MRK"
    elif company_name == "bristol myers squibb":
        return "BMY"
    elif company_name == "gilead":
        return "GILD"
    elif company_name == "vertex":
        return "VRTX"
    elif company_name == "pfizer":
        return "PFE"
    elif company_name == "abbvie":
        return "ABBV"
    


def get_molecule_types_batch(drug_names):
    """
    Batches ChEMBL API lookup for a list of drug names into chunked batch HTTP requests
    instead of hundreds of individual requests.
    Returns a dictionary mapping {drug_name: molecule_type_string}.
    """
    if not drug_names:
        return {}

    clean_names = [d.strip() for d in drug_names if d and isinstance(d, str) and d.strip()]
    if not clean_names:
        return {}

    results = {}
    url = "https://www.ebi.ac.uk/chembl/api/data/molecule"
    chunk_size = 40
    unmatched_names = set(clean_names)

    # 1. Batch query with pref_name__in
    for i in range(0, len(clean_names), chunk_size):
        chunk = clean_names[i:i + chunk_size]
        query_str = ",".join([c.upper() for c in chunk])
        try:
            res = requests.get(url, params={"pref_name__in": query_str, "format": "json", "limit": 1000}, timeout=10).json()
            for mol in res.get('molecules', []):
                pref_name = mol.get('pref_name', '').upper()
                mol_type = mol.get('molecule_type', '')
                type_str = "Small Molecule" if (mol_type and mol_type.lower() == 'small molecule') else f"Large Molecule ({mol_type})"
                for orig_name in chunk:
                    if orig_name.upper() == pref_name:
                        results[orig_name] = type_str
                        unmatched_names.discard(orig_name)
        except Exception:
            pass

    # 2. Batch query for remaining unmatched with molecule_synonyms__molecule_synonym__in
    unmatched_list = list(unmatched_names)
    for i in range(0, len(unmatched_list), chunk_size):
        chunk = unmatched_list[i:i + chunk_size]
        query_str = ",".join([c.upper() for c in chunk])
        try:
            res = requests.get(url, params={"molecule_synonyms__molecule_synonym__in": query_str, "format": "json", "limit": 1000}, timeout=10).json()
            for mol in res.get('molecules', []):
                mol_type = mol.get('molecule_type', '')
                type_str = "Small Molecule" if (mol_type and mol_type.lower() == 'small molecule') else f"Large Molecule ({mol_type})"
                synonyms = [s.get('molecule_synonym', '').upper() for s in mol.get('molecule_synonyms', []) if s.get('molecule_synonym')]
                pref_name = mol.get('pref_name', '').upper()
                for orig_name in chunk:
                    orig_upper = orig_name.upper()
                    if orig_upper in synonyms or orig_upper == pref_name:
                        results[orig_name] = type_str
                        unmatched_names.discard(orig_name)
        except Exception:
            pass

    # Default remaining unmatched drugs to "Drug not found in ChEMBL"
    for name in unmatched_names:
        results[name] = "Drug not found in ChEMBL"

    return results


def get_molecule_type(drug_name):
    # Single-drug wrapper using batch logic
    res = get_molecule_types_batch([drug_name])
    return res.get(drug_name, "Drug not found in ChEMBL")

if __name__ == "__main__":
    # Examples
    print(f"Aspirin: {get_molecule_type('Aspirin')}")
    print(f"Adalimumab: {get_molecule_type('Adalimumab')}")