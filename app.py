import pickle
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from dados_processados import limpar_dados_pokemon  # Suas funções do projeto
from utils import get_effectiveness

app = Flask(__name__)
CORS(app)  # Permite que o React se conecte sem bloqueios de segurança [cite: 193]

print("--- Carregando modelos treinados em memória ---")
# Carrega instantaneamente os modelos que foram gerados pelo pipeline
with open('modelos_treinados/model_rf.pkl', 'rb') as f:
    model_rf = pickle.load(f)

with open('modelos_treinados/model_lr.pkl', 'rb') as f:
    model_lr = pickle.load(f)

with open('modelos_treinados/model_nn.pkl', 'rb') as f:
    model_nn = pickle.load(f)

with open('modelos_treinados/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

with open('modelos_treinados/colunas_X.pkl', 'rb') as f:
    colunas_X = pickle.load(f)

print("Modelos prontos para receber requisições do React!")

@app.route('/battle/matchups', methods=['POST'])
def battle_matchups():

    # Recebe os dados vindos do front-end
    dados = request.get_json()
    nome_pokemon = dados.get('pokemon', {}).get('name')
    min_win_rate = dados.get('minWinRate', 50) / 100.0
    limit = dados.get('limit', 20)

    df_pk = limpar_dados_pokemon()
    nome_pokemon = nome_pokemon.title()

    if nome_pokemon not in df_pk['Pokemon'].values:
        return jsonify({"error": "Pokémon não encontrado"}), 404
    
    meu_pk = df_pk[df_pk['Pokemon'] == nome_pokemon].iloc[0]
    
    lista_predicoes = []

    for _, oponente in df_pk.iterrows():
        if oponente['Pokemon'] == meu_pk['Pokemon']: continue

        # Calcula a vantagem que o meu Pokémon tem contra o oponente
        eff_meu = max(get_effectiveness(meu_pk['Type1'], oponente['Type1'], oponente['Type2']),
                      get_effectiveness(meu_pk['Type2'], oponente['Type1'], oponente['Type2']))
                      
        # Calcula a vantagem que o oponente tem contra o meu Pokémon
        eff_opo = max(get_effectiveness(oponente['Type1'], meu_pk['Type1'], meu_pk['Type2']),
                      get_effectiveness(oponente['Type2'], meu_pk['Type1'], meu_pk['Type2']))
            
        # Montar a linha de features incluindo as colunas numéricas de vantagem
        features_combate = pd.DataFrame([{
            'P1_HP': meu_pk['HP Max'], 'P1_Atk': meu_pk['Attack Max'], 'P1_Def': meu_pk['Defense Max'], 
            'P1_SpAtk': meu_pk['Special Attack Max'], 'P1_SpDef': meu_pk['Special Defense Max'], 'P1_Speed': meu_pk['Speed Max'],
            'P2_HP': oponente['HP Max'], 'P2_Atk': oponente['Attack Max'], 'P2_Def': oponente['Defense Max'], 
            'P2_SpAtk': oponente['Special Attack Max'], 'P2_SpDef': oponente['Special Defense Max'], 'P2_Speed': oponente['Speed Max'],
            'Vantagem_Tipo_P1': eff_meu,
            'Vantagem_Tipo_P2': eff_opo
        }])

        # GARANTIA: Forçar a mesma ordem de colunas usada no treinamento
        features_combate = features_combate[colunas_X]
        
        # --- PREVISÕES DOS MODELOS (predict_proba pega a chance de vitória) ---
        prob_rf = model_rf.predict_proba(features_combate)[0][1] # Random Forest
        prob_lr = model_lr.predict_proba(features_combate)[0][1] # Regressão Logística
        
        # Para a Rede Neural, escalamos os dados antes.
        features_scaled = scaler.transform(features_combate)
        prob_nn = model_nn.predict_proba(features_scaled)[0][1]  # Rede Neural

        lista_predicoes.append({
            "opponent": {
                "name": oponente['Pokemon'].lower(), # React costuma usar minúsculo
                "types": [oponente['Type1'], oponente['Type2']] if pd.notna(oponente['Type2']) else [oponente['Type1']]
            },
            "winRate": int(prob_rf * 100), # Manda em formato de porcentagem inteira para o slider
            "chanceLR": int(prob_lr * 100),
            "chanceNN": int(prob_nn * 100),
            "xpReward": int(oponente['Base Exp'])
        })

    # 3. Filtra com base no slider dinâmico do front-end
    df_resultados = pd.DataFrame(lista_predicoes)
    # Filtra usando o valor dinâmico que veio do 'minWinRate' do React!
    df_filtrado = df_resultados[df_resultados['winRate'] >= (min_win_rate * 100)]
    df_ranking = df_filtrado.sort_values(by='xpReward', ascending=False).head(limit)

    # 4. Devolve a resposta estruturada em JSON para o React ler no MatchupList
    resposta = {
        "pokemon": {"name": nome_pokemon},
        "likelyWins": df_ranking.to_dict(orient='records')
    }
        
    return jsonify(resposta)

if __name__ == '__main__':
    app.run(debug=True)