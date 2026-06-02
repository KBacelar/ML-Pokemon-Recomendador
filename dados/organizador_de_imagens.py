import os
import shutil

# Caminhos exatos do seu computador
pasta_origem = r'C:\Users\caiio\OneDrive\Área de Trabalho\IML\ML-Pokemon-Recomendador\dados\Pokemon Images DB\Pokemon Images DB'
pasta_destino = r'C:\Users\caiio\OneDrive\Área de Trabalho\IML\ML-Pokemon-Recomendador\dados\Pokemon Images DB'

# Garante que a pasta de destino existe (no seu caso, já existe)
os.makedirs(pasta_destino, exist_ok=True)

contagem = 0
print("Iniciando a extração e limpeza dos nomes das imagens...")

# O os.walk vai varrer todas as mais de 1000 subpastas
for raiz, diretorios, arquivos in os.walk(pasta_origem):
    for arquivo in arquivos:
        # Verifica se é um arquivo de imagem
        if arquivo.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
            caminho_antigo = os.path.join(raiz, arquivo)
            
            # Pega o nome da pasta (ex: 'Abra', 'Alakazam')
            nome_pasta = os.path.basename(raiz)
            
            # Pega apenas a extensão original do arquivo (ex: '.png')
            extensao = os.path.splitext(arquivo)[1]
            
            # Monta o nome novo perfeito baseado na pasta, ignorando o "_new"
            novo_nome_arquivo = f"{nome_pasta}{extensao}"
            
            caminho_novo = os.path.join(pasta_destino, novo_nome_arquivo)
            
            # Move e renomeia o arquivo
            shutil.move(caminho_antigo, caminho_novo)
            contagem += 1

print(f"Sucesso! {contagem} imagens foram movidas e renomeadas perfeitamente.")