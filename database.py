import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry
import sqlite3
import csv

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
	"latitude": 3.8667,
	"longitude": 11.5167,
	"start_date": "2020-01-01",
	"end_date": "2023-12-31",
	"hourly": "temperature_2m"
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}
hourly_data["temperature_2m"] = hourly_temperature_2m

hourly_dataframe = pd.DataFrame(data = hourly_data)

# Écrire le DataFrame dans un fichier CSV
hourly_dataframe.to_csv('dataTemperature.csv', index=False)

# Connexion à la base de données
connect = sqlite3.connect('temperature_douala.db')
cursor = connect.cursor()

# Création de la table si elle n'existe pas déjà
cursor.execute('''CREATE TABLE IF NOT EXISTS temperature (

                    date TEXT,
                    temperature_2m REAL
                )''')


# Fonction pour insérer les données du CSV dans la base de données
def save_temperature(date, temperature_2m):
    cursor.execute('''INSERT INTO temperature (date, temperature_2m) VALUES (?, ?)''', (date, temperature_2m))
    connect.commit()


# Lecture du dataframe et insertion des données dans la base de données temperature_douala.db
with open('dataTemperature.csv', 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        date = row['date']
        temperature_2m = float(row['temperature_2m'])
        save_temperature(date, temperature_2m)

print("les données ont été sauvegardées dans le database avec succès")

# Fermeture de la connexion à la base de données
connect.close()
