import sqlite3
from elasticsearch import Elasticsearch, helpers

# 📌 Connexion à SQLite
db_path = "/mnt/c/Users/33618/OneDrive/Documents/Cours Telecom/Datalake/project_datalake3/data/meteo.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 📌 Connexion à Elasticsearch
es = Elasticsearch("http://localhost:9200")

### **🔹 Envoi des données action_prioritaire dans Elasticsearch** ###
# 🔍 Récupérer les données de la table action_prioritaire
cursor.execute("SELECT * FROM action_prioritaire")
rows_action_prioritaire = cursor.fetchall()

# 🏗️ Définir les colonnes de la table action_prioritaire
columns_action_prioritaire = [
    "id", "date", "periode", "action_prioritaire", "stock_necessaire", "ressource_disponible", "faisabilite"
]

# 📦 Préparer les données pour Elasticsearch
actions_prioritaires = [
    {
        "_index": "action_prioritaire",
        "_source": dict(zip(columns_action_prioritaire, row))
    }
    for row in rows_action_prioritaire
]

# 🚀 Envoi des données action_prioritaire
try:
    helpers.bulk(es, actions_prioritaires)
    print("✅ Données action_prioritaire envoyées vers Elasticsearch !")
except Exception as e:
    print("❌ Erreur lors de l'envoi des données action_prioritaire :", e)

### **🔹 Envoi des données actions_vigneron dans Elasticsearch** ###
# 🔍 Récupérer les données de la table actions_vigneron
cursor.execute("SELECT * FROM actions_vigneron")
rows_actions_vigneron = cursor.fetchall()

# 🏗️ Définir les colonnes de la table actions_vigneron
columns_actions_vigneron = [
    "id", "date", "periode", "temperature", "vent", "humidite", "pluie", "neige", "actions", "raison"
]

# 📦 Préparer les données pour Elasticsearch
actions_vigneron = [
    {
        "_index": "actions_vigneron",
        "_source": dict(zip(columns_actions_vigneron, row))
    }
    for row in rows_actions_vigneron
]

# 🚀 Envoi des données actions_vigneron
try:
    helpers.bulk(es, actions_vigneron)
    print("✅ Données actions_vigneron envoyées vers Elasticsearch !")
except Exception as e:
    print("❌ Erreur lors de l'envoi des données actions_vigneron :", e)

# 🛑 Fermer la connexion SQLite
conn.close()
