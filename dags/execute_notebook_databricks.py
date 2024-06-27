from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from airflow.utils.dates import days_ago

# Definindo o DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
}

dag = DAG(
    'databricks_notebook_dag',
    default_args=default_args,
    description='Executa um notebook no Databricks',
    schedule_interval='@daily',
    catchup=False
)

# Configurações para executar o notebook no Databricks
notebook_task_params = {
    'existing_cluster_id': '0626-205409-935ntddc',
    'notebook_task': {
        'notebook_path': '/Workspace/Users/contatocappelletto@outlook.com/inbev_process_silver'
    }
}

# Definindo a tarefa para executar o notebook no Databricks
run_notebook = DatabricksRunNowOperator(
    task_id='run_databricks_notebook',
    databricks_conn_id='databricks_default',
    job_id='493309520753041',
    notebook_params=notebook_task_params,
    dag=dag,
)

run_notebook
