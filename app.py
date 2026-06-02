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

    # if nome_pokemon not in df_pk['Pokemon'].values:
    #     return jsonify({"error": "Pokémon não encontrado"}), 404
    
    meu_pk = df_pk[df_pk['Pokemon'] == nome_pokemon].iloc[0]

    lista_predicoes = []
    
    # Comparar contra todos os outros Pokémons do jogo
    for _, oponente in df_pk.iterrows():
        if oponente['Pokemon'] == meu_pk['Pokemon']:
            continue
            
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
            'opponent': {
                'name': oponente['Pokemon'],
                'types': oponente['Type'].split(',')
            },
            
            'Chance_RF': round(prob_rf * 100, 1),
            'Chance_LR': round(prob_lr * 100, 1),
            'Chance_NN': round(prob_nn * 100, 1),
            'XP_Recompensa': oponente['Base Exp']
        })
        
    df_resultados = pd.DataFrame(lista_predicoes)

    df_seguro = df_resultados[df_resultados['Chance_RF'] >= 0.85]

    
    df_ranking = df_seguro.sort_values(by='Chance_RF', ascending=False).head(limit)

    print(df_ranking)

    lista_final = df_ranking[['opponent', 'Chance_RF', 'Chance_LR', 'Chance_NN', 'XP_Recompensa']].to_dict(orient='records')

    resposta = {
        "pokemon": {
            "name": nome_pokemon
        },
        # "totalEvaluated": total_avaliados,  
        "likelyWins": lista_final
    }
    
    print(resposta)
    return jsonify(resposta)

if __name__ == '__main__':
    app.run(debug=True)

    