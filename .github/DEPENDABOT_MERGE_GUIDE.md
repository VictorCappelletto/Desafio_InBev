# 🤖 Guia de Merge - Dependabot PRs

## ✅ PRs SEGUROS PARA MERGE IMEDIATO

### PR #7 - `mkdocs-mermaid2-plugin` (1.1.1 → 1.2.2)
**Status:** ✅ SAFE - Minor update  
**Link:** https://github.com/VictorCappelletto/Desafio_InBev/pull/7

**O que mudou:**
- Fix deprecation warning do BeautifulSoup (#119)
- Adiciona framework de testes (pytest)
- Migração para pyproject.toml

**Merge:**
```bash
gh pr merge 7 --squash --delete-branch
```

---

### PR #9 - `pyodbc` (5.1.0 → 5.2.0)
**Status:** ✅ SAFE - Minor update  
**Link:** https://github.com/VictorCappelletto/Desafio_InBev/pull/9

**O que mudou:**
- Suporte para Python 3.13 (future-proof!)
- Adiciona constante `SQL_SS_VARIANT`
- Melhorias em type hints

**Merge:**
```bash
gh pr merge 9 --squash --delete-branch
```

---

### PR #4 - `action-semantic-pull-request` (v5 → v6)
**Status:** ✅ SAFE - CI/CD only (não afeta código)  
**Link:** https://github.com/VictorCappelletto/Desafio_InBev/pull/4

**O que mudou:**
- Upgrade para Node.js 24
- Suporte a regex para `types` e `scopes`
- Correções de segurança

**Merge:**
```bash
gh pr merge 4 --squash --delete-branch
```

---

## ⚠️ PRs QUE REQUEREM REVISÃO MANUAL

### PR #1 - `astronomer/astro-runtime` (11.5.0 → 13.2.0)
**Status:** ⚠️ MAJOR UPDATE - Testar antes!  
**Link:** https://github.com/VictorCappelletto/Desafio_InBev/pull/1

**Riscos:**
- Atualização major (11 → 13)
- Pode ter breaking changes no Airflow
- Requer teste local primeiro

**Teste local:**
```bash
# 1. Criar branch de teste
git checkout -b test-astro-runtime-13

# 2. Fazer merge local
git merge origin/dependabot/docker/astronomer/astro-runtime-13.2.0

# 3. Testar Docker build
docker build -t desafio-inbev:test .

# 4. Se OK, fazer merge no GitHub
gh pr merge 1 --squash --delete-branch
```

---

### PR #8 - `black` (24.4.2 → 25.9.0)
**Status:** ⚠️ MAJOR UPDATE - Reformatação de código  
**Link:** https://github.com/VictorCappelletto/Desafio_InBev/pull/8

**Riscos:**
- Atualização major (24 → 25)
- Pode reformatar código existente
- Remove suporte Python < 3.7

**Teste local:**
```bash
# 1. Criar branch de teste
git checkout -b test-black-25

# 2. Fazer merge local
git merge origin/dependabot/pip/black-25.9.0

# 3. Rodar black e ver diff
poetry run black . --check --diff

# 4. Se diferenças são aceitáveis
poetry run black .
git add -A
git commit -m "chore: apply black 25.9.0 formatting"

# 5. Push e merge
git push
gh pr merge 8 --squash --delete-branch
```

---

## 🏷️ CRIAR LABELS (VIA WEB)

Acesse: https://github.com/VictorCappelletto/Desafio_InBev/labels

| Nome            | Cor       | Descrição                           |
|-----------------|-----------|-------------------------------------|
| `dependencies`  | `#0366d6` | Pull requests that update a dependency file |
| `python`        | `#3572A5` | Python dependencies                 |
| `docker`        | `#2496ED` | Docker dependencies                 |
| `ci-cd`         | `#28A745` | CI/CD related changes               |
| `github-actions`| `#2088FF` | GitHub Actions workflows            |

---

## 📊 ORDEM RECOMENDADA

1. ✅ Criar labels (2 min)
2. ✅ Merge PR #7 (mermaid)
3. ✅ Merge PR #9 (pyodbc)
4. ✅ Merge PR #4 (semantic-pr)
5. 🧪 Testar PR #8 localmente (black)
6. 🧪 Testar PR #1 localmente (astro-runtime)
7. ✅ Merge PRs testados (se OK)

---

## 🤖 AUTO-MERGE FUTURO

Para evitar PRs manuais no futuro, configure GitHub auto-merge:

### Via GitHub Web:
1. Acesse: Settings → General → Pull Requests
2. Habilite: "Allow auto-merge"
3. Configure: Branch protection rules (require status checks)

### Via Dependabot:
Já configurado em `.github/dependabot-auto-merge.yml`!

---

**Gerado automaticamente pelo Assistant** ✨

