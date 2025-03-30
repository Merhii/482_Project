import requests
import pandas as pd 

import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

API_KEY = os.getenv("API_KEY")


LOCATION = "Beirut"
# URL = f"https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={LOCATION}&day=10"
# URL = f"https://api.weatherapi.com/v1/future.json?key={API_KEY}&q={LOCATION}&dt=2025-04-"

locations = ["Beirut", "Paris", "Riyad", "Cairo","LA"]
arr = []
for LOCATION in locations:
    URL = f"https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={LOCATION}&days=3"
    response = requests.get(URL)
    data = response.json()
 
    for forecast_day in data['forecast']['forecastday']:
        date = forecast_day['date']
        average_temp = forecast_day['day']['avgtemp_c']

        arr.append({
            "Date": date,
            "Average Temp": average_temp,
            "Location": LOCATION
        })
# Print the array or convert it to DataFrame
df = pd.DataFrame(arr)
print(df)
df.to_csv("weather.csv", mode='a', index=False, header=False)
