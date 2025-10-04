#!/bin/bash
# ==============================================================================
# Script de Teste - Dependabot Major Updates
# ==============================================================================

set -e  # Exit on error

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "================================"
echo "🧪 TESTE DE DEPENDABOT PRs MAJOR"
echo "================================"
echo ""

# ==============================================================================
# Função: Testar Black 25.9.0
# ==============================================================================
test_black_25() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎨 Testando Black 25.9.0"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Salvar branch atual
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    
    # Criar branch de teste
    echo "📦 Criando branch de teste..."
    git checkout -b test-black-25 2>/dev/null || git checkout test-black-25
    
    # Fazer merge do PR
    echo "🔀 Fazendo merge do PR #8..."
    git fetch origin
    git merge origin/dependabot/pip/black-25.9.0 --no-edit || true
    
    # Atualizar dependências
    echo "📥 Instalando Black 25.9.0..."
    poetry install
    
    # Testar Black
    echo "🔍 Verificando diferenças de formatação..."
    poetry run black . --check --diff > black-diff.txt || true
    
    if [ -s black-diff.txt ]; then
        echo "⚠️  Black 25 reformataria o código:"
        head -n 50 black-diff.txt
        echo ""
        echo "📊 Ver diferenças completas: cat black-diff.txt"
        echo ""
        read -p "Aplicar formatação? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            poetry run black .
            echo "✅ Código reformatado!"
            echo "🔍 Review as mudanças com: git diff"
        else
            echo "❌ Formatação cancelada"
        fi
    else
        echo "✅ Nenhuma mudança de formatação necessária!"
    fi
    
    # Voltar para branch original
    git checkout "$CURRENT_BRANCH"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Teste Black 25 completo!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# ==============================================================================
# Função: Testar Astro Runtime 13.2.0
# ==============================================================================
test_astro_runtime_13() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🚀 Testando Astro Runtime 13.2.0"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Salvar branch atual
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    
    # Criar branch de teste
    echo "📦 Criando branch de teste..."
    git checkout -b test-astro-runtime-13 2>/dev/null || git checkout test-astro-runtime-13
    
    # Fazer merge do PR
    echo "🔀 Fazendo merge do PR #1..."
    git fetch origin
    git merge origin/dependabot/docker/astronomer/astro-runtime-13.2.0 --no-edit || true
    
    # Testar Docker build
    echo "🐳 Buildando imagem Docker..."
    docker build -t desafio-inbev:test-astro-13 . || {
        echo "❌ Docker build falhou!"
        echo "📋 Verifique os logs acima"
        git checkout "$CURRENT_BRANCH"
        return 1
    }
    
    echo "✅ Docker build bem-sucedido!"
    echo ""
    echo "🔍 Informações da imagem:"
    docker images desafio-inbev:test-astro-13
    echo ""
    echo "📊 Tamanho da imagem:"
    docker inspect desafio-inbev:test-astro-13 --format='{{.Size}}' | numfmt --to=iec
    
    # Limpar imagem de teste
    read -p "Limpar imagem de teste? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker rmi desafio-inbev:test-astro-13
        echo "✅ Imagem de teste removida"
    fi
    
    # Voltar para branch original
    git checkout "$CURRENT_BRANCH"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Teste Astro Runtime 13 completo!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# ==============================================================================
# Menu Principal
# ==============================================================================
echo "Escolha qual PR major testar:"
echo ""
echo "1) 🎨 Black 25.9.0 (PR #8)"
echo "2) 🚀 Astro Runtime 13.2.0 (PR #1)"
echo "3) 🔄 Ambos"
echo "4) ❌ Cancelar"
echo ""
read -p "Opção: " -n 1 -r
echo
echo ""

case $REPLY in
    1)
        test_black_25
        ;;
    2)
        test_astro_runtime_13
        ;;
    3)
        test_black_25
        test_astro_runtime_13
        ;;
    4)
        echo "❌ Teste cancelado"
        exit 0
        ;;
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac

echo ""
echo "================================"
echo "✅ TESTES COMPLETOS!"
echo "================================"
echo ""
echo "📋 Próximos passos:"
echo "  1. Review as mudanças"
echo "  2. Se OK, faça merge dos PRs no GitHub"
echo "  3. Delete as branches de teste locais"
echo ""
echo "🚀 Comandos úteis:"
echo "  - Limpar branches: git branch -D test-black-25 test-astro-runtime-13"
echo "  - Merge PR #8: gh pr merge 8 --squash --delete-branch"
echo "  - Merge PR #1: gh pr merge 1 --squash --delete-branch"
echo ""

