import os
import requests
import pandas as pd
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp

# ⚡ Configuration du chemin du driver SQLite
os.environ["SPARK_CLASSPATH"] = "/mnt/c/Users/33618/OneDrive/Documents/Cours Telecom/Datalake/project_datalake3/jars/sqlite-jdbc-3.36.0.3.jar"

# ⚡ Initialisation de la session Spark avec le driver JDBC SQLite
spark = SparkSession.builder \
    .appName("MeteoDataProcessing") \
    .config("spark.jars", os.environ["SPARK_CLASSPATH"]) \
    .getOrCreate()

# 🌍 Coordonnées de localisation
latitude = 45.0064
longitude = -0.6195

# 🌦️ Requête à l'API Open-Meteo
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": latitude,
    "longitude": longitude,
    "hourly": "temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation_probability,precipitation,rain,snowfall,pressure_msl,wind_speed_10m",
    "forecast_days": 2,
    "timezone": "Europe/Paris"
}

response = requests.get(url, params=params)
data = response.json()

# 📅 Extraction des données horaires
hourly_data = data.get("hourly", {})
times = hourly_data.get("time", [])

# 📌 Transformer les données en dictionnaire structuré
structured_data = [
    {
        "timestamp": t,
        "temperature": hourly_data.get("temperature_2m", [])[i],
        "humidity": hourly_data.get("relative_humidity_2m", [])[i],
        "dew_point": hourly_data.get("dew_point_2m", [])[i],
        "apparent_temperature": hourly_data.get("apparent_temperature", [])[i],
        "precipitation_probability": hourly_data.get("precipitation_probability", [])[i],
        "precipitation": hourly_data.get("precipitation", [])[i],
        "rain": hourly_data.get("rain", [])[i],
        "snowfall": hourly_data.get("snowfall", [])[i],
        "pressure": hourly_data.get("pressure_msl", [])[i],
        "wind_speed": hourly_data.get("wind_speed_10m", [])[i]
    }
    for i, t in enumerate(times)
]

# 🗃️ Conversion en DataFrame Spark
df_spark = spark.createDataFrame(pd.DataFrame(structured_data))

# 🛠️ PRÉTRAITEMENT DES DONNÉES DANS SPARK
df_spark = df_spark.withColumn("timestamp", to_timestamp(col("timestamp")))

# 🔍 Vérifier le formatage et affichage des 5 premières lignes
df_spark.show(5)

# 🚀 Sauvegarde des données formatées en Parquet
output_path = "/mnt/c/Users/33618/OneDrive/Documents/Cours Telecom/Datalake/project_datalake3/data/formatted/meteo_data.parquet"
df_spark.write.mode("overwrite").parquet(output_path)
print(f"✅ Données enregistrées dans '{output_path}'.")

# --- Écriture dans SQLite ---
db_path = "/mnt/c/Users/33618/OneDrive/Documents/Cours Telecom/Datalake/project_datalake3/data/meteo.db"
table_name = "meteo_data"

try:
    df_spark.write \
        .format("jdbc") \
        .option("url", f"jdbc:sqlite:{db_path}") \
        .option("dbtable", table_name) \
        .option("driver", "org.sqlite.JDBC") \
        .mode("append") \
        .save()
    print(f"✅ Données écrites dans SQLite : {db_path}")
except Exception as e:
    print("❌ Erreur lors de l'écriture dans SQLite :", e)

# 🛑 Arrêt de la session Spark
spark.stop()