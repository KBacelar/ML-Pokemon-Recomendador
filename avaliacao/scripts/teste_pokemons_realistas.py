# Teste de robustez ampliado com 30 Pokémons sintéticos realistas
# Perfis baseados nos percentis reais do dataset de treinamento
# Cobre 6 arquétipos de combate e diversas combinações de vantagem de tipo

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

# Oponente padrão fixado nos valores medianos do dataset real
# Mediana observada: HP=344, Atk=284, Def=262, SpAtk=251, SpDef=262, Speed=256
oponente_padrao = {
    'P2_HP': 344, 'P2_Atk': 284, 'P2_Def': 262,
    'P2_SpAtk': 251, 'P2_SpDef': 262, 'P2_Speed': 256
}

# 30 Pokémons sintéticos organizados em 6 arquétipos
# Stats baseados nos percentis observados no dataset (P10 a P90)
# Combinações de tipo cobrem cenários neutros, favoráveis e desfavoráveis
pokemons_sinteticos = [
    # ARQUÉTIPO 1 - TANQUES (HP alto + Defesa alta, baixa ofensividade)
    {'nome': 'Tanque-01 (Neutro)',           'arquetipo': 'Tanque',
     'P1_HP': 420, 'P1_Atk': 220, 'P1_Def': 360, 'P1_SpAtk': 200, 'P1_SpDef': 340, 'P1_Speed': 180,
     'Vantagem_Tipo_P1': 1.0, 'Vantagem_Tipo_P2': 1.0},
    {'nome': 'Tanque-02 (Vant. 2x)',         'arquetipo': 'Tanque',
     'P1_HP': 400, 'P1_Atk': 240, 'P1_Def': 380, 'P1_SpAtk': 210, 'P1_SpDef': 320, 'P1_Speed': 190,
     'Vantagem_Tipo_P1': 2.0, 'Vantagem_Tipo_P2': 1.0},
    {'nome': 'Tanque-03 (Desvant.)',         'arquetipo': 'Tanque',
     'P1_HP': 430, 'P1_Atk': 200, 'P1_Def': 350, 'P1_SpAtk': 220, 'P1_SpDef': 360, 'P1_Speed': 175,
     'Vantagem_Tipo_P1': 0.5, 'Vantagem_Tipo_P2': 2.0},
    {'nome': 'Tanque-04 (Dupla Vant.)',      'arquetipo': 'Tanque',
     'P1_HP': 410, 'P1_Atk': 230, 'P1_Def': 370, 'P1_SpAtk': 215, 'P1_SpDef': 330, 'P1_Speed': 185,
     'Vantagem_Tipo_P1': 4.0, 'Vantagem_Tipo_P2': 0.5},
    {'nome': 'Tanque-05 (Imunidade Of.)',    'arquetipo': 'Tanque',
     'P1_HP': 425, 'P1_Atk': 235, 'P1_Def': 365, 'P1_SpAtk': 205, 'P1_SpDef': 345, 'P1_Speed': 180,
     'Vantagem_Tipo_P1': 1.0, 'Vantagem_Tipo_P2': 0.0},

    # ARQUÉTIPO 2 - SWEEPERS FÍSICOS (Ataque + Velocidade altos)
    {'nome': 'SweeperFis-01 (Neutro)',       'arquetipo': 'Sweeper Físico',
     'P1_HP': 320, 'P1_Atk': 380, 'P1_Def': 230, 'P1_SpAtk': 200, 'P1_SpDef': 220, 'P1_Speed': 340,
     'Vantagem_Tipo_P1': 1.0, 'Vantagem_Tipo_P2': 1.0},
    {'nome': 'SweeperFis-02 (Vant. 2x)',     'arquetipo': 'Sweeper Físico',
     'P1_HP': 310, 'P1_Atk': 395, 'P1_Def': 225, 'P1_SpAtk': 195, 'P1_SpDef': 215, 'P1_Speed': 350,
     'Vantagem_Tipo_P1': 2.0, 'Vantagem_Tipo_P2': 1.0},
    {'nome': 'SweeperFis-03 (Desvant.)',     'arquetipo': 'Sweeper Físico',
     'P1_HP': 315, 'P1_Atk': 385, 'P1_Def': 220, 'P1_SpAtk': 210, 'P1_SpDef': 218, 'P1_Speed': 345,
     'Vantagem_Tipo_P1': 1.0, 'Vantagem_Tipo_P2': 2.0},
    {'nome': 'SweeperFis-04 (Dupla Desv.)',  'arquetipo': 'Sweeper Físico',
     'P1_HP': 305, 'P1_Atk': 375, 'P1_Def': 215, 'P1_SpAtk': 200, 'P1_SpDef': 210, 'P1_Speed': 355,
     'Vantagem_Tipo_P1': 0.5, 'Vantagem_Tipo_P2': 2.0},
    {'nome': 'SweeperFis-05 (Vant. Forte)',  'arquetipo': 'Sweeper Físico',
     'P1_HP': 325, 'P1_Atk': 390, 'P1_Def': 235, 'P1_SpAtk': 205, 'P1_SpDef': 225, 'P1_Speed': 335,
     'Vantagem_Tipo_P1': 2.0, 'Vantagem_Tipo_P2': 0.5},

    # ARQUÉTIPO 3 - SWEEPERS ESPECIAIS (Ataque Especial + Velocidade altos)
    {'nome': 'SweeperEsp-01 (Neutro)',       'arquetipo': 'Sweeper Especial',
     'P1_HP': 315, 'P1_Atk': 195, 'P1_Def': 220, 'P1_SpAtk': 380, 'P1_SpDef': 235, 'P1_Speed': 345,
     'Vantagem_Tipo_P1': 1.0, 'Vantagem_Tipo_P2': 1.0},
    {'nome': 'SweeperEsp-02 (Vant. 2x)',     'arquetipo': 'Sweeper Especial',
     'P1_HP': 310, 'P1_Atk': 200, 'P1_Def': 215, 'P1_SpAtk': 395, 'P1_SpDef': 230, 'P1_Speed': 350,
     'Vantagem_Tipo_P1': 2.0, 'Vantagem_Tipo_P2': 1.0},
    {'nome': 'SweeperEsp-03 (Desvant.)',     'arquetipo': 'Sweeper Especial',
     'P1_HP': 320, 'P1_Atk': 190, 'P1_Def': 225, 'P1_SpAtk': 370, 'P1_SpDef': 240, 'P1_Speed': 340,
     'Vantagem_Tipo_P1': 1.0, 'Vantagem_Tipo_P2': 2.0},
    {'nome': 'SweeperEsp-04 (Vant. Forte)',  'arquetipo': 'Sweeper Especial',
     'P1_HP': 318, 'P1_Atk': 198, 'P1_Def': 222, 'P1_SpAtk': 388, 'P1_SpDef': 232, 'P1_Speed': 348,
     'Vantagem_Tipo_P1': 4.0, 'Vantagem_Tipo_P2': 0.5},
    {'nome': 'SweeperEsp-05 (Neutro)',       'arquetipo': 'Sweeper Especial',
     'P1_HP': 312, 'P1_Atk': 192, 'P1_Def': 218, 'P1_SpAtk': 375, 'P1_SpDef': 228, 'P1_Speed': 342,
     'Vantagem_Tipo_P1': 1.0, 'Vantagem_Tipo_P2': 1.0},

    # ARQUÉTIPO 4 - BALANCEADOS (Stats medianos em todos os atributos)
    {'nome': 'Balanceado-01 (Neutro)',       'arquetipo': 'Balanceado',
     'P1_HP': 345, 'P1_Atk': 285, 'P1_Def': 265, 'P1_SpAtk': 250, 'P1_SpDef': 260, 'P1_Speed': 255,
     'Vantagem_Tipo_P1': 1.0, 'Vantagem_Tipo_P2': 1.0},
    {'nome': 'Balanceado-02 (Vant. 2x)',     'arquetipo': 'Balanceado',
     'P1_HP': 350, 'P1_Atk': 290, 'P1_Def': 270, 'P1_SpAtk': 255, 'P1_SpDef': 265, 'P1_Speed': 260,
     'Vantagem_Tipo_P1': 2.0, 'Vantagem_Tipo_P2': 1.0},
    {'nome': 'Balanceado-03 (Desvant.)',     'arquetipo': 'Balanceado',
     'P1_HP': 340, 'P1_Atk': 280, 'P1_Def': 260, 'P1_SpAtk': 245, 'P1_SpDef': 258, 'P1_Speed': 250,
     'Vantagem_Tipo_P1': 1.0, 'Vantagem_Tipo_P2': 2.0},
    {'nome': 'Balanceado-04 (Dupla Vant.)',  'arquetipo': 'Balanceado',
     'P1_HP': 348, 'P1_Atk': 287, 'P1_Def': 268, 'P1_SpAtk': 252, 'P1_SpDef': 263, 'P1_Speed': 257,
     'Vantagem_Tipo_P1': 2.0, 'Vantagem_Tipo_P2': 0.5},
    {'nome': 'Balanceado-05 (Dupla Desv.)',  'arquetipo': 'Balanceado',
     'P1_HP': 342, 'P1_Atk': 282, 'P1_Def': 262, 'P1_SpAtk': 248, 'P1_SpDef': 257, 'P1_Speed': 252,
     'Vantagem_Tipo_P1': 0.5, 'Vantagem_Tipo_P2': 2.0},

    # ARQUÉTIPO 5 - HÍBRIDOS (Ofensivos mistos físico/especial)
    {'nome': 'Hibrido-01 (Neutro)',          'arquetipo': 'Híbrido',
     'P1_HP': 360, 'P1_Atk': 330, 'P1_Def': 280, 'P1_SpAtk': 320, 'P1_SpDef': 275, 'P1_Speed': 290,
     'Vantagem_Tipo_P1': 1.0, 'Vantagem_Tipo_P2': 1.0},
    {'nome': 'Hibrido-02 (Vant. 2x)',        'arquetipo': 'Híbrido',
     'P1_HP': 365, 'P1_Atk': 335, 'P1_Def': 285, 'P1_SpAtk': 325, 'P1_SpDef': 280, 'P1_Speed': 295,
     'Vantagem_Tipo_P1': 2.0, 'Vantagem_Tipo_P2': 1.0},
    {'nome': 'Hibrido-03 (Desvant.)',        'arquetipo': 'Híbrido',
     'P1_HP': 355, 'P1_Atk': 325, 'P1_Def': 275, 'P1_SpAtk': 315, 'P1_SpDef': 270, 'P1_Speed': 285,
     'Vantagem_Tipo_P1': 1.0, 'Vantagem_Tipo_P2': 2.0},
    {'nome': 'Hibrido-04 (Vant. Forte)',     'arquetipo': 'Híbrido',
     'P1_HP': 358, 'P1_Atk': 328, 'P1_Def': 278, 'P1_SpAtk': 318, 'P1_SpDef': 273, 'P1_Speed': 288,
     'Vantagem_Tipo_P1': 4.0, 'Vantagem_Tipo_P2': 1.0},
    {'nome': 'Hibrido-05 (Dupla Desv.)',     'arquetipo': 'Híbrido',
     'P1_HP': 362, 'P1_Atk': 332, 'P1_Def': 282, 'P1_SpAtk': 322, 'P1_SpDef': 277, 'P1_Speed': 292,
     'Vantagem_Tipo_P1': 0.5, 'Vantagem_Tipo_P2': 4.0},

    # ARQUÉTIPO 6 - LENDÁRIOS / SUBPAR (extremos dentro da distribuição real)
    {'nome': 'Lendario-01 (Stats P90)',      'arquetipo': 'Lendário',
     'P1_HP': 450, 'P1_Atk': 400, 'P1_Def': 370, 'P1_SpAtk': 380, 'P1_SpDef': 360, 'P1_Speed': 360,
     'Vantagem_Tipo_P1': 1.0, 'Vantagem_Tipo_P2': 1.0},
    {'nome': 'Lendario-02 (P90+Vant.)',      'arquetipo': 'Lendário',
     'P1_HP': 460, 'P1_Atk': 410, 'P1_Def': 375, 'P1_SpAtk': 385, 'P1_SpDef': 365, 'P1_Speed': 365,
     'Vantagem_Tipo_P1': 2.0, 'Vantagem_Tipo_P2': 0.5},
    {'nome': 'Lendario-03 (P90+Desv.)',      'arquetipo': 'Lendário',
     'P1_HP': 440, 'P1_Atk': 395, 'P1_Def': 365, 'P1_SpAtk': 375, 'P1_SpDef': 355, 'P1_Speed': 355,
     'Vantagem_Tipo_P1': 0.5, 'Vantagem_Tipo_P2': 2.0},
    {'nome': 'Subpar-01 (Stats P10)',        'arquetipo': 'Subpar',
     'P1_HP': 285, 'P1_Atk': 200, 'P1_Def': 195, 'P1_SpAtk': 185, 'P1_SpDef': 195, 'P1_Speed': 175,
     'Vantagem_Tipo_P1': 1.0, 'Vantagem_Tipo_P2': 1.0},
    {'nome': 'Subpar-02 (P10+Vant. Forte)',  'arquetipo': 'Subpar',
     'P1_HP': 290, 'P1_Atk': 205, 'P1_Def': 200, 'P1_SpAtk': 190, 'P1_SpDef': 200, 'P1_Speed': 180,
     'Vantagem_Tipo_P1': 4.0, 'Vantagem_Tipo_P2': 0.5},
]

