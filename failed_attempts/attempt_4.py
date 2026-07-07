import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
import requests

load_dotenv(dotenv_path="apikey.env")
API_KEY = os.getenv("API_KEY")

symbol = "JNJ"
#url = f"https://financialmodelingprep.com/api/v3/historical-market-capitalization/{symbol}?limit=100&apikey={API_KEY}"
url = f"https://financialmodelingprep.com/stable/income-statement?symbol={symbol}&apikey={API_KEY}"
data = requests.get(url).json()
print(data)