from fastapi import FastAPI
from pydantic import BaseModel
import joblib
from datetime import datetime
import pandas as pd
import sqlite3
from loguru import logger  # Importer Loguru
import uvicorn
from fastapi import Query
from typing import Optional

# Définition de la classe pour le corps de la requête
class dataInt(BaseModel):
    step: int
    start_date: str
    end_date: str

# Charger le modèle ARIMA
modele = joblib.load('Modeles/model_arima')

# Créer une instance de l'application FastAPI
app = FastAPI()

journalisation = "data/logs.log"
logger.add(journalisation, rotation="125 MB", retention="15 day", level="INFO")


def save_data(dates, predictions):
    df = pd.DataFrame({'date': dates, 'prediction': predictions})
    return df

def save_prediction_database(df, chemin='data'):

    try:
        conn = sqlite3.connect(chemin)
        df.to_sql('predictions', conn, if_exists='append', index=False)
        conn.close()
        print("Prédictions enregistrées avec succès dans la base de données.")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement des prédictions : {str(e)}")


@app.get("/")
def root():
    logger.info("connexion à la racine effectué avec succès")
    return {"message": "Bienvenue dans mon Api pour le projet BIHAR !"}

# Définir le point de terminaison pour les prédictions
@app.post("/predict")
async def predict(data: dataInt):
    try:
        logger.info(f"Prédictions pour les dates intervalle de date suivante {data.start_date} à {data.end_date}")
        # Convertir les dates en format datetime
        start_date = datetime.strptime(data.start_date, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(data.end_date, "%Y-%m-%d %H:%M:%S")

        # Liste pour stocker les dates et les prédictions
        dates = []
        predictions = []

        # Boucle pour calculer les prédictions pour chaque intervalle de 3 heures
        current_date = start_date
        while current_date <= end_date:
            # Faire la prédiction pour l'intervalle actuel
            prediction = modele.predict(start=current_date, end=current_date, dynamic=False)  # Sans prédiction dynamique

            # Ajouter la date et la prédiction aux listes
            dates.append(current_date)
            predictions.append(prediction[0])  # Prendre le premier élément de la prédiction

            # Passer à l'intervalle de 3 heures suivant

            current_date += pd.Timedelta(hours=3)
        logger.info("Prédictions effectuées avec succès")
        # Enregistrer les prédictions dans un DataFrame
        predictionsTemperature = save_data(dates, predictions)
        chemin_database = 'data/predictions.db'
        # Enregistrer les prédictions dans la base de données SQLite
        save_prediction_database(predictionsTemperature, chemin_database)

        return {"predictions": predictionsTemperature.to_dict(orient='records')}

    except Exception as e:
        logger.error(f"Erreur lors des prédictions : {str(e)}")
        return {"error": str(e)}

@app.get("/predictions")
async def get_predictions(start_date: Optional[str] = Query(None, description="Date de début au format YYYY-MM-DD"),
                          end_date: Optional[str] = Query(None, description="Date de fin au format YYYY-MM-DD")):
    try:
        #logger.info("Début de la récupération des prédictions depuis la base de données")

        # Construction de la requête SQL en fonction des paramètres
        conn = sqlite3.connect('data/predictions.db')
        if start_date and end_date:
            query = f"SELECT * FROM predictions WHERE date BETWEEN '{start_date}' AND '{end_date}'"
        elif start_date:
            query = f"SELECT * FROM predictions WHERE date >= '{start_date}'"
        elif end_date:
            query = f"SELECT * FROM predictions WHERE date <= '{end_date}'"
        else:
            query = "SELECT * FROM predictions"

        # Exécution de la requête SQL
        df_predictions = pd.read_sql_query(query, conn)
        conn.close()

        predictions_list = df_predictions.to_dict(orient='records')
        #logger.info("Prédictions récupérées avec succès depuis la base de données")
        return {"predictions": predictions_list}

    except Exception as e:
        #logger.error(f"Erreur lors de la récupération des prédictions : {str(e)}")
        return {"error": "Erreur lors de la récupération des prédictions"}




@app.get("/combined_predictions")
async def get_combined_predictions(start_date: Optional[str] = Query(None, description="Date de début au format YYYY-MM-DD"),
                                   end_date: Optional[str] = Query(None, description="Date de fin au format YYYY-MM-DD")):
    try:
        # Récupérer les prédictions à partir de la base de données pour la période donnée
        conn = sqlite3.connect('data/predictions.db')
        query = f"SELECT * FROM predictions WHERE date BETWEEN '{start_date}' AND '{end_date}'"
        df_predictions = pd.read_sql_query(query, conn)
        conn.close()

        # Charger les données réelles à partir du fichier CSV
        df_real_data = pd.read_csv('data/TemperatureReel.csv')

        # Fusionner les prédictions et les données réelles sur la colonne 'date'
        df_combined = pd.merge(df_predictions, df_real_data, on='date', how='inner')

        # Convertir le DataFrame combiné en une liste de dictionnaires
        combined_predictions_list = df_combined.to_dict(orient='records')

        return {"combined_predictions": combined_predictions_list}

    except Exception as e:
        return {"error": "Erreur lors de la récupération des prédictions combinées avec les données réelles."}


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
