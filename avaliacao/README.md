# Avaliação de Modelos - Sistema de Predição de Batalhas Pokémon

Esta pasta contém os scripts e resultados da etapa de avaliação dos modelos de Machine Learning treinados pelo backend. A avaliação utiliza validação cruzada estratificada com métricas de Precision, Recall e Matriz de Confusão.

---

## Estrutura

```
avaliacao/
├── scripts/
│   ├── avaliacao_modelos.py           # Validação cruzada e métricas
│   ├── teste_pokemon_novo.py          # Testes de robustez com dados sintéticos
│   ├── gerar_relatorio.py             # Geração do relatório HTML
│   └── executar_avaliacao_completa.py # Executa os três scripts em sequência
│
└── resultados/                        # Saídas geradas em tempo de execução
    ├── relatorio_completo.html
    ├── resumo_avaliacao.txt
    ├── resultados_avaliacao.csv
    ├── teste_pokemons_novos.csv
    ├── matrizes_confusao.png
    ├── comparacao_modelos.png
    └── teste_pokemons_confianca.png
```

---

## Origem dos Dados e dos Modelos

A avaliação não treina modelos novos; ela utiliza os artefatos gerados pelas etapas anteriores do pipeline.

| Arquivo | Conteúdo | Origem |
|---------|----------|--------|
| `dados/batalhas_pokemon_treino.csv` | 10.000 batalhas simuladas | `simulador.py` |
| `dados/pokemonDB_dataset.csv` | Atributos base dos Pokémons | Dataset público |
| `modelos_treinados/model_rf.pkl` | Random Forest treinado | `pipeline_ml.py` |
| `modelos_treinados/model_lr.pkl` | Regressão Logística treinada | `pipeline_ml.py` |
| `modelos_treinados/model_nn.pkl` | Rede Neural (MLP) treinada | `pipeline_ml.py` |
| `modelos_treinados/scaler.pkl` | StandardScaler ajustado para a rede neural | `pipeline_ml.py` |
| `modelos_treinados/colunas_X.pkl` | Ordem das features usada no treinamento | `pipeline_ml.py` |

O dataset de batalhas contém 14 features (HP, Attack, Defense, Special Attack, Special Defense e Speed do P1 e do P2, além de Vantagem_Tipo_P1 e Vantagem_Tipo_P2) e uma variável alvo `Vitoria_P1` (1 se P1 venceu, 0 caso contrário).

---

## Metodologia

### Validação Cruzada (Stratified K-Fold, k=5)

O dataset é particionado em 5 folds preservando a proporção entre as classes. Cada modelo é treinado e avaliado 5 vezes, alternando o fold de teste. As métricas reportadas correspondem à média e ao desvio padrão dessas execuções. Essa estratégia reduz o viés de uma única divisão treino/teste e fornece uma estimativa mais estável de desempenho.

A configuração utilizada está em `scripts/avaliacao_modelos.py`:

```python
kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv = cross_validate(modelo, X, y, cv=kfold, scoring=['precision', 'recall'])
```

### Métricas

- **Precision**: proporção de predições positivas que estavam corretas.
- **Recall**: proporção de positivos reais que foram identificados.
- **Matriz de Confusão**: distribuição de acertos e erros por classe.

### Testes de Robustez

O script `teste_pokemon_novo.py` define 5 Pokémons sintéticos com perfis extremos (defensor, atacante veloz, equilibrado, fraco e com vantagem de tipo) e os submete aos três modelos contra um oponente padrão de stats medianos. O objetivo é observar:

- Concordância entre os modelos em cenários fora da distribuição de treino.
- Coerência das predições com perfis estatísticos extremos.

---

## Execução

### Pré-requisitos

- Modelos treinados disponíveis em `modelos_treinados/`.
- Dataset de batalhas em `dados/batalhas_pokemon_treino.csv`.
- Ambiente Python com dependências instaladas (`pip install -r requirements.txt`).

### Comando

A partir da raiz do projeto:

```bash
python executar_avaliacao.py
```

Para apagar resultados anteriores e regerar tudo:

```bash
rm -rf avaliacao/resultados/* && python executar_avaliacao.py
```

### Execução individual dos scripts

Os scripts esperam ser executados a partir de `avaliacao/scripts/`:

```bash
cd avaliacao/scripts
python avaliacao_modelos.py
python teste_pokemon_novo.py
python gerar_relatorio.py
```

---

## Saídas

Todas as saídas são gravadas em `avaliacao/resultados/`.

| Arquivo | Descrição |
|---------|-----------|
| `resultados_avaliacao.csv` | Métricas (Precision, Recall) por modelo, com média e desvio padrão. |
| `teste_pokemons_novos.csv` | Predições e nível de confiança dos modelos sobre os Pokémons sintéticos. |
| `matrizes_confusao.png` | Matrizes de confusão dos três modelos lado a lado. |
| `comparacao_modelos.png` | Gráfico de barras comparando Precision e Recall com desvio padrão. |
| `teste_pokemons_confianca.png` | Confiança de vitória prevista por cada modelo para os Pokémons sintéticos. |
| `resumo_avaliacao.txt` | Resumo das principais métricas em texto. |
| `relatorio_completo.html` | Relatório consolidado com tabelas, gráficos e análise. |

---

## Fluxo do Projeto

```
simulador.py        -> dados/batalhas_pokemon_treino.csv
pipeline_ml.py      -> modelos_treinados/*.pkl
avaliacao/scripts/  -> avaliacao/resultados/*
app.py              -> consome modelos_treinados/*.pkl em produção
```

Os scripts desta pasta consomem os mesmos artefatos `.pkl` utilizados pelo backend (`app.py`), garantindo que a avaliação reflita o comportamento dos modelos em produção.
