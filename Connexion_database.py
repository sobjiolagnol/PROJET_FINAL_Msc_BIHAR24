import pandas as pd
import sqlite3
from io import StringIO


def Connexion():
    conn = sqlite3.connect('temperature_douala.db')
    dataset = pd.read_sql('SELECT * FROM temperature', conn)
    conn.close()

    # Convertir le DataFrame en une chaîne CSV
    save_csv = StringIO()
    dataset.to_csv(save_csv, index=False)

    save_csv.seek(0)

    return save_csv




