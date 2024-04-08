import preprocessing
from Connexion_database import Connexion
import statsmodels.api as sm
import pandas as pd
from sklearn.metrics import mean_squared_error

from statsmodels.tsa.arima.model import ARIMA

################################ Modele ARIMA

def Model_ARIMA(ts_train):
    # Modèle ARIMA
    arima_model = sm.tsa.ARIMA(ts_train, order=(2, 1, 2))
    arima_result = arima_model.fit()
    #arima_pred = arima_result.predict(start=len(ts_train), end=len(ts_train) + len(ts_test) - 1, typ='levels')
    return arima_result

############################### Modele SARIMA

def Model_SARIMA(ts_train):
    sarima_model = sm.tsa.SARIMAX(ts_train, order=(2, 1, 2), seasonal_order=(1, 1, 1, 12))
    sarima_result = sarima_model.fit()
    #sarima_pred = sarima_result.predict(start=len(ts_train), end=len(ts_train) + len(ts_test) - 1, typ='levels')
    return sarima_result

from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error

#################################### Modele SARIMAX

def Model_SARIMAX(ts_train,ts_val):
    ts_train_val = pd.concat([ts_train, ts_val], axis=0)
    best_order = (5, 0, 5)
    model_sarimax = SARIMAX(ts_train_val, order=best_order).fit()
    ts_pred = model_sarimax.predict(start=ts_test.index[0], end=ts_test.index[-1])
    rmse = mean_squared_error(ts_test.values, ts_pred.values, squared=False)
    print(f'SARIMAX{best_order}\nAIC={model_sarimax.aic:.2f}\nRMSE (test)={rmse:.2f}')
    return model_sarimax

########################## Regression lineaire

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

def Model_RegressionLineaire(X_train,y_train,X_test,y_test):
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    y_pred = lr.predict(X_test)
    print(f"Linear regression\n R^2={r2_score(y_test, y_pred):.2f}")
    return lr

############################## RandomForestRegressor

from sklearn.ensemble import RandomForestRegressor

def Model_RandomForest(X_train,y_train,X_test,y_test):
    rfr = RandomForestRegressor()
    rfr.fit(X_train, y_train)
    y_pred = rfr.predict(X_test)
    print(f"Random Forest regression\n R^2={r2_score(y_test, y_pred):.2f}")
    return rfr


################################ persitance des models ##################################################

import os
import joblib


def sauvegarder_modele(modele, chemin_dossier, nom_fichier):
    # Créer le dossier s'il n'existe pas
    if not os.path.exists(chemin_dossier):
        os.makedirs(chemin_dossier)

    # Chemin complet du fichier de sauvegarde
    chemin_complet = os.path.join(chemin_dossier, nom_fichier)

    # Sauvegarde du modèle
    joblib.dump(modele, chemin_complet)

    return chemin_complet

############################### TRAIN ###############################################################


donne = Connexion()
new_hourly_dataframe_diff, ts_train, ts_test = preprocessing.preprocess(donne)
X_train, X_test, y_train, y_test = preprocessing.preprocess_data(new_hourly_dataframe_diff)

directory = 'Modeles'

Model_RegressionLineaire=Model_RegressionLineaire(X_train,y_train,X_test,y_test)
sauvegarder_modele(Model_RegressionLineaire, directory, 'model_regression')

Model_ARIMA=Model_ARIMA(ts_train)
sauvegarder_modele(Model_ARIMA, directory, 'model_arima')


Model_SARIMA=Model_SARIMA(ts_train)
sauvegarder_modele(Model_SARIMA, directory, 'model_sarima')
'''
Model_RegressionLineaire=Model_RegressionLineaire(X_train,y_train,X_test,y_test)
sauvegarder_modele(Model_RegressionLineaire, directory, 'model_regression')

Model_RandomForest=Model_RandomForest(X_train,y_train,X_test,y_test)
sauvegarder_modele(Model_RandomForest, directory, 'randomforest')

'''