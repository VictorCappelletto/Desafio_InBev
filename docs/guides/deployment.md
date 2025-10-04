# Deploy em Produção

Guia completo para deploy do projeto em ambientes produtivos.

---

## Ambientes Suportados

O projeto pode ser deployado em:

### 1. **Astronomer Cloud** (Recomendado)
- **Vantagens:** Gerenciamento simplificado, auto-scaling, monitoramento integrado
- **Custo:** Plano pago ($0.25/AU/hora)
- **Docs:** [Astronomer Deploy Guide](https://docs.astronomer.io/astro/deploy-code)

### 2. **Azure Container Instances**
- **Vantagens:** Integração nativa com Azure, baixo custo
- **Setup:** Requer configuração de networking e secrets

### 3. **Kubernetes (GKE/EKS/AKS)**
- **Vantagens:** Total controle, customização ilimitada
- **Complexidade:** Requer expertise em K8s

---

## Deploy via Astronomer Cloud

### Passo 1: Criar Conta
```bash
# Criar conta gratuita (trial)
https://www.astronomer.io/try-astro/

# Instalar Astro CLI (se ainda não tiver)
brew install astro
```

### Passo 2: Login e Deploy
```bash
# Login
astro login

# Deploy para workspace
astro deploy

# Escolher workspace e cluster
# Aguardar build (~5 min)
```

### Passo 3: Configurar Secrets
```bash
# Via Astro UI:
# 1. Settings → Environment Variables
# 2. Adicionar secrets:
AZURE_SQL_PASSWORD=***
DATABRICKS_TOKEN=***
DATABRICKS_HOST=https://...
ADF_TENANT_ID=***
ADF_CLIENT_ID=***
ADF_CLIENT_SECRET=***
```

### Passo 4: Verificar Deploy
```bash
# Ver logs
astro deployment logs

# Ver status
astro deployment list

# URL da UI: https://your-deployment.astro.datakin.com
```

---

## Deploy via Docker Compose

### Passo 1: Build da Imagem
```bash
# Build otimizado
docker build -t desafio-inbev:latest .

# Push para registry (opcional)
docker tag desafio-inbev:latest your-registry/desafio-inbev:latest
docker push your-registry/desafio-inbev:latest
```

### Passo 2: Criar `docker-compose.prod.yml`
```yaml
version: '3'
services:
 webserver:
 image: desafio-inbev:latest
 environment:
 AIRFLOW__CORE__EXECUTOR: CeleryExecutor
 AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://...
 AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
 AZURE_SQL_PASSWORD: ${AZURE_SQL_PASSWORD}
 DATABRICKS_TOKEN: ${DATABRICKS_TOKEN}
 ports:
 - "8080:8080"

 scheduler:
 image: desafio-inbev:latest
 command: scheduler
 depends_on:
 - postgres
 - redis

 worker:
 image: desafio-inbev:latest
 command: celery worker
 depends_on:
 - postgres
 - redis

 postgres:
 image: postgres:13
 environment:
 POSTGRES_USER: airflow
 POSTGRES_PASSWORD: airflow
 POSTGRES_DB: airflow

 redis:
 image: redis:7
```

### Passo 3: Deploy
```bash
# Start
docker-compose -f docker-compose.prod.yml up -d

# Ver logs
docker-compose logs -f

# Stop
docker-compose -f docker-compose.prod.yml down
```

---

## Deploy via Kubernetes

### Passo 1: Helm Chart (Airflow)
```bash
# Adicionar repo
helm repo add apache-airflow https://airflow.apache.org
helm repo update

# Instalar
helm install airflow apache-airflow/airflow \
 --namespace airflow \
 --create-namespace \
 --set images.airflow.repository=your-registry/desafio-inbev \
 --set images.airflow.tag=latest
```

### Passo 2: Configurar Secrets
```bash
# Criar secret
kubectl create secret generic airflow-secrets \
 --from-literal=AZURE_SQL_PASSWORD='***' \
 --from-literal=DATABRICKS_TOKEN='***' \
 --namespace airflow
```

### Passo 3: Deploy via Kubectl
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
 name: airflow-webserver
 namespace: airflow
spec:
 replicas: 2
 selector:
 matchLabels:
 app: airflow-webserver
 template:
 metadata:
 labels:
 app: airflow-webserver
 spec:
 containers:
 - name: webserver
 image: your-registry/desafio-inbev:latest
 ports:
 - containerPort: 8080
 envFrom:
 - secretRef:
 name: airflow-secrets
```

---

## Gerenciamento de Secrets

### Opção 1: Azure Key Vault (Recomendado)
```python
# dags/config/azure_secrets.py
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://your-vault.vault.azure.net/", credential=credential)

# Usar em DAGs:
AZURE_SQL_PASSWORD = client.get_secret("azure-sql-password").value
```

### Opção 2: Airflow Variables (Encrypted)
```bash
# Via CLI:
airflow variables set AZURE_SQL_PASSWORD "***" --json

# Via UI:
# Admin → Variables → + → Key/Value
```

### Opção 3: Environment Variables
```bash
# .env (não commitar!)
export AZURE_SQL_PASSWORD='***'
export DATABRICKS_TOKEN='***'
```

---

## Monitoramento

### 1. **Airflow UI**
- DAG runs history
- ⏱ Task duration
- Failure logs

### 2. **Azure Monitor** (se usando Azure)
```bash
# Habilitar logs
az monitor diagnostic-settings create \
 --resource /subscriptions/.../airflow \
 --logs '[{"category": "AirflowLogs", "enabled": true}]'
```

### 3. **Prometheus + Grafana**
```yaml
# metrics.yaml
apiVersion: v1
kind: ConfigMap
metadata:
 name: airflow-metrics
data:
 statsd_exporter.yml: |
 mappings:
 - match: "airflow.dag.*.*.duration"
 name: "airflow_dag_duration"
```

---

## CI/CD Automation

### GitHub Actions Deploy (exemplo)
```yaml
# .github/workflows/cd.yml
name: Deploy to Production

on:
 push:
 branches: [main]

jobs:
 deploy:
 runs-on: ubuntu-latest
 steps:
 - uses: actions/checkout@v4

 - name: Deploy to Astronomer
 run: |
 astro login --token ${{ secrets.ASTRO_TOKEN }}
 astro deploy <deployment-id>
```

---

## Checklist de Deploy

Antes de fazer deploy para produção:

- [ ] Todos os testes passando (`poetry run task test`)
- [ ] Lint sem erros (`poetry run task lint`)
- [ ] Security scan limpo (CI)
- [ ] Secrets configurados (não hardcoded)
- [ ] Connections testadas (Azure SQL, Databricks, ADF)
- [ ] Variáveis de ambiente configuradas
- [ ] Logs configurados (nível INFO ou WARNING)
- [ ] Alertas configurados (email/Slack)
- [ ] Backup do metastore configurado
- [ ] Monitoramento configurado
- [ ] Documentação atualizada

---

## Rollback

Se algo der errado:

### Astronomer
```bash
# Listar deploys
astro deployment list

# Rollback para versão anterior
astro deployment rollback <deployment-id>
```

### Docker
```bash
# Stop current
docker-compose down

# Deploy versão anterior
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes
```bash
# Rollback deployment
kubectl rollout undo deployment/airflow-webserver -n airflow

# Ver histórico
kubectl rollout history deployment/airflow-webserver -n airflow
```

---

## Suporte

Para dúvidas sobre deploy:

- [Astronomer Docs](https://docs.astronomer.io/)
- [Airflow Docs - Production](https://airflow.apache.org/docs/apache-airflow/stable/production-deployment.html)
- [Azure AKS Docs](https://learn.microsoft.com/en-us/azure/aks/)

---

## Próximos Passos

Após deploy em produção:

1. **Habilitar auto-scaling** (Astronomer/K8s)
2. **Configurar alertas** (PagerDuty, Slack)
3. **Implementar observability completa** (framework já criado)
4. **Configurar backup automático** do metastore
5. **Documentar runbooks** para incidentes comuns
