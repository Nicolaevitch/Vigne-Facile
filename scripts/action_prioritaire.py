import sqlite3

# 📌 Connexion à la base SQLite
db_path = "/mnt/c/Users/33618/OneDrive/Documents/Cours Telecom/Datalake/project_datalake3/data/meteo.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 📌 Création de la table action_prioritaire qui dépend de meteo_data, actions_vigneron et stock
cursor.execute("""
CREATE TABLE IF NOT EXISTS action_prioritaire (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    periode TEXT NOT NULL,
    action_prioritaire TEXT NOT NULL,
    stock_necessaire TEXT NOT NULL,
    ressource_disponible TEXT NOT NULL,
    faisabilite TEXT NOT NULL,
    temps_trajet TEXT,
    etat_traffic TEXT
);
""")

# 📌 Déterminer l'action prioritaire en fonction de actions_vigneron
priorite_actions = ["🌿 Traitement de la vigne", "🪵 Planter des piquets", "🛠️ Poser du fil de fer", "🌾 Travailler la terre", "🏡 Travailler dans le chai"]

# 📌 Récupération des données avec jointures sécurisées
cursor.execute("""
SELECT a.date, a.periode, a.actions, 
       s.stock_produit, s.stock_essence, s.stock_sulfite, s.stock_piquet, s.stock_fil_de_fer, 
       COALESCE(r.temps_ravitaillement, '') AS temps_ravitaillement, 
       COALESCE(r.etat_traffic_ravitaillement, '') AS etat_traffic_ravitaillement, 
       COALESCE(r.temps_venue_tracteur, '') AS temps_venue_tracteur, 
       COALESCE(r.etat_traffic_tracteur, '') AS etat_traffic_tracteur
FROM actions_vigneron a
LEFT JOIN stock s ON a.date = s.date
LEFT JOIN acces_ressources r ON a.periode = r.periode;
""")
data = cursor.fetchall()

# 📌 Définition des ratios de consommation
def get_stock_requirements(action):
    stock_map = {
        "🌿 Traitement de la vigne": {"produit": 5, "essence": 3},
        "🪵 Planter des piquets": {"piquet": 15, "essence": 3},
        "🛠️ Poser du fil de fer": {"fil": 100},
        "🌾 Travailler la terre": {"essence": 3},
        "🏡 Travailler dans le chai": {"sulfite": 5}
    }
    return stock_map.get(action, {})

# 📌 Calcul et insertion des données
for row in data:
    date, periode, actions, stock_produit, stock_essence, stock_sulfite, stock_piquet, stock_fil_de_fer, \
    temps_ravitaillement, etat_traffic_ravitaillement, temps_venue_tracteur, etat_traffic_tracteur = row
    
    actions_possibles = actions.split(", ") if actions else []
    action_prioritaire = next((act for act in priorite_actions if act in actions_possibles), "Aucune")
    stock_needed = get_stock_requirements(action_prioritaire)
    
    # Calculer les ressources disponibles
    ressource_disponible = {
        "produit": stock_produit, "essence": stock_essence, "sulfite": stock_sulfite,
        "piquet": stock_piquet, "fil": stock_fil_de_fer
    }
    
    # Calcul de la faisabilité (priorité au pire état)
    faisabilite_result = "Stock ok"
    for key, value in stock_needed.items():
        if key in ressource_disponible and ressource_disponible[key] is not None:
            heures_restantes = ressource_disponible[key] / value
            if heures_restantes < 1:
                faisabilite_result = "Pas assez de stock"
                break
            elif heures_restantes < 4:
                faisabilite_result = "Stock limite"
    
    # Définir temps de trajet et état du trafic (laisser vide si non disponible)
    temps_trajet = temps_venue_tracteur if action_prioritaire == "🌿 Traitement de la vigne" else temps_ravitaillement
    etat_traffic = etat_traffic_tracteur if action_prioritaire == "🌿 Traitement de la vigne" else etat_traffic_ravitaillement
    
    # Insertion dans la table action_prioritaire
    cursor.execute("""
    INSERT INTO action_prioritaire (date, periode, action_prioritaire, stock_necessaire, ressource_disponible, faisabilite, temps_trajet, etat_traffic)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (date, periode, action_prioritaire, str(stock_needed), str(ressource_disponible), faisabilite_result, temps_trajet, etat_traffic))

# 📌 Valider et fermer la connexion
conn.commit()
conn.close()

print("✅ Table action_prioritaire mise à jour avec les actions prioritaires, les stocks et les données de trafic !")
