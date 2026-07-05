# Dependências do Projeto — Tech Challenge FIAP

## 📋 Informações do Ambiente

- **Python**: 3.14.6 (Virtual Environment)
- **Localização do venv**: `.venv/`
- **Data**: 2026-07-05

---

## 📦 Bibliotecas Necessárias

### Núcleo Científico & Dados

| Biblioteca | Versão Mínima | Propósito | Compatibilidade Python 3.14 |
|-----------|---------------|---------|------|
| **numpy** | >= 1.26.0 | Computação numérica e arrays multidimensionais | ✅ Sim |
| **pandas** | >= 2.1.0 | Manipulação de DataFrames e análise de dados | ✅ Sim |
| **matplotlib** | >= 3.8.0 | Visualização de gráficos e plots | ✅ Sim |

### Machine Learning & Otimização

| Biblioteca | Versão Mínima | Propósito | Compatibilidade Python 3.14 |
|-----------|---------------|---------|------|
| **scikit-learn** | >= 1.3.0 | Modelos ML (Random Forest, métricas) | ✅ Sim |
| **imbalanced-learn** | >= 0.11.0 | SMOTE para balanceamento de dados | ✅ Sim |

### Ambiente Jupyter

| Biblioteca | Versão Mínima | Propósito | Compatibilidade Python 3.14 |
|-----------|---------------|---------|------|
| **jupyter** | >= 1.0.0 | Ambiente Jupyter Notebook | ✅ Sim |
| **ipykernel** | >= 6.25.0 | Kernel Python para Jupyter | ✅ Sim |
| **ipywidgets** | >= 8.0.0 | Widgets interativos no notebook | ✅ Sim |

### Desenvolvimento & Qualidade

| Biblioteca | Versão Mínima | Propósito | Compatibilidade Python 3.14 |
|-----------|---------------|---------|------|
| **pytest** | >= 7.4.0 | Framework de testes (opcional) | ✅ Sim |
| **black** | >= 23.7.0 | Formatação de código (opcional) | ✅ Sim |

---

## 🔧 Instalação

### 1) Verificar o ambiente virtual (já existe)

```bash
# No PowerShell, navegar até o projeto
cd c:\Users\mikae\OneDrive\Documentos\FIAP\tech_challenge_fiap_2

# Ativar o venv (se necessário)
.\.venv\Scripts\Activate.ps1
```

### 2) Instalar dependências

```bash
pip install -r requirements.txt
```

### 3) Verificar instalação

```bash
pip list
```

---

## ✅ Bibliotecas Built-in Utilizadas

O notebook também usa as seguintes bibliotecas **nativas do Python** (não requerem instalação):

- `warnings` — supressão de avisos
- `time` — medição de tempo de execução
- `copy` — cópia profunda de objetos

---

## 🔍 Detalhes de Compatibilidade

### Por que essas versões?

- **Python 3.14** é a versão mais recente (lançada em 2024)
- Todas as bibliotecas selecionadas têm suporte completo para Python 3.14
- As versões mínimas especificadas garantem compatibilidade com features do Python 3.14

### Versões Pinadas vs Ranges

O `requirements.txt` usa **ranges mínimos** (`>=`) em vez de versões exatas para:
- Permitir updates de patch (bugfixes)
- Evitar travamento em versões antigas
- Facilitar resolução de dependências transitivas

Se precisar de **reprodutibilidade exata**, use:

```bash
pip freeze > requirements-lock.txt
```

Isso cria um arquivo com versões exatas de **tudo** instalado no ambiente.

---

## 📝 Uso do requirements.txt

### Para novos desenvolvedores

```bash
# Clonar/baixar o projeto
cd tech_challenge_fiap_2

# Criar e ativar venv (opcional, já existe)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependências do projeto
pip install -r requirements.txt

# Abrir Jupyter e rodar o notebook
jupyter notebook
```

### Para atualizar dependências

```bash
# Atualizar pacotes para a versão mais recente compatível
pip install --upgrade -r requirements.txt

# Verificar conflitos (se houver)
pip check
```

---

## 🐛 Resolução de Problemas

### Erro: "ModuleNotFoundError: No module named 'sklearn'"

```bash
# Reinstalar scikit-learn
pip install --force-reinstall scikit-learn>=1.3.0
```

### Erro: "SMOTE not found"

```bash
# Reinstalar imbalanced-learn
pip install --force-reinstall imbalanced-learn>=0.11.0
```

### Atualizar pip para evitar problemas

```bash
python -m pip install --upgrade pip
```

---

## 📊 Resumo do Projeto

| Aspecto | Informação |
|--------|-----------|
| **Python** | 3.14.6 |
| **Tipo de Env** | Virtual Environment |
| **Arquivo de deps** | `requirements.txt` |
| **Total de pacotes** | 10 (+ suas dependências transitivas) |
| **Data última atualização** | 2026-07-05 |

