import shap
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

shap.initjs()

print("--- Carregando modelos treinados em memória ---")

with open('../modelos_treinados/model_rf.pkl', 'rb') as f:
    model_rf = pickle.load(f)

with open('../modelos_treinados/model_lr.pkl', 'rb') as f:
    model_lr = pickle.load(f)

with open('../modelos_treinados/model_nn.pkl', 'rb') as f:
    model_nn = pickle.load(f)

with open('../modelos_treinados/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

with open('../modelos_treinados/colunas_X.pkl', 'rb') as f:
    colunas_X = pickle.load(f)

print("--- Carregando os dados de treinamento e teste ---")

data = np.load("../modelos_treinados/train_test_data.npz")
print("Variáveis no arquivo:", data.files)

X_train = data['X_train']
y_train = data['y_train']
X_test = data['X_test']
y_test = data['y_test']

print("Dados de treinamento e teste carregados com sucesso!")

print("--- Gerando Análise SHAP para Random Forest ---")
# TreeExplainer é super otimizado para Random Forest
explainer_rf = shap.TreeExplainer(model_rf)
shap_values_rf = explainer_rf.shap_values(X_test)

# Se for classificação binária, o shap_values pode retornar uma lista [classe_0, classe_1]
# Vamos pegar a explicação da classe 1 (Vitória)
if isinstance(shap_values_rf, list):
    # Comportamento antigo do SHAP
    shap_vals_rf = shap_values_rf[1]
elif len(shap_values_rf.shape) == 3:
    # Comportamento novo do SHAP: Array 3D (amostras, features, classes)
    # Fatiamos pegando: TODAS as linhas (:), TODAS as colunas (:), e o índice 1 da classe
    shap_vals_rf = shap_values_rf[:, :, 1] 
else:
    shap_vals_rf = shap_values_rf

plt.figure(figsize=(10, 6))
plt.title("Impacto das Features na Vitória (Random Forest)")
shap.summary_plot(shap_vals_rf, X_test, feature_names=colunas_X, show=False)
plt.tight_layout()
plt.savefig("shap_random_forest.png", dpi=300)
plt.close()
print("Gráfico da Random Forest salvo como 'shap_random_forest.png'")

print("--- Gerando Análise SHAP para Regressão Logística ---")
# LinearExplainer precisa dos dados como referência
explainer_lr = shap.LinearExplainer(model_lr, X_test)
shap_values_lr = explainer_lr.shap_values(X_test)

plt.figure(figsize=(10, 6))
plt.title("Impacto das Features na Vitória (Regressão Logística)")
shap.summary_plot(shap_values_lr, X_test, feature_names=colunas_X, show=False)
plt.tight_layout()
plt.savefig("shap_regressao_logistica.png", dpi=300)
plt.close()
print("Gráfico da Regressão Logística salvo como 'shap_regressao_logistica.png'")

print("--- Gerando Análise SHAP para Rede Neural (MLP) ---")
# Para a Rede Neural, OS DADOS PRECISAM ESTAR ESCALONADOS, assim como no pipeline original
X_test_scaled = scaler.transform(X_test)

# O KernelExplainer é genérico e mais lento, por isso passamos o predict_proba e uma amostra menor como "fundo"
X_fundo = shap.sample(X_test_scaled, 50) # Fundo resumido para a matemática
explainer_nn = shap.KernelExplainer(model_nn.predict_proba, X_fundo)
# Calculamos os SHAP values apenas para as 50 primeiras linhas para não travar o PC
shap_values_nn = explainer_nn.shap_values(X_test_scaled[:50])

# Pega apenas a classe 1 (Vitória)
if isinstance(shap_values_nn, list):
    shap_vals_nn = shap_values_nn[1]
else:
    # KernelExplainer pode retornar matriz 3D, pegamos a dimensão da classe 1
    shap_vals_nn = shap_values_nn[:,:,1] if len(shap_values_nn.shape) == 3 else shap_values_nn

plt.figure(figsize=(10, 6))
plt.title("Impacto das Features na Vitória (Rede Neural)")
# Passamos os nomes das colunas originais para o gráfico não ficar com números vazios (0, 1, 2...)
shap.summary_plot(shap_vals_nn, X_test_scaled[:50], feature_names=colunas_X, show=False)
plt.tight_layout()
plt.savefig("shap_rede_neural.png", dpi=300)
plt.close()
print("Gráfico da Rede Neural salvo como 'shap_rede_neural.png'")

print("--- Análise Concluída! Verifique as imagens geradas na pasta. ---")

