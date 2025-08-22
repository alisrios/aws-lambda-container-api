# Guia para Remover .kiro do Repositório Remoto

## 🎯 Objetivo

Remover a pasta `.kiro` do repositório remoto (GitHub) mantendo-a apenas localmente para uso do Kiro IDE.

## 🚀 Execução Rápida

### Opção 1: Script Automatizado (Recomendado)

**No Windows (PowerShell):**
```powershell
.\remove-kiro-from-git.ps1
```

**No Linux/macOS/WSL:**
```bash
chmod +x remove-kiro-from-git.sh
./remove-kiro-from-git.sh
```

### Opção 2: Comandos Manuais

```bash
# 1. Remover .kiro do controle de versão (mantém local)
git rm -r --cached .kiro/

# 2. Verificar se foi removido
git status

# 3. Fazer commit da remoção
git add .gitignore
git commit -m "Remove .kiro directory from version control - keep local only"

# 4. Push para remover do repositório remoto
git push origin main
```

## 📋 O que acontece

### ✅ **Antes da execução:**
- `.kiro/` existe localmente ✅
- `.kiro/` está no repositório remoto ❌
- `.kiro/` está sendo rastreado pelo Git ❌

### ✅ **Depois da execução:**
- `.kiro/` existe localmente ✅
- `.kiro/` **NÃO** está no repositório remoto ✅
- `.kiro/` **NÃO** é rastreado pelo Git ✅
- `.kiro/` está no `.gitignore` ✅

## 🔍 Verificações

### Verificar se .kiro está sendo rastreado:
```bash
git ls-files | grep .kiro
# Se não retornar nada = não está sendo rastreado ✅
```

### Verificar se está no .gitignore:
```bash
grep -n ".kiro" .gitignore
# Deve mostrar a linha com .kiro/ ✅
```

### Verificar status do Git:
```bash
git status
# .kiro não deve aparecer em "Changes not staged" ✅
```

## 🛡️ Segurança

- ✅ **Pasta local preservada**: `.kiro/` continua funcionando localmente
- ✅ **Configurações mantidas**: Todas as configurações do Kiro IDE preservadas
- ✅ **Sem perda de dados**: Nenhum arquivo local é perdido
- ✅ **Reversível**: Pode ser desfeito se necessário

## 🔄 Para Reverter (se necessário)

```bash
# Remover do .gitignore
sed -i '/\.kiro\//d' .gitignore

# Adicionar de volta ao controle de versão
git add .kiro/
git commit -m "Add .kiro back to version control"
git push origin main
```

## 📁 Estrutura Final

```
projeto/
├── .kiro/                    # ✅ Local apenas
│   ├── settings/
│   └── steering/
├── .gitignore               # ✅ Contém .kiro/
├── src/
├── terraform/
└── ...
```

## ✅ Resultado Esperado

Após a execução:
1. ✅ **Repositório remoto limpo** - sem pasta .kiro
2. ✅ **Kiro IDE funciona** - pasta local preservada
3. ✅ **Git ignora .kiro** - não rastreia mudanças futuras
4. ✅ **Colaboradores não veem** - .kiro não aparece para outros

## 🎉 Benefícios

- **Repositório mais limpo** - sem arquivos específicos do IDE
- **Configurações pessoais** - cada desenvolvedor tem suas próprias
- **Menos conflitos** - não há merge conflicts em configurações
- **Melhor colaboração** - foco no código, não nas ferramentas

Execute o script e a pasta `.kiro` será mantida apenas localmente! 🚀