resultados_teste = []

for pk in pokemons_sinteticos:
    nome = pk.pop('nome')
    arquetipo = pk.pop('arquetipo')
    features = pd.DataFrame([{**pk, **oponente_padrao}])
    features = features[colunas_X]

    prob_rf = model_rf.predict_proba(features)[0][1]
    prob_lr = model_lr.predict_proba(features)[0][1]
    prob_nn = model_nn.predict_proba(scaler.transform(features))[0][1]

    pred_rf = 'SIM' if prob_rf >= 0.5 else 'NÃO'
    pred_lr = 'SIM' if prob_lr >= 0.5 else 'NÃO'
    pred_nn = 'SIM' if prob_nn >= 0.5 else 'NÃO'
    concordancia = 'TOTAL' if pred_rf == pred_lr == pred_nn else 'PARCIAL'

    resultados_teste.append({
        'Pokémon': nome,
        'Arquétipo': arquetipo,
        'Vantagem_P1': pk['Vantagem_Tipo_P1'],
        'Vantagem_P2': pk['Vantagem_Tipo_P2'],
        'RF_Vitoria': pred_rf,
        'RF_Confianca': f"{prob_rf*100:.1f}%",
        'LR_Vitoria': pred_lr,
        'LR_Confianca': f"{prob_lr*100:.1f}%",
        'NN_Vitoria': pred_nn,
        'NN_Confianca': f"{prob_nn*100:.1f}%",
        'Concordancia': concordancia
    })

df_resultados = pd.DataFrame(resultados_teste)
df_resultados.to_csv('../resultados/teste_pokemons_realistas.csv', index=False)

# Estatísticas agregadas
total = len(resultados_teste)
concordancia_total = sum(1 for r in resultados_teste if r['Concordancia'] == 'TOTAL')
taxa_concordancia = concordancia_total / total * 100

print(f"\nResumo: {total} Pokémons sintéticos realistas testados")
print(f"Concordância total (3 modelos): {concordancia_total}/{total} ({taxa_concordancia:.1f}%)")
print(f"Concordância parcial: {total - concordancia_total}/{total}")

# Gráfico horizontal de barras agrupadas (30 perfis x 3 modelos)
nomes_pk = [r['Pokémon'] for r in resultados_teste]
conf_rf = [float(r['RF_Confianca'].replace('%', '')) for r in resultados_teste]
conf_lr = [float(r['LR_Confianca'].replace('%', '')) for r in resultados_teste]
conf_nn = [float(r['NN_Confianca'].replace('%', '')) for r in resultados_teste]

y = np.arange(len(nomes_pk))
height = 0.27

fig, ax = plt.subplots(figsize=(14, 14))
ax.barh(y - height, conf_rf, height, label='Random Forest', alpha=0.85, color='#1f77b4')
ax.barh(y, conf_lr, height, label='Regressão Logística', alpha=0.85, color='#ff7f0e')
ax.barh(y + height, conf_nn, height, label='Rede Neural', alpha=0.85, color='#2ca02c')

