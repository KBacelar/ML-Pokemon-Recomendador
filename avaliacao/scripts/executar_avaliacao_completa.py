# Executa todos os scripts da avaliação em sequência

import subprocess
import sys
import os

def executar(script):
    print(f"\n--- Executando {script} ---")
    resultado = subprocess.run([sys.executable, script])
    if resultado.returncode != 0:
        print(f"Erro ao executar {script}")
        sys.exit(resultado.returncode)

# Verifica se os modelos treinados existem antes de começar
modelos = [
    '../../modelos_treinados/model_rf.pkl',
    '../../modelos_treinados/model_lr.pkl',
    '../../modelos_treinados/model_nn.pkl',
    '../../modelos_treinados/scaler.pkl',
    '../../modelos_treinados/colunas_X.pkl'
]
faltando = [m for m in modelos if not os.path.exists(m)]
if faltando:
    print("Modelos treinados não encontrados. Execute pipeline_ml.py antes.")
    for m in faltando:
        print(f"  - {m}")
    sys.exit(1)

executar('avaliacao_modelos.py')
executar('teste_pokemon_novo.py')
executar('teste_pokemons_realistas.py')
executar('gerar_relatorio.py')

print("\nAvaliação concluída. Resultados em avaliacao/resultados/")
