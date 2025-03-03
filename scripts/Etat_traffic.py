import sqlite3
import requests
from datetime import datetime

# 📌 Connexion à la base SQLite
db_path = "/mnt/c/Users/33618/OneDrive/Documents/Cours Telecom/Datalake/project_datalake3/data/meteo.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 📌 Création de la table acces_ressources avec une colonne date et periode
cursor.execute("""
CREATE TABLE IF NOT EXISTS acces_ressources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    periode TEXT NOT NULL,
    temps_ravitaillement REAL NOT NULL,
    etat_traffic_ravitaillement TEXT NOT NULL,
    temps_venue_tracteur REAL NOT NULL,
    etat_traffic_tracteur TEXT NOT NULL
);
""")

# 📅 Générer la date et l'heure actuelle au format YYYY-MM-DD HH:MM
current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M")

# 🕒 Déterminer la tranche horaire (2 heures)
current_hour = datetime.now().hour
start_hour = (current_hour // 2) * 2  # Trouver le début de la tranche horaire
end_hour = start_hour + 2
periode = f"{start_hour:02d}:00 - {end_hour:02d}:00"

# 🌍 Coordonnées pour le trajet normal (aller-retour)
latitude_depart_1 = 45.0064
longitude_depart_1 = -0.6195
latitude_arrivee_1 = 44.874427
longitude_arrivee_1 = -0.554835

# 🌾 Coordonnées pour le tracteur
latitude_depart_2 = 44.781587
longitude_depart_2 = -0.587752
latitude_arrivee_2 = 45.0064
longitude_arrivee_2 = -0.6195

# Vitesse maximale du tracteur
TRACTOR_MAX_SPEED = 25  # km/h

# Fonction pour récupérer les données OSRM
def get_route_data(start_lat, start_lon, end_lat, end_lon):
    url = f"https://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=false&annotations=speed,duration,distance"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Erreur dans la requête : {response.status_code}")
        return None

# Fonction pour analyser le trafic
def analyze_traffic(data):
    if not data:
        return None, None

    distance = data['routes'][0]['distance']  # en mètres
    duration = data['routes'][0]['duration'] / 60  # Convertir en minutes
    speed_kmh = (distance / (duration * 60)) * 3.6  # Convertir en km/h

    if speed_kmh >= 60:
        return duration, "OK ✅"
    elif speed_kmh >= 40:
        return duration, "Lent 🟠"
    else:
        return duration, "Critique 🔴"

# Fonction spécifique pour analyser le trafic du tracteur
def analyze_tractor_traffic(data):
    if not data:
        return None, None

    segments = data["routes"][0]["legs"][0]["annotation"]["speed"]
    total_distance = data['routes'][0]['distance'] / 1000  # Convertir en km

    slow_zones = [speed for speed in segments if speed < 15]
    risky_zones = [speed for speed in segments if 15 <= speed < 25]

    if len(slow_zones) > 0:
        avg_speed = 12
        traffic_status = "🚨 Bouchons critiques sur la route du tracteur"
    elif len(risky_zones) > 0:
        avg_speed = 18
        traffic_status = "⚠️ Attention : Risque de ralentissement pour le tracteur"
    else:
        avg_speed = TRACTOR_MAX_SPEED
        traffic_status = "✅ Route dégagée pour le tracteur"

    estimated_time = total_distance / avg_speed * 60  # Convertir en minutes
    return estimated_time, traffic_status

# 🔄 Calcul du trajet normal (aller-retour)
data_aller = get_route_data(latitude_depart_1, longitude_depart_1, latitude_arrivee_1, longitude_arrivee_1)
data_retour = get_route_data(latitude_arrivee_1, longitude_arrivee_1, latitude_depart_1, longitude_depart_1)

data_tractor = get_route_data(latitude_depart_2, longitude_depart_2, latitude_arrivee_2, longitude_arrivee_2)

# 📊 Résultats du trajet normal
if data_aller and data_retour:
    duration_aller, traffic_aller = analyze_traffic(data_aller)
    duration_retour, traffic_retour = analyze_traffic(data_retour)
    total_duration = (duration_aller + duration_retour)

# 📊 Résultat du trajet tracteur
if data_tractor:
    estimated_time_tractor, tractor_status = analyze_tractor_traffic(data_tractor)

# 📌 Insertion des données avec date et periode
cursor.execute("""
INSERT INTO acces_ressources (date, periode, temps_ravitaillement, etat_traffic_ravitaillement, temps_venue_tracteur, etat_traffic_tracteur)
VALUES (?, ?, ?, ?, ?, ?)
""", (current_datetime, periode, total_duration, traffic_aller, estimated_time_tractor, tractor_status))

# 📌 Valider et fermer la connexion
conn.commit()
conn.close()

print("✅ Données insérées dans acces_ressources avec date et période !")
