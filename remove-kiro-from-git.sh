#!/bin/bash

# Script para remover a pasta .kiro do repositório remoto
# mantendo-a apenas localmente

set -e

echo "🔍 Verificando se a pasta .kiro está sendo rastreada pelo Git..."

# Verificar se a pasta .kiro está no índice do Git
if git ls-files --error-unmatch .kiro/ >/dev/null 2>&1; then
    echo "📁 Pasta .kiro encontrada no controle de versão"
    echo "🗑️  Removendo .kiro do controle de versão..."
    
    # Remove a pasta do índice do Git mas mantém localmente
    git rm -r --cached .kiro/
    
    echo "✅ Pasta .kiro removida do controle de versão"
    echo "📝 A pasta ainda existe localmente mas não será mais rastreada"
    
    # Verificar se .gitignore já contém .kiro/
    if grep -q "^\.kiro/" .gitignore; then
        echo "✅ .kiro/ já está no .gitignore"
    else
        echo "📝 Adicionando .kiro/ ao .gitignore..."
        echo "" >> .gitignore
        echo "# Kiro IDE directory (local only)" >> .gitignore
        echo ".kiro/" >> .gitignore
        echo "✅ .kiro/ adicionado ao .gitignore"
    fi
    
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Fazer commit das mudanças:"
    echo "   git add .gitignore"
    echo "   git commit -m 'Remove .kiro directory from version control'"
    echo ""
    echo "2. Fazer push para o repositório remoto:"
    echo "   git push origin main"
    echo ""
    echo "⚠️  A pasta .kiro será removida do repositório remoto mas permanecerá local"
    
else
    echo "✅ A pasta .kiro não está sendo rastreada pelo Git"
    echo "ℹ️  Nenhuma ação necessária - a pasta já é apenas local"
    
    # Verificar se está no .gitignore
    if grep -q "^\.kiro/" .gitignore; then
        echo "✅ .kiro/ já está no .gitignore"
    else
        echo "📝 Garantindo que .kiro/ está no .gitignore..."
        echo "" >> .gitignore
        echo "# Kiro IDE directory (local only)" >> .gitignore
        echo ".kiro/" >> .gitignore
        echo "✅ .kiro/ adicionado ao .gitignore"
        
        echo ""
        echo "📋 Fazer commit da atualização do .gitignore:"
        echo "   git add .gitignore"
        echo "   git commit -m 'Ensure .kiro directory is ignored'"
        echo "   git push origin main"
    fi
fi

echo ""
echo "🎉 Processo concluído!"
echo "📁 A pasta .kiro agora é mantida apenas localmente"