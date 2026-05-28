# Teste de robustez dos modelos com Pokémons sintéticos
# Cria perfis extremos e verifica a concordância entre os três modelos

import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import os

os.makedirs('../resultados', exist_ok=True)

# Carregar modelos, scaler e ordem de colunas
with open('../../modelos_treinados/model_rf.pkl', 'rb') as f:
    model_rf = pickle.load(f)
with open('../../modelos_treinados/model_lr.pkl', 'rb') as f:
    model_lr = pickle.load(f)
with open('../../modelos_treinados/model_nn.pkl', 'rb') as f:
    model_nn = pickle.load(f)
with open('../../modelos_treinados/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)
with open('../../modelos_treinados/colunas_X.pkl', 'rb') as f:
    colunas_X = pickle.load(f)

# Oponente padrão de stats medianos para comparação consistente
oponente_padrao = {
    'P2_HP': 80, 'P2_Atk': 80, 'P2_Def': 80,
    'P2_SpAtk': 80, 'P2_SpDef': 80, 'P2_Speed': 80
}

# Pokémons sintéticos com perfis variados
pokemons_sinteticos = [
    {
        'nome': 'TankBot (Defensor Extremo)',
        'P1_HP': 200, 'P1_Atk': 40, 'P1_Def': 250,
        'P1_SpAtk': 40, 'P1_SpDef': 250, 'P1_Speed': 30,
        'Vantagem_Tipo_P1': 1.0, 'Vantagem_Tipo_P2': 1.0
    },
    {
        'nome': 'SpeedDemon (Atacante Veloz)',
        'P1_HP': 60, 'P1_Atk': 150, 'P1_Def': 50,
        'P1_SpAtk': 150, 'P1_SpDef': 50, 'P1_Speed': 200,
        'Vantagem_Tipo_P1': 1.0, 'Vantagem_Tipo_P2': 1.0
    },
    {
        'nome': 'AllRounder (Equilibrado)',
        'P1_HP': 100, 'P1_Atk': 100, 'P1_Def': 100,
        'P1_SpAtk': 100, 'P1_SpDef': 100, 'P1_Speed': 100,
        'Vantagem_Tipo_P1': 1.0, 'Vantagem_Tipo_P2': 1.0
    },
    {
        'nome': 'Weakling (Muito Fraco)',
        'P1_HP': 30, 'P1_Atk': 20, 'P1_Def': 20,
        'P1_SpAtk': 20, 'P1_SpDef': 20, 'P1_Speed': 20,
        'Vantagem_Tipo_P1': 1.0, 'Vantagem_Tipo_P2': 1.0
    },
    {
        'nome': 'TypeMaster (Vantagem de Tipo 2x)',
        'P1_HP': 90, 'P1_Atk': 100, 'P1_Def': 90,
        'P1_SpAtk': 100, 'P1_SpDef': 90, 'P1_Speed': 90,
        'Vantagem_Tipo_P1': 2.0, 'Vantagem_Tipo_P2': 0.5
    }
]

resultados_teste = []

for pk in pokemons_sinteticos:
    nome = pk.pop('nome')
    features = pd.DataFrame([{**pk, **oponente_padrao}])
    features = features[colunas_X]

    prob_rf = model_rf.predict_proba(features)[0][1]
    prob_lr = model_lr.predict_proba(features)[0][1]
    prob_nn = model_nn.predict_proba(scaler.transform(features))[0][1]

    resultados_teste.append({
        'Pokémon': nome,
        'RF_Vitoria': 'SIM' if prob_rf >= 0.5 else 'NÃO',
        'RF_Confianca': f"{prob_rf*100:.1f}%",
        'LR_Vitoria': 'SIM' if prob_lr >= 0.5 else 'NÃO',
        'LR_Confianca': f"{prob_lr*100:.1f}%",
        'NN_Vitoria': 'SIM' if prob_nn >= 0.5 else 'NÃO',
        'NN_Confianca': f"{prob_nn*100:.1f}%"
    })

    print(f"{nome}")
    print(f"  Random Forest:       {'VITÓRIA' if prob_rf >= 0.5 else 'DERROTA'} ({prob_rf*100:.1f}%)")
    print(f"  Regressão Logística: {'VITÓRIA' if prob_lr >= 0.5 else 'DERROTA'} ({prob_lr*100:.1f}%)")
    print(f"  Rede Neural:         {'VITÓRIA' if prob_nn >= 0.5 else 'DERROTA'} ({prob_nn*100:.1f}%)\n")

df_resultados = pd.DataFrame(resultados_teste)
df_resultados.to_csv('../resultados/teste_pokemons_novos.csv', index=False)

# Gráfico de barras agrupadas com a confiança de vitória de cada modelo
nomes_pk = [r['Pokémon'] for r in resultados_teste]
conf_rf = [float(r['RF_Confianca'].replace('%', '')) for r in resultados_teste]
conf_lr = [float(r['LR_Confianca'].replace('%', '')) for r in resultados_teste]
conf_nn = [float(r['NN_Confianca'].replace('%', '')) for r in resultados_teste]

x = np.arange(len(nomes_pk))
width = 0.25

fig, ax = plt.subplots(figsize=(14, 6))
ax.bar(x - width, conf_rf, width, label='Random Forest', alpha=0.85)
ax.bar(x, conf_lr, width, label='Regressão Logística', alpha=0.85)
ax.bar(x + width, conf_nn, width, label='Rede Neural', alpha=0.85)

ax.set_xlabel('Pokémons Sintéticos', fontsize=12, fontweight='bold')
ax.set_ylabel('Confiança de Vitória (%)', fontsize=12, fontweight='bold')
ax.set_title('Confiança dos Modelos em Pokémons Sintéticos', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(nomes_pk, rotation=15, ha='right')
ax.legend()
ax.grid(axis='y', alpha=0.3)
ax.set_ylim([0, 110])

plt.tight_layout()
plt.savefig('../resultados/teste_pokemons_confianca.png', dpi=300, bbox_inches='tight')

print("Arquivos gerados em avaliacao/resultados/:")
print("  - teste_pokemons_novos.csv")
print("  - teste_pokemons_confianca.png")
