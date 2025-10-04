# Boas Práticas

## 🎯 Princípios Gerais

### 1. Segurança em Primeiro Lugar

!!! danger "NUNCA faça isso"
    ```python
    # ❌ Senha hardcoded
    password = "minha_senha_123"
    
    # ❌ Token no código
    databricks_token = "dapi1234567890"
    
    # ❌ IDs reais em documentação
    cluster_id = "0626-205409-935ntddc"
    ```

!!! success "SEMPRE faça isso"
    ```python
    # ✅ Usar configurações
    from config import AzureSQLConfig
    config = AzureSQLConfig()  # Lê de environment
    
    # ✅ Usar Airflow Variables
    cluster_id = Variable.get("databricks_cluster_id")
    
    # ✅ Placeholders em docs
    cluster_id = "XXXX-XXXXXX-XXXXXXXX"
    ```

### 2. Sempre Use Dependency Injection

!!! example "Dependency Injection"
    ```python
    # ✅ BOM - Injetar dependências
    class BreweryAPIExtractor:
        def __init__(self, config: APIConfig):
            self.config = config
    
    # Fácil de testar
    mock_config = APIConfig(brewery_api_url="http://test")
    extractor = BreweryAPIExtractor(mock_config)
    ```

### 3. Single Responsibility

!!! tip "Uma classe, uma responsabilidade"
    ```python
    # ✅ BOM - Classes focadas
    class BreweryAPIExtractor:
        """Apenas extrai dados"""
        def extract(self): ...
    
    class BreweryTransformer:
        """Apenas transforma dados"""
        def transform(self, data): ...
    
    class AzureSQLLoader:
        """Apenas carrega dados"""
        def load(self, data): ...
    
    # ❌ RUIM - Classe faz tudo
    class BreweryProcessor:
        def process(self):
            # Extrai, transforma e carrega tudo aqui
            ...
    ```

## 📝 DAGs

### Estrutura Padrão

```python
"""
DAG Description

Detailed explanation of what this DAG does.
"""

# 1. Imports organizados
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Configurações
from config import AirflowConfig, APIConfig
from factories import ETLFactory
from utils.logger import get_logger

# 2. Configuração global
config = AirflowConfig()
logger = get_logger(__name__)

# 3. Funções de task
def my_task(**context):
    """Task docstring."""
    log_task_start(logger, "my_task")
    try:
        # Lógica
        result = do_something()
        log_task_success(logger, "my_task", records=result)
    except Exception as e:
        log_task_error(logger, "my_task", e)
        raise

# 4. Default args
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 1),
    'retries': config.default_retries,
    'retry_delay': timedelta(seconds=config.retry_delay_seconds),
}

# 5. DAG definition
with DAG(
    'my_dag_name',
    default_args=default_args,
    description='Clear description',
    schedule_interval='@daily',
    catchup=False,
    tags=['category', 'solid', 'production'],
) as dag:
    
    task1 = PythonOperator(
        task_id='task1',
        python_callable=my_task,
        doc_md="""
        ### Task Documentation
        
        What this task does.
        """,
    )
```

### Naming Conventions

| Tipo | Convenção | Exemplo |
|------|-----------|---------|
| **DAG** | `{domain}_{action}_{tech}` | `brewery_etl_solid` |
| **Task** | `{verb}_{noun}_task` | `extract_data_task` |
| **Variable** | `snake_case` | `databricks_cluster_id` |
| **Class** | `PascalCase` | `BreweryAPIExtractor` |
| **Function** | `snake_case` | `extract_brewery_data` |

### Tags

Use tags para organizar DAGs:

```python
tags = [
    'etl',           # Tipo de processo
    'brewery',       # Domínio
    'azure-sql',     # Tecnologia
    'solid',         # Arquitetura
    'production',    # Ambiente
]
```

## 🔧 Código Python

### Type Hints

!!! success "SEMPRE use type hints"
    ```python
    def extract_data(config: APIConfig) -> List[Dict[str, Any]]:
        """Extract data from API."""
        ...
    
    class BreweryExtractor:
        def __init__(self, config: APIConfig) -> None:
            self.config: APIConfig = config
    ```

### Docstrings

Use Google Style:

```python
def load_data(data: List[Dict], config: AzureSQLConfig) -> int:
    """
    Load brewery data to Azure SQL.
    
    Args:
        data: List of brewery dictionaries
        config: Azure SQL configuration
        
    Returns:
        Number of records loaded
        
    Raises:
        LoadError: If loading fails
        
    Example:
        >>> loader = AzureSQLLoader(config)
        >>> count = loader.load(data)
        >>> print(f"Loaded {count} records")
    """
    ...
```

### Error Handling

```python
# ✅ BOM - Exceções específicas
try:
    data = extractor.extract()
except ExtractionError as e:
    logger.error(f"Failed to extract: {e}")
    raise
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    raise
finally:
    cleanup_resources()

# ❌ RUIM - Catch genérico
try:
    data = extractor.extract()
except Exception as e:  # Muito genérico!
    print("Error!")  # Não use print!
```

### Logging

!!! tip "Use o sistema de logging"
    ```python
    from utils.logger import get_logger, log_task_start
    
    logger = get_logger(__name__)
    
    # Início da task
    log_task_start(logger, "extract", source="API")
    
    # Sucesso com métricas
    log_task_success(
        logger,
        "extract",
        records=100,
        duration="2.3s"
    )
    
    # Erro com contexto
    log_task_error(
        logger,
        "extract",
        error,
        retry_count=1
    )
    ```

## 🧪 Testes

### Estrutura de Testes

```
tests/
├── unit/
│   ├── test_extractors.py
│   ├── test_loaders.py
│   └── test_transformers.py
├── integration/
│   └── test_etl_pipeline.py
└── conftest.py
```

### Unit Tests

```python
import pytest
from config import APIConfig
from services import BreweryAPIExtractor

def test_brewery_extractor():
    # Arrange
    config = APIConfig(brewery_api_url="http://test")
    extractor = BreweryAPIExtractor(config)
    
    # Act
    data = extractor.extract()
    
    # Assert
    assert len(data) > 0
    assert extractor.validate_data(data)
```

### Mock Configs

```python
from unittest.mock import Mock

def test_with_mock():
    # Mock extractor
    mock_extractor = Mock(spec=IDataExtractor)
    mock_extractor.extract.return_value = [
        {'id': '1', 'name': 'Test'}
    ]
    
    # Test
    pipeline = ETLPipeline(extractor=mock_extractor)
    result = pipeline.run()
    
    # Assert
    mock_extractor.extract.assert_called_once()
```

## 📊 Monitoramento

### Métricas Importantes

```python
# Registre sempre
log_task_success(
    logger,
    "extract",
    records=len(data),        # Quantidade
    duration="2.3s",          # Tempo
    api_status=200,           # Status
    source="brewery_api"      # Origem
)
```

### Alertas

Configure alertas para:
- ❌ DAG failures
- ⏱️ Tasks lentas (>threshold)
- 📉 Queda na quantidade de dados
- 🔄 Muitos retries

### SLAs

```python
with DAG(
    'critical_dag',
    sla_miss_callback=notify_team,
    default_args={
        'sla': timedelta(hours=2),  # SLA de 2 horas
    }
) as dag:
    ...
```

## 🔐 Segurança

### Checklist de Segurança

- [ ] Nenhuma senha no código
- [ ] `.env` no `.gitignore`
- [ ] Connections via Airflow
- [ ] Variables para configs sensíveis
- [ ] Placeholders em docs
- [ ] Logs não expõem secrets
- [ ] Service Principals (não users)

### Azure Key Vault (Produção)

```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = SecretClient(
    vault_url="https://my-vault.vault.azure.net",
    credential=credential
)

secret = client.get_secret("databricks-token")
token = secret.value
```

## 📚 Documentação

### README de DAG

Cada DAG deve ter:
- Descrição clara
- Dependências
- Configurações necessárias
- Exemplo de execução
- Troubleshooting comum

### Comentários

```python
# ✅ BOM - Explica o "porquê"
# MERGE instead of INSERT to handle duplicates
cursor.execute(merge_sql, ...)

# ❌ RUIM - Explica o "o quê" (óbvio)
# Execute SQL
cursor.execute(sql)
```

## 🚀 Performance

### Otimizações

```python
# ✅ BOM - Batch loading
def load_batch(data: List[Dict]):
    with connection() as conn:
        cursor.executemany(sql, data)  # Batch!

# ❌ RUIM - Loading individual
for record in data:
    cursor.execute(sql, record)  # Lento!
```

### Connection Pooling

```python
# ✅ BOM - Context manager
def get_data():
    with get_connection() as conn:
        cursor = conn.cursor()
        return cursor.fetchall()
    # Connection fechada automaticamente

# ❌ RUIM - Connections abertas
conn = get_connection()
cursor = conn.cursor()
# Nunca fecha!
```

## 📖 Saiba Mais

- [Arquitetura SOLID →](../architecture/overview.md)
- [Troubleshooting →](troubleshooting.md)
- [Deployment →](deployment.md)

