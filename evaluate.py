import preprocessing
import Connexion_database
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import joblib

# Fonction pour le chargement du modele
def charger_modele(chemin_fichier):
    modele = joblib.load(chemin_fichier)
    return modele

# Fonction pour évaluer le modèle ARIMA
def evaluer_modele_arima(modele_arima, ts_test):
    debut_index = ts_test.index[0]
    fin_index = ts_test.index[-1]
    # Effectuer les prédictions en utilisant le modèle ARIMA ajusté
    ts_pred = modele_arima.predict(start=debut_index, end=fin_index, typ='levels')
    # Calculer les métriques de performance
    rmse = np.sqrt(mean_squared_error(ts_test, ts_pred))
    r2s = r2_score(ts_test, ts_pred)
    return ts_pred, rmse, r2s

# Fonction pour évaluer le modèle SARIMA
def evaluer_modele_sarima(modele_sarima, ts_test):
    debut_index = ts_test.index[0]
    fin_index = ts_test.index[-1]
    # Effectuer les prédictions en utilisant le modèle SARIMA ajusté
    ts_pred = modele_sarima.predict(start=debut_index, end=fin_index)
    # Calculer les métriques de performance
    rmse = np.sqrt(mean_squared_error(ts_test, ts_pred))
    r2s = r2_score(ts_test, ts_pred)
    return ts_pred, rmse, r2s

# Fonction pour évaluer un modèle de régression
def evaluate_model(model, X, y):
    print("Evaluating the model")
    y_pred = model.predict(X)
    score = r2_score(y, y_pred)
    return score

# Connexion à la base de données et prétraitement des données
donne = Connexion_database.Connexion()
new_hourly_dataframe_diff, ts_train, ts_test = preprocessing.preprocess(donne)
X_train, X_test, y_train, y_test = preprocessing.preprocess_data(new_hourly_dataframe_diff)

# Chargement du modèle de régression linéaire
modele_regression = charger_modele('Modeles/model_regression')
score_regression = evaluate_model(modele_regression, X_test, y_test)
print(f"Score for Linear Regression Model: {score_regression}")

# Chargement du modèle ARIMA
modele_arima = charger_modele('Modeles/model_arima')
ts_pred_arima, rmse_arima, r2s_arima = evaluer_modele_arima(modele_arima, ts_test)
print(f"Performance du modèle ARIMA :\nRMSE : {rmse_arima}\nR-squared : {r2s_arima}")

# Chargement du modèle SARIMA
modele_sarima = charger_modele('Modeles/model_sarima')
ts_pred_sarima, rmse_sarima, r2s_sarima = evaluer_modele_sarima(modele_sarima, ts_test)
print(f"Performance du modèle SARIMA :\nRMSE : {rmse_sarima}\nR-squared : {r2s_sarima}")
