# Comparativo Evolutivo — Random Forest Original vs Otimizado

## 📋 Resumo Executivo

Comparação entre o modelo Random Forest do **Módulo 1** (data_triagem.ipynb) e o modelo **otimizado via Algoritmo Genético** (algoritmo_genetico.ipynb).

---

## 📊 Resultados Comparativos (Teste)

| Métrica | RF Original | RF Otimizado (AG) | Variação |
|---------|-------------|-------------------|----------|
| **Acurácia** | 92,36% | 92,69% | **+0,33 p.p.** ✅ |
| **Macro F1** | 0,9101 | 0,9118 | **+0,17%** ✅ |
| **Recall nível 2 (teste)** | 92,04% | 92,04% | **Sem mudança** ➡️ |
| **Recall nível 3 (teste)** | 94,38% | 93,26% | **−1,12 p.p.** ❌ |
| **Subtriagem (casos)** | 86 | 95 | **+9 casos** ❌ |
| **Score treino (SMOTE)** | 95,66% | 98,21% | **+2,55 p.p.** |
| **Gap treino-teste (p.p.)** | 3,3 | 5,5 | **+2,2 p.p.** ⚠️ |

---

## 🎯 Análise Detalhada

### ✅ Melhorias Observadas

1. **Acurácia global**: +0,33 p.p. (92,36% → 92,69%)
   - Ganho pequeno, mas consistente em casos corretamente classificados

2. **Macro F1**: +0,17% (0,9101 → 0,9118)
   - Melhor equilíbrio entre precisão e recall nas 4 classes

---

### ❌ Pioras Observadas

1. **Recall do nível 3** (casos mais graves): −1,12 p.p.
   - RF Original detecta **94,38%** dos casos críticos
   - RF Otimizado detecta **93,26%** — 9 casos graves deixados passar

2. **Subtriagem aumentou**:
   - De 86 para 95 casos — aumento de 10,5% em erros clínicos potenciais
   - **Risco clínico**: pacientes graves classificados como menos urgentes

3. **Overfitting mais evidente**:
   - Gap treino-teste subiu de 3,3 p.p. para 5,5 p.p.
   - O modelo otimizado memoriza mais os dados de treino (SMOTE inflacionado em 98,21%)

---

## 🔍 Hiperparâmetros Otimizados

**Experimento vencedor**: Exp. 2 — Refinamento

- `n_estimators`: 22 (vs 20 original)
- `max_depth`: 19 (vs 10 original) — permite árvores mais profundas
- `min_samples_split`: 6
- `min_samples_leaf`: 3
- `criterion`: entropy
- `class_weight`: None

**Interpretação**: O AG aumentou a profundidade das árvores, permitindo maior complexidade, o que melhorou acurácia geral mas prejudicou recall dos níveis urgentes.

---

## 🏥 Impacto Clínico

Em um sistema de triagem de pronto-socorro:

| Aspecto | Implicação |
|--------|-----------|
| **Acurácia +0,33%** | Ganho marginal, praticamente imperceptível clinicamente |
| **Recall nível 3 −1,12%** | Aproximadamente **1 em 90 casos críticos deixados passar** |
| **Subtriagem +9 casos** | Risco de atraso no atendimento de pacientes graves |
| **Gap treino-teste +2,2 p.p.** | Modelo pode generalizar pior em dados não vistos |

---

## 💡 Conclusão

A otimização com **Algoritmo Genético resultou em ganho marginal e contraditório**:

1. ✅ **Ganhou em acurácia geral** (+0,33 p.p.)
2. ❌ **Perdeu em segurança clínica** (recall nível 3 e subtriagem)
3. ⚠️ **Maior overfitting** (gap treino-teste aumentou)

### Recomendação Final

**O modelo RF Original (Módulo 1) permanece como escolha superior** para este caso de uso porque:

- **Prioridade clínica**: em triagem, recall das classes urgentes (níveis 2–3) é mais crítico que acurácia global
- **Modelo já bem ajustado**: o RF original (92,36% acurácia, 94,38% recall nível 3) era já muito bem calibrado — havia pouco espaço para melhoria significativa
- **Menores riscos**: menos subtriagem (86 vs 95 casos), melhor detecção de emergências
- **Menor overfitting**: gap treino-teste mais controlado (3,3 vs 5,5 p.p.)

### Valor do AG

Embora o modelo final não supere o baseline, o **Algoritmo Genético cumpriu seu objetivo pedagógico e metodológico**:
- Documentou busca **sistemática** no espaço de hiperparâmetros (vs ajustes manuais)
- Implementou componentes genéticos completos (seleção, cruzamento, mutação, elitismo)
- Validou que o modelo manual do Módulo 1 era já robustamente otimizado

---

## 📝 Metadados

- **Data da comparação**: 2026-07-05
- **Dataset**: synthetic_medical_triage.csv
- **Split**: 80% treino / 20% teste (random_state=7)
- **Balanceamento**: SMOTE em treino
- **Classes**: 4 níveis de triagem (0=leve, 3=crítico)

