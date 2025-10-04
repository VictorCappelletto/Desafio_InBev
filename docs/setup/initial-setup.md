# Setup Inicial

## 🎯 Pré-requisitos

Antes de começar, certifique-se de ter:

- ✅ **Python 3.11+**
- ✅ **Docker & Docker Compose**
- ✅ **Astronomer CLI** (opcional, mas recomendado)
- ✅ **Poetry** (gerenciador de dependências Python)
- ✅ **Git**

## 📥 Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/victorcappelleto/Desafio_InBev.git
cd Desafio_InBev
```

### 2. Instale Astronomer CLI

=== "macOS"

    ```bash
    brew install astro
    ```

=== "Linux"

    ```bash
    curl -sSL install.astronomer.io | sudo bash -s
    ```

=== "Windows"

    ```powershell
    winget install -e --id Astronomer.Astro
    ```

### 3. Configure Variáveis de Ambiente

```bash
# Copie o template
cp env.template .env

# Edite com suas credenciais
nano .env  # ou vim, code, etc
```

**Exemplo de `.env`:**
```bash
# Azure SQL
AZURE_SQL_PASSWORD=SuaSenhaSegura

# Databricks
DATABRICKS_HOST=https://adb-12345.azuredatabricks.net
DATABRICKS_TOKEN=dapi1234567890abcdef
DATABRICKS_CLUSTER_ID=1234-567890-abcd1234
DATABRICKS_JOB_ID=1234567890123
DATABRICKS_NOTEBOOK_PATH=/Workspace/Users/seu.email@empresa.com/notebook

# Azure Data Factory
ADF_TENANT_ID=12345678-1234-1234-1234-123456789012
ADF_SUBSCRIPTION_ID=12345678-1234-1234-1234-123456789012
ADF_CLIENT_ID=12345678-1234-1234-1234-123456789012
ADF_CLIENT_SECRET=SeuClientSecret
```

!!! warning "Segurança"
    **NUNCA** commite o arquivo `.env`! Ele já está no `.gitignore`.

### 4. Inicie o Ambiente Airflow

```bash
# Com Astronomer CLI (recomendado)
astro dev start

# Ou com Docker Compose puro
docker-compose up -d
```

### 5. Acesse a Interface Web

```bash
# Abra no navegador
open http://localhost:8080

# Ou
# http://localhost:8080
```

**Credenciais padrão:**
- **Username:** `admin`
- **Password:** `admin`

## ✅ Verificação

### 1. Verifique os Containers

```bash
astro dev ps

# Deve mostrar:
# - webserver (porta 8080)
# - scheduler
# - postgres
# - triggerer
```

### 2. Verifique as DAGs

```bash
# Liste as DAGs
astro dev run dags list

# Deve mostrar:
# - brewery_etl_solid
# - databricks_processing_solid
# - azure_data_factory_solid
```

### 3. Teste uma Conexão

```bash
# Teste a conexão Azure SQL
astro dev run connections test azure_sql_default

# Deve retornar: Connection successfully tested
```

### 4. Verifique ODBC Driver

```bash
# Entre no container
astro dev bash

# Verifique drivers instalados
odbcinst -q -d

# Deve mostrar: [ODBC Driver 18 for SQL Server]
```

## 🔧 Configuração Adicional

### Pools

Os pools já estão pré-configurados em `airflow_settings.yaml`:

```yaml
pools:
  - pool_name: azure_pool
    pool_slot: 5
  - pool_name: databricks_pool
    pool_slot: 3
```

**Verificar pools:**
```bash
astro dev run pools list
```

### Variables

As variables também estão pré-configuradas:

```bash
# Listar variables
astro dev run variables list

# Deve mostrar:
# - databricks_cluster_id
# - databricks_job_id
# - databricks_notebook_path
# - adf_resource_group
# ...
```

### Connections

Conexões pré-configuradas:
- `azure_sql_default` - Azure SQL Database
- `databricks_default` - Databricks
- `azure_data_factory_default` - Azure Data Factory

**Verificar connections:**
```bash
astro dev run connections list
```

## 🚀 Primeira Execução

### 1. Ative uma DAG

Na interface web:
1. Navegue para http://localhost:8080
2. Encontre `brewery_etl_solid`
3. Toggle o switch para **ON**
4. Clique em "Trigger DAG" (ícone play)

### 2. Monitore a Execução

```bash
# Logs em tempo real
astro dev logs --follow

# Logs de uma DAG específica
astro dev logs --scheduler --follow
```

### 3. Verifique os Resultados

1. Acesse "DAGs" na interface
2. Clique em `brewery_etl_solid`
3. Visualize o "Graph View"
4. Clique em cada task para ver logs

## 🐛 Troubleshooting

### Container não inicia

```bash
# Pare tudo
astro dev stop

# Limpe volumes
astro dev kill

# Reinicie
astro dev start
```

### ODBC Driver não encontrado

```bash
# Rebuild com cache limpo
astro dev stop
astro dev start --build
```

### Conexão Azure SQL falha

1. Verifique `.env` - senha correta?
2. Verifique firewall Azure - IP permitido?
3. Teste manualmente:
   ```bash
   astro dev bash
   python -c "import pyodbc; print(pyodbc.drivers())"
   ```

### DAG não aparece

```bash
# Verifique erros de sintaxe
python dags/brewery_etl_dag.py

# Verifique erros de import
astro dev run dags list-import-errors
```

## 📚 Próximos Passos

- [Configurar Connections →](connections.md)
- [Entender as DAGs →](../dags/introduction.md)
- [Boas Práticas →](../guides/best-practices.md)
- [Troubleshooting Completo →](../guides/troubleshooting.md)

