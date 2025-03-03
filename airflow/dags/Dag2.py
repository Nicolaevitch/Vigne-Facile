from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Définition du DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 2, 28),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'simple_meteo_dag',
    default_args=default_args,
    description='Un DAG qui exécute les scripts météo et actions chaque heure',
    schedule_interval='@hourly',
    catchup=False
)

# Tâche qui exécute le script de récupération des données météo
run_meteo_script = BashOperator(
    task_id='run_meteo_script',
    bash_command='python3 "/mnt/c/Users/33618/OneDrive/Documents/Cours Telecom/Datalake/project_datalake3/scripts/script_meteo.py"',
    dag=dag
)

# Tâche qui exécute le script de conseil d'actions après la météo
run_action_script = BashOperator(
    task_id='run_action_script',
    bash_command='python3 "/mnt/c/Users/33618/OneDrive/Documents/Cours Telecom/Datalake/project_datalake3/scripts/action_advice.py"',
    dag=dag
)

# Tâche qui exécute le script de définition de l'action prioritaire
run_action_prioritaire_script = BashOperator(
    task_id='run_action_prioritaire_script',
    bash_command='python3 "/mnt/c/Users/33618/OneDrive/Documents/Cours Telecom/Datalake/project_datalake3/scripts/action_prioritaire.py"',
    dag=dag
)

# Tâche qui envoie les données à Elasticsearch après la mise à jour des actions
send_to_elastic = BashOperator(
    task_id='send_to_elastic',
    bash_command='python3 "/mnt/c/Users/33618/OneDrive/Documents/Cours Telecom/Datalake/project_datalake3/scripts/send_to_elastic.py"',
    dag=dag
)

# Tâche indépendante qui exécute le script État du trafic
run_etat_traffic_script = BashOperator(
    task_id='run_etat_traffic_script',
    bash_command='python3 "/mnt/c/Users/33618/OneDrive/Documents/Cours Telecom/Datalake/project_datalake3/scripts/etat_traffic.py"',
    dag=dag
)

# Définition des dépendances
run_meteo_script >> run_action_script >> run_action_prioritaire_script >> send_to_elastic

# Le script État du trafic est exécuté indépendamment en parallèle
run_etat_traffic_script
