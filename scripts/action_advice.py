import sqlite3
import pandas as pd

# 📌 Connexion à la base SQLite
db_path = "/mnt/c/Users/33618/OneDrive/Documents/Cours Telecom/Datalake/project_datalake3/data/meteo.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 📌 Création de la table actions_vigneron si elle n'existe pas
cursor.execute("""
CREATE TABLE IF NOT EXISTS actions_vigneron (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    periode TEXT NOT NULL,
    temperature REAL,
    vent REAL,
    humidite REAL,
    pluie REAL,
    neige REAL,
    actions TEXT NOT NULL,
    raison TEXT NOT NULL
);
""")

# 📌 Récupérer les données météo
query = """
SELECT datetime(timestamp / 1000, 'unixepoch', 'localtime') as date_time, 
       temperature, wind_speed, humidity, precipitation, snowfall
FROM meteo_data;
"""
df_meteo = pd.read_sql(query, conn)

# Transformer la colonne date_time en datetime
from datetime import datetime

df_meteo['date_time'] = pd.to_datetime(df_meteo['date_time'])
df_meteo['date'] = df_meteo['date_time'].dt.date
df_meteo['hour'] = df_meteo['date_time'].dt.hour

# Filtrer pour ne garder que les horaires entre 06h et 21h
df_meteo = df_meteo[(df_meteo['hour'] >= 6) & (df_meteo['hour'] <= 21)]

def determine_actions(row):
    """Détermine les actions possibles en fonction des conditions météo."""
    actions = []
    raisons = []
    
    # Conditions bloquantes
    if row['snowfall'] > 0 or row['precipitation'] > 10:
        return "🚫 Aucune action (neige ou trop de pluie)", "Neige ou précipitations excessives"
    
    # Traitement de la vigne (prioritaire)
    if row['wind_speed'] < 10 and row['humidity'] < 70 and row['precipitation'] == 0 and row['snowfall'] == 0:
        return "🌿 Traitement de la vigne", "Conditions idéales : pas de vent, faible humidité, pas de précipitations"
    
    # Autres actions possibles
    if row['humidity'] > 80 or row['precipitation'] > 2:
        actions.append("🛠️ Poser du fil de fer")
        raisons.append("Humidité élevée ou précipitations modérées")
    if row['humidity'] > 70 and row['precipitation'] < 5:
        actions.append("🪵 Planter des piquets")
        raisons.append("Sol humide, précipitations faibles")
        raisons.append("Vent fort ou froid avec précipitations")
    if row['humidity'] > 60 and row['precipitation'] < 5:
        actions.append("🌾 Travailler la terre")
        raisons.append("Humidité du sol favorable")
    
    return ", ".join(actions) if actions else "🏡 Travailler dans le chai", ", ".join(raisons) if raisons else "Pas de conditions favorables"

# Appliquer la fonction pour déterminer les actions
df_meteo[['actions', 'raison']] = df_meteo.apply(lambda row: pd.Series(determine_actions(row)), axis=1)

def get_period(hour):
    start_hour = (hour // 2) * 2  # Forcer des périodes de 2 heures
    end_hour = start_hour + 2
    return f"{start_hour:02d}:00 - {end_hour:02d}:00"

df_meteo['periode'] = df_meteo['hour'].apply(get_period)

# Grouper par date et période et choisir l'action dominante
df_final = df_meteo.groupby(['date', 'periode'])[['temperature', 'wind_speed', 'humidity', 'precipitation', 'snowfall', 'actions', 'raison']].first().reset_index()

# Insérer dans la table actions_vigneron
for _, row in df_final.iterrows():
    cursor.execute("""
        INSERT OR REPLACE INTO actions_vigneron (date, periode, temperature, vent, humidite, pluie, neige, actions, raison)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (row['date'], row['periode'], row['temperature'], row['wind_speed'], row['humidity'], row['precipitation'], row['snowfall'], row['actions'], row['raison']))

# 📌 Valider et fermer la connexion
conn.commit()
conn.close()

print("✅ Actions générées et enregistrées dans la table actions_vigneron avec des périodes de 2h.")
