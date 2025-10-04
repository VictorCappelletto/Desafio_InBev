# Setup GitHub Pages - MkDocs

Instruções para configurar o GitHub Pages pela primeira vez.

---

## Configuração Inicial (Uma vez apenas)

### 1. Ativar GitHub Pages no Repositório

1. Vá para **Settings** do seu repositório no GitHub
2. No menu lateral, clique em **Pages**
3. Em **Source**, selecione:
 - **Source**: `GitHub Actions` (não Branch!)
4. Clique em **Save**

### 2. Executar Workflow Manualmente (Primeira vez)

1. Vá para a aba **Actions** no GitHub
2. Clique em **Deploy Documentation** no menu lateral
3. Clique em **Run workflow** → **Run workflow**
4. Aguarde o workflow concluir (~2 minutos)

### 3. Verificar Deployment

Após o workflow concluir:
- Acesse: https://victorcappelleto.github.io/Desafio_InBev/
- A documentação deve estar disponível!

---

## Atualizações Automáticas

Após a configuração inicial, a documentação será automaticamente atualizada quando:

1. **Push para main** com mudanças em:
 - `docs/**` (qualquer arquivo de documentação)
 - `mkdocs.yml` (configuração)
 - `.github/workflows/mkdocs-deploy.yml` (workflow)

2. **Workflow manual** (qualquer momento):
 - Actions → Deploy Documentation → Run workflow

---

## Desenvolvimento Local

### Instalar Dependências

```bash
# Com poetry (recomendado)
poetry install

# Ou com pip
pip install mkdocs mkdocs-material mkdocstrings[python] mkdocs-mermaid2-plugin
```

### Comandos Disponíveis

```bash
# Preview local (hot reload)
poetry run task doc
# Acesse: http://localhost:8000

# Build (gera site/ folder)
poetry run task doc-build

# Deploy manual para GitHub Pages
poetry run task doc-deploy

# Limpar build artifacts
poetry run task clean
```

### Preview Local (Sem Poetry)

```bash
# Instalar MkDocs
pip install mkdocs-material

# Servir localmente
mkdocs serve

# Build
mkdocs build

# Deploy
mkdocs gh-deploy
```

---

## Troubleshooting

### Erro: "GitHub Pages is not enabled"

**Solução:** Ative GitHub Pages nas configurações (passo 1 acima)

---

### Erro: "Permission denied"

**Solução:** Verifique que o workflow tem permissões corretas:
1. Settings → Actions → General
2. Workflow permissions: **Read and write permissions**
3. Salve as mudanças

---

### Erro: "404 - Page not found"

**Possíveis causas:**
1. Workflow ainda não rodou → Execute manualmente (passo 2)
2. URL incorreta → Verifique em Settings → Pages
3. Build falhou → Verifique logs em Actions

---

### Erro: "MkDocs plugin not found"

**Solução local:**
```bash
# Reinstalar dependências
pip install --upgrade mkdocs-material mkdocstrings[python] mkdocs-mermaid2-plugin

# Ou com poetry
poetry install
```

---

## Estrutura de Arquivos

```
docs/
 index.md # Homepage
 architecture/
 overview.md
 components.md
 data-flow.md
 domain-layer.md
 use-cases.md
 repositories.md
 guides/
 best-practices.md
 data-quality.md
 observability.md
 troubleshooting.md
 deployment.md
 dags/
 introduction.md
 extract-api-sql.md
 databricks-notebook.md
 azure-data-factory.md
 setup/
 initial-setup.md
 connections.md
 variables.md
 local-development.md

mkdocs.yml # MkDocs configuration
.github/workflows/mkdocs-deploy.yml # GitHub Actions workflow
```

---

## Checklist de Verificação

Antes de fazer push:

- [ ] Todas as páginas listadas em `mkdocs.yml` existem
- [ ] Links internos funcionam (use `mkdocs build --strict`)
- [ ] Imagens e diagramas carregam corretamente
- [ ] Preview local funciona (`task doc`)
- [ ] Sem erros de build no terminal

---

## Links Úteis

- **Documentação MkDocs**: https://www.mkdocs.org/
- **Material Theme**: https://squidfunk.github.io/mkdocs-material/
- **GitHub Pages Docs**: https://docs.github.com/en/pages
- **MkDocstrings**: https://mkdocstrings.github.io/

---

## Dicas

!!! tip "Hot Reload"
 Use `task doc` para desenvolvimento - mudanças aparecem instantaneamente no browser!

!!! warning "Build Strict"
 Sempre use `mkdocs build --strict` antes de fazer push para detectar links quebrados.

!!! success "Custom Domain"
 Para usar domínio customizado, adicione arquivo `CNAME` na pasta `docs/`:
 ```
 docs.seu-dominio.com
 ```

