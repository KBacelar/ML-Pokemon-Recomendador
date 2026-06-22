# Avaliação dos modelos treinados com validação cruzada K-Fold
# Métricas: Precision, Recall e Matriz de Confusão

import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.model_selection import cross_validate, StratifiedKFold
from sklearn.metrics import confusion_matrix

os.makedirs('../resultados', exist_ok=True)

# Carregar dataset de batalhas
df_batalhas = pd.read_csv('../../dados/batalhas_pokemon_treino.csv')
X = df_batalhas.drop(columns=['Vitoria_P1'])
y = df_batalhas['Vitoria_P1']
print(f"Dataset carregado: {X.shape[0]} batalhas, {X.shape[1]} features")

# Carregar modelos treinados e o scaler
with open('../../modelos_treinados/model_rf.pkl', 'rb') as f:
    model_rf = pickle.load(f)
with open('../../modelos_treinados/model_lr.pkl', 'rb') as f:
    model_lr = pickle.load(f)
with open('../../modelos_treinados/model_nn.pkl', 'rb') as f:
    model_nn = pickle.load(f)
with open('../../modelos_treinados/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

# Validação cruzada estratificada com k=5 (mantém proporção de classes nos folds)
kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scoring = ['precision', 'recall']

resultados = {}

cv_rf = cross_validate(model_rf, X, y, cv=kfold, scoring=scoring, n_jobs=-1)
resultados['Random Forest'] = {
    'precision': cv_rf['test_precision'],
    'recall': cv_rf['test_recall']
}

cv_lr = cross_validate(model_lr, X, y, cv=kfold, scoring=scoring, n_jobs=-1)
resultados['Regressão Logística'] = {
    'precision': cv_lr['test_precision'],
    'recall': cv_lr['test_recall']
}

# Rede neural opera sobre dados normalizados
X_scaled = scaler.transform(X)
cv_nn = cross_validate(model_nn, X_scaled, y, cv=kfold, scoring=scoring, n_jobs=-1)
resultados['Rede Neural'] = {
    'precision': cv_nn['test_precision'],
    'recall': cv_nn['test_recall']
}

# Calcular média e desvio padrão das métricas para cada modelo
estatisticas = []
for modelo_nome, metricas in resultados.items():
    for metrica_nome, valores in metricas.items():
        estatisticas.append({
            'Modelo': modelo_nome,
            'Métrica': metrica_nome.capitalize(),
            'Média': np.mean(valores),
            'Desvio Padrão': np.std(valores)
        })

df_stats = pd.DataFrame(estatisticas)
df_stats.to_csv('../resultados/resultados_avaliacao.csv', index=False)

# Exibir resumo no terminal
print(f"\n{'MODELO':<25} {'MÉTRICA':<12} {'MÉDIA':<10} {'DESVIO PADRÃO'}")
for _, row in df_stats.iterrows():
    print(f"{row['Modelo']:<25} {row['Métrica']:<12} {row['Média']:.4f}     ±{row['Desvio Padrão']:.4f}")

# Predições sobre todo o dataset para matrizes de confusão
y_pred_rf = model_rf.predict(X)
y_pred_lr = model_lr.predict(X)
y_pred_nn = model_nn.predict(X_scaled)

cm_rf = confusion_matrix(y, y_pred_rf)
cm_lr = confusion_matrix(y, y_pred_lr)
cm_nn = confusion_matrix(y, y_pred_nn)

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('Matrizes de Confusão', fontsize=16, fontweight='bold')

modelos_cm = [
    ('Random Forest', cm_rf),
    ('Regressão Logística', cm_lr),
    ('Rede Neural', cm_nn)
]

for idx, (nome, cm) in enumerate(modelos_cm):
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx])
    axes[idx].set_title(nome, fontsize=14, fontweight='bold')
    axes[idx].set_xlabel('Predição')
    axes[idx].set_ylabel('Valor Real')
    axes[idx].set_xticklabels(['Derrota P1', 'Vitória P1'])
    axes[idx].set_yticklabels(['Derrota P1', 'Vitória P1'])

plt.tight_layout()
plt.savefig('../resultados/matrizes_confusao.png', dpi=300, bbox_inches='tight')

# Gráfico comparativo de Precision e Recall com barras de erro
df_plot = df_stats[df_stats['Métrica'].isin(['Precision', 'Recall'])]

fig, ax = plt.subplots(figsize=(12, 6))
modelos = df_plot['Modelo'].unique()
metricas = df_plot['Métrica'].unique()
x = np.arange(len(modelos))
width = 0.35

for i, metrica in enumerate(metricas):
    dados = df_plot[df_plot['Métrica'] == metrica]
    medias = dados['Média'].values
    desvios = dados['Desvio Padrão'].values
    ax.bar(x + i*width, medias, width, yerr=desvios, label=metrica, capsize=5, alpha=0.8)
    # Anotar valores acima das barras
    for j, valor in enumerate(medias):
        ax.text(j + i*width, valor + 0.003, f'{valor:.4f}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_xlabel('Modelos', fontsize=12, fontweight='bold')
ax.set_ylabel('Score', fontsize=12, fontweight='bold')
ax.set_title('Comparação de Precision e Recall entre Modelos\n(desvio padrão da validação cruzada K-Fold)',
             fontsize=14, fontweight='bold')
ax.set_xticks(x + width / 2)
ax.set_xticklabels(modelos)
ax.legend(loc='lower right')
ax.grid(axis='y', alpha=0.3)
ax.set_ylim([0.90, 1.0])  # zoom para evidenciar diferenças

plt.tight_layout()
plt.savefig('../resultados/comparacao_modelos.png', dpi=300, bbox_inches='tight')

print("\nArquivos gerados em avaliacao/resultados/:")
print("  - resultados_avaliacao.csv")
print("  - matrizes_confusao.png")
print("  - comparacao_modelos.png")
