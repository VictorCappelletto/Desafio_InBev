
from airflow import DAG
from airflow.providers.microsoft.azure.operators.data_factory import AzureDataFactoryRunPipelineOperator
from airflow.utils.dates import days_ago

# Configurações do Azure Data Factory
adf_pipeline_name = 'Pipeline1'
adf_resource_group_name = 'inbev_resource_group'
adf_factory_name = 'inbev-data-factory'

# Definindo o DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
}

dag = DAG(
    'trigger_data_factory_azure',
    default_args=default_args,
    description='Executa a pipeline do Azure Data Factory',
    schedule_interval='@daily',
)

# Definindo a tarefa para executar a pipeline do ADF
trigger_pipeline = AzureDataFactoryRunPipelineOperator(
    task_id='run_adf_pipeline',
    pipeline_name=adf_pipeline_name,
    resource_group_name=adf_resource_group_name,
    factory_name=adf_factory_name,
    dag=dag,
)

