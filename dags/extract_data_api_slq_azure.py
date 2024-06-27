from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import requests
import pyodbc
import json

# Definir a função para extrair os dados da API
def extract_data():
    url = 'https://api.openbrewerydb.org/breweries'
    response = requests.get(url)
    data = response.json()
    return data

# Definir a função para inserir os dados no Azure SQL
def insert_data_to_azure_sql():
    # Configurar a string de conexão
    server = 'inbev-sql-server.database.windows.net'
    database = 'inbev_db'
    username = 'inbev_admin'
    password = 'Doni*****'
    driver = '{ODBC Driver 17 for SQL Server}'
 
    connection_string = f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}'

    # Conectar ao banco de dados
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    # Criar a tabela se não existir
    cursor.execute('''
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Breweries' and xtype='U')
    CREATE TABLE Breweries (
        id NVARCHAR(200) PRIMARY KEY,
        name NVARCHAR(255),
        brewery_type NVARCHAR(100),
        address_1 NVARCHAR(100),
        address_2 NVARCHAR(100),
        address_3 NVARCHAR(100),
        city NVARCHAR(100),
        state_province NVARCHAR(100),
        postal_code NVARCHAR(100),
        country NVARCHAR(100),
        longitude FLOAT,
        latitude FLOAT,
        phone NVARCHAR(20),
        website_url NVARCHAR(255),
        state NVARCHAR(100),
        street NVARCHAR(100)
    )
    ''')
       
    # Extrair os dados da função anterior
    data = extract_data()

    # Inserir dados na tabela
    for brewery in data:
        cursor.execute('''
        INSERT INTO Breweries (id,name,brewery_type,address_1,address_2,address_3,city,state_province,postal_code,country,longitude,latitude,phone,website_url,state,street )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        brewery['id'], brewery['name'], brewery['brewery_type'], brewery['address_1'], brewery['address_2'], brewery['address_3'], brewery['city'], brewery['state_province'], brewery['postal_code'], brewery['country'], brewery['longitude'], brewery['latitude'], brewery['phone'], brewery['website_url'], brewery['state'], brewery['street'])

    # Commitar as transações e fechar a conexão
    conn.commit()
    cursor.close()
    conn.close()

# Definir os argumentos padrão do DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
}

# Definir o DAG
with DAG(
    'insert_data_to_azure_sql_dag',
    default_args=default_args,
    description='Extrai dados da API e insere no banco de dados Azure SQL',
    schedule_interval='@daily',
    catchup=False
) as dag:

    # Definir as tarefas do DAG
    extract_task = PythonOperator(
        task_id='extract_data_task',
        python_callable=extract_data,
    )

    insert_task = PythonOperator(
        task_id='insert_data_to_azure_sql_task',
        python_callable=insert_data_to_azure_sql,
    )

    # Definir a ordem de execução das tarefas
    extract_task >> insert_task
