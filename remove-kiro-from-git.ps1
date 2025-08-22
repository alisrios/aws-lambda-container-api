# Script PowerShell para remover a pasta .kiro do repositório remoto
# mantendo-a apenas localmente

Write-Host "🔍 Verificando se a pasta .kiro está sendo rastreada pelo Git..." -ForegroundColor Blue

# Verificar se a pasta .kiro está no índice do Git
$kiroTracked = $false
try {
    git ls-files --error-unmatch .kiro/ 2>$null | Out-Null
    $kiroTracked = $true
} catch {
    $kiroTracked = $false
}

if ($kiroTracked) {
    Write-Host "📁 Pasta .kiro encontrada no controle de versão" -ForegroundColor Yellow
    Write-Host "🗑️  Removendo .kiro do controle de versão..." -ForegroundColor Yellow
    
    # Remove a pasta do índice do Git mas mantém localmente
    git rm -r --cached .kiro/
    
    Write-Host "✅ Pasta .kiro removida do controle de versão" -ForegroundColor Green
    Write-Host "📝 A pasta ainda existe localmente mas não será mais rastreada" -ForegroundColor Cyan
    
    # Verificar se .gitignore já contém .kiro/
    $gitignoreContent = Get-Content .gitignore -ErrorAction SilentlyContinue
    if ($gitignoreContent -contains ".kiro/" -or $gitignoreContent -contains "# Kiro IDE directory (local only)") {
        Write-Host "✅ .kiro/ já está no .gitignore" -ForegroundColor Green
    } else {
        Write-Host "📝 Adicionando .kiro/ ao .gitignore..." -ForegroundColor Cyan
        Add-Content .gitignore "`n# Kiro IDE directory (local only)"
        Add-Content .gitignore ".kiro/"
        Write-Host "✅ .kiro/ adicionado ao .gitignore" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
    Write-Host "1. Fazer commit das mudanças:" -ForegroundColor White
    Write-Host "   git add .gitignore" -ForegroundColor Gray
    Write-Host "   git commit -m 'Remove .kiro directory from version control'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Fazer push para o repositório remoto:" -ForegroundColor White
    Write-Host "   git push origin main" -ForegroundColor Gray
    Write-Host ""
    Write-Host "⚠️  A pasta .kiro será removida do repositório remoto mas permanecerá local" -ForegroundColor Yellow
    
} else {
    Write-Host "✅ A pasta .kiro não está sendo rastreada pelo Git" -ForegroundColor Green
    Write-Host "ℹ️  Nenhuma ação necessária - a pasta já é apenas local" -ForegroundColor Cyan
    
    # Verificar se está no .gitignore
    $gitignoreContent = Get-Content .gitignore -ErrorAction SilentlyContinue
    if ($gitignoreContent -contains ".kiro/" -or $gitignoreContent -contains "# Kiro IDE directory (local only)") {
        Write-Host "✅ .kiro/ já está no .gitignore" -ForegroundColor Green
    } else {
        Write-Host "📝 Garantindo que .kiro/ está no .gitignore..." -ForegroundColor Cyan
        Add-Content .gitignore "`n# Kiro IDE directory (local only)"
        Add-Content .gitignore ".kiro/"
        Write-Host "✅ .kiro/ adicionado ao .gitignore" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "📋 Fazer commit da atualização do .gitignore:" -ForegroundColor Cyan
        Write-Host "   git add .gitignore" -ForegroundColor Gray
        Write-Host "   git commit -m 'Ensure .kiro directory is ignored'" -ForegroundColor Gray
        Write-Host "   git push origin main" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "🎉 Processo concluído!" -ForegroundColor Green
Write-Host "📁 A pasta .kiro agora é mantida apenas localmente" -ForegroundColor Cyan