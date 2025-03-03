#!/bin/bash

echo "🔄 Arrêt de Kibana avant redémarrage..."
sudo systemctl stop kibana

echo "🔄 Redémarrage d'Elasticsearch..."
sudo systemctl start elasticsearch

# 🔍 Attendre qu'Elasticsearch démarre complètement avant de lancer Kibana
echo "⏳ Attente du démarrage complet d'Elasticsearch..."
while ! curl -s http://localhost:9200 >/dev/null; do
    sleep 5
done
echo "✅ Elasticsearch est bien démarré."

# ⏸️ Pause pour éviter les conflits de démarrage
sleep 10

echo "🔄 Lancement de Kibana..."
sudo systemctl start kibana

# 🔍 Attendre que Kibana soit bien lancé
echo "⏳ Vérification du démarrage de Kibana..."
while ! curl -s http://localhost:5601 >/dev/null; do
    sleep 5
done
echo "✅ Kibana est bien démarré."

# Vérifier le statut d'Elasticsearch et Kibana
if systemctl is-active --quiet elasticsearch; then
    echo "✅ Elasticsearch tourne bien."
else
    echo "❌ Erreur : Elasticsearch ne s'est pas correctement lancé."
fi

if systemctl is-active --quiet kibana; then
    echo "✅ Kibana tourne bien."
else
    echo "❌ Erreur : Kibana ne s'est pas correctement lancé."
fi

echo "🔄 Redémarrage d'Airflow Webserver et Scheduler..."
airflow db upgrade  # Vérifier et mettre à jour la base de données d'Airflow
airflow webserver -D
airflow scheduler -D

# Attendre qu'Airflow démarre correctement
echo "⏳ Vérification du démarrage d'Airflow..."
sleep 10

# Vérifier si les processus Airflow sont bien en cours d'exécution
if pgrep -f "airflow webserver" > /dev/null; then
    echo "✅ Airflow Webserver est bien démarré."
else
    echo "❌ Erreur : Airflow Webserver ne s'est pas correctement lancé."
fi

if pgrep -f "airflow scheduler" > /dev/null; then
    echo "✅ Airflow Scheduler est bien démarré."
else
    echo "❌ Erreur : Airflow Scheduler ne s'est pas correctement lancé."
fi

# 🌐 Afficher l'URL du Webserver Airflow
echo "🌍 Accédez à l'interface Web d'Airflow ici : http://localhost:8080"

# 🔍 Afficher la liste des utilisateurs Airflow
echo "👤 Liste des utilisateurs Airflow :"
airflow users list

# 🗃️ Afficher les tables SQLite et leur nombre de lignes
echo "📂 Liste des tables SQLite et nombre de lignes :"
sqlite3 "/mnt/c/Users/33618/OneDrive/Documents/Cours Telecom/Datalake/project_datalake3/data/meteo.db" "
.tables"
echo "➡️ Si nécessaire, relance avec le nom des tables pour afficher les lignes."

# 🛠️ Vérifier le nombre de documents indexés dans Elasticsearch
echo "🔍 Nombre de documents indexés dans Elasticsearch :"
curl -s "http://localhost:9200/_cat/indices?v" | grep -E "action_prioritaire|actions_vigneron|meteo_data"

# 🌍 Afficher l'URL de Kibana
echo "🌍 Accédez à l'interface Kibana ici : http://localhost:5601"

echo "🎉 Tous les services ont été redémarrés avec succès !"