# Linha vertical em 50% (limiar de decisão)
ax.axvline(x=50, color='red', linestyle='--', linewidth=1, alpha=0.6, label='Limiar 50%')

ax.set_xlabel('Confiança de Vitória (%)', fontsize=12, fontweight='bold')
ax.set_ylabel('Pokémons Sintéticos Realistas', fontsize=12, fontweight='bold')
ax.set_title('Confiança dos Modelos em 30 Pokémons Sintéticos Realistas\n(Stats baseados nos percentis do dataset real)',
             fontsize=14, fontweight='bold')
ax.set_yticks(y)
ax.set_yticklabels(nomes_pk, fontsize=9)
ax.invert_yaxis()
ax.legend(loc='lower right')
ax.grid(axis='x', alpha=0.3)
ax.set_xlim([0, 105])

plt.tight_layout()
plt.savefig('../resultados/teste_pokemons_realistas_confianca.png', dpi=200, bbox_inches='tight')

# Gráfico secundário: taxa de concordância por arquétipo
arquetipos = df_resultados['Arquétipo'].unique()
concordancia_por_arq = []
for arq in arquetipos:
    subset = df_resultados[df_resultados['Arquétipo'] == arq]
    total_arq = len(subset)
    concord_arq = sum(1 for _, r in subset.iterrows() if r['Concordancia'] == 'TOTAL')
    concordancia_por_arq.append(concord_arq / total_arq * 100)

fig2, ax2 = plt.subplots(figsize=(10, 5))
bars = ax2.bar(arquetipos, concordancia_por_arq, color='#2ca02c', alpha=0.85)
ax2.set_ylabel('Concordância Total dos 3 Modelos (%)', fontsize=11, fontweight='bold')
ax2.set_xlabel('Arquétipo', fontsize=11, fontweight='bold')
ax2.set_title('Concordância entre os Três Modelos por Arquétipo de Pokémon',
              fontsize=13, fontweight='bold')
ax2.set_ylim([0, 110])
ax2.grid(axis='y', alpha=0.3)
for bar, valor in zip(bars, concordancia_por_arq):
    ax2.text(bar.get_x() + bar.get_width()/2, valor + 2, f'{valor:.0f}%',
             ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('../resultados/teste_pokemons_realistas_concordancia.png', dpi=200, bbox_inches='tight')

print("\nArquivos gerados em avaliacao/resultados/:")
print("  - teste_pokemons_realistas.csv")
print("  - teste_pokemons_realistas_confianca.png")
print("  - teste_pokemons_realistas_concordancia.png")
