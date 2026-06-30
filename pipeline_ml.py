# Importações básicas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# Importações do Scikit-Learn
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

# Importação do csv
df_batalhas = pd.read_csv('dados/batalhas_pokemon_treino.csv')
print(f"Dataset de batalhas carregado: {df_batalhas.shape[0]} linhas e {df_batalhas.shape[1]} colunas.")

# Importação do csv
df_batalhas = pd.read_csv('dados/batalhas_pokemon_treino.csv')
print(f"Dataset de batalhas carregado: {df_batalhas.shape[0]} linhas e {df_batalhas.shape[1]} colunas.")

# Separando as variáveis preditoras (X) e a variável alvo (y)
X = df_batalhas.drop(columns=['Vitoria_P1'])
y = df_batalhas['Vitoria_P1']

# Divisão em Treino (80%) e Teste (20%) - Corrigido para 'test_size'
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Dados de Treino: {X_train.shape[0]} amostras")
print(f"Dados de Teste: {X_test.shape[0]} amostras")

print("--- Treinando Regressão Logística ---")
model_lr = LogisticRegression(max_iter=1000)
model_lr.fit(X_train, y_train)

# Predição Regressão Logística
y_pred_lr = model_lr.predict(X_test)

print("--- Treinando Random Forest com GridSearchCV ---")

# Definição dos parâmetros (PARA NA HORA DE ESCREVER O RELATÓRIO SABER QUE AQUI É O 'Ajuste de hiperparâmetros (quando aplicável)')
param_grid = {
    'n_estimators': [50, 100],
    'max_depth': [10, 20, None],
    'min_samples_split': [2, 5]
}

rf_base = RandomForestClassifier(random_state=42)

# O GridSearchCV vai testar as combinações cruzando os dados para achar a melhor
grid_search = GridSearchCV(estimator=rf_base, param_grid=param_grid, cv=3, scoring='accuracy', n_jobs=-1)
grid_search.fit(X_train, y_train)

# Melhor modelo encontrado
model_rf = grid_search.best_estimator_
print(f"Melhores parâmetros encontrados: {grid_search.best_params_}")

# Predição Random Forest
y_pred_rf = model_rf.predict(X_test)

print("--- Treinando Rede Neural (MLPClassifier) ---")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model_nn = MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42)
model_nn.fit(X_train_scaled, y_train)

# Predição MPL
y_pred_nn = model_nn.predict(X_test_scaled)

import pickle

# Criar a pasta para salvar os modelos
os.makedirs('modelos_treinados', exist_ok=True)

print("--- Salvando modelos treinados em disco ---")
with open('modelos_treinados/model_rf.pkl', 'wb') as f:
    pickle.dump(model_rf, f)

with open('modelos_treinados/model_lr.pkl', 'wb') as f:
    pickle.dump(model_lr, f)

with open('modelos_treinados/model_nn.pkl', 'wb') as f:
    pickle.dump(model_nn, f)

with open('modelos_treinados/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

# Também precisamos salvar a estrutura de colunas (X) para garantir a ordem no app.py
with open('modelos_treinados/colunas_X.pkl', 'wb') as f:
    pickle.dump(X.columns, f)

print("Todos os modelos foram persistidos com sucesso na pasta 'modelos_treinados'!")



