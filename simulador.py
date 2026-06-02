import random
import pandas as pd
from tqdm import tqdm 
from dados_processados import limpar_dados_pokemon  
from utils import get_effectiveness

def simular_batalha(p1, p2):
    # Usando estritamente os status Max
    hp_p1 = p1['HP Max']
    hp_p2 = p2['HP Max']
    
    # Determinar quem ataca primeiro pela Velocidade Máxima
    if p1['Speed Max'] >= p2['Speed Max']:
        primeiro, segundo = p1, p2
        hp1, hp2 = hp_p1, hp_p2
    else:
        primeiro, segundo = p2, p1
        hp1, hp2 = hp_p2, hp_p1

    for _ in range(20):
        # Turno do primeiro
        eff = max(get_effectiveness(primeiro['Type1'], segundo['Type1'], segundo['Type2']),
                  get_effectiveness(primeiro['Type2'], segundo['Type1'], segundo['Type2']))
        
        # Fórmula de Dano usando os status Max
        dano = (((2 * 100 / 5 + 2) * 60 * (primeiro['Attack Max'] / segundo['Defense Max'])) / 50 + 2) * eff
        hp2 -= max(1, dano)
        if hp2 <= 0:
            return 1 if primeiro['Pokemon'] == p1['Pokemon'] else 0
            
        # Turno do segundo
        eff = max(get_effectiveness(segundo['Type1'], primeiro['Type1'], primeiro['Type2']),
                  get_effectiveness(segundo['Type2'], primeiro['Type1'], primeiro['Type2']))
        
        dano = (((2 * 100 / 5 + 2) * 60 * (segundo['Attack Max'] / primeiro['Defense Max'])) / 50 + 2) * eff
        hp1 -= max(1, dano)
        if hp1 <= 0:
            return 1 if segundo['Pokemon'] == p1['Pokemon'] else 0
            
    return 1 if hp1 >= hp2 else 0

def gerar_dataset_batalhas(n_batalhas=10000):
    print("Carregando e limpando dados dos Pokémons...")
    df = limpar_dados_pokemon()
    
    dados_batalhas = []
    batalhas_realizadas = 0

    print(f"Iniciando a simulação de {n_batalhas} batalhas aleatórias (Modo Status Max):")
    
    with tqdm(total=n_batalhas, desc="Progresso da Simulação", unit="luta") as pbar:
        while batalhas_realizadas < n_batalhas:
            pk1 = df.sample(1).iloc[0]
            pk2 = df.sample(1).iloc[0]
            
            if pk1['Pokemon'] == pk2['Pokemon']:
                continue
                
            resultado = simular_batalha(pk1, pk2)
            
            eff_p1_em_p2 = max(get_effectiveness(pk1['Type1'], pk2['Type1'], pk2['Type2']),
                               get_effectiveness(pk1['Type2'], pk2['Type1'], pk2['Type2']))

            eff_p2_em_p1 = max(get_effectiveness(pk2['Type1'], pk1['Type1'], pk1['Type2']),
                               get_effectiveness(pk2['Type2'], pk1['Type1'], pk1['Type2']))
            
            dados_batalhas.append({
                'P1_HP': pk1['HP Max'], 'P1_Atk': pk1['Attack Max'], 'P1_Def': pk1['Defense Max'], 
                'P1_SpAtk': pk1['Special Attack Max'], 'P1_SpDef': pk1['Special Defense Max'], 'P1_Speed': pk1['Speed Max'],
                'P2_HP': pk2['HP Max'], 'P2_Atk': pk2['Attack Max'], 'P2_Def': pk2['Defense Max'], 
                'P2_SpAtk': pk2['Special Attack Max'], 'P2_SpDef': pk2['Special Defense Max'], 'P2_Speed': pk2['Speed Max'],
                'Vantagem_Tipo_P1': eff_p1_em_p2,  
                'Vantagem_Tipo_P2': eff_p2_em_p1,  
                'Vitoria_P1': resultado
            })
            
            batalhas_realizadas += 1
            pbar.update(1)

    print("Salvando arquivo final...")
    dataset_treino = pd.DataFrame(dados_batalhas)
    dataset_treino.to_csv('dados/batalhas_pokemon_treino.csv', index=False)
    print("Dataset gerado com sucesso em 'dados/batalhas_pokemon_treino.csv'!")

if __name__ == "__main__":
    gerar_dataset_batalhas(10000)