# Carregar csv bruto e limpar as strings
import pandas as pd

def limpar_dados_pokemon(caminho_csv='dados/pokemonDB_dataset.csv'):
    df = pd.read_csv(caminho_csv)

    # Limpar Base Exp e Catch Rate
    df['Base Exp'] = df['Base Exp'].astype(str).str.extract(r'(\d+)').astype(float)
    df['Base Exp'] = df['Base Exp'].fillna(df['Base Exp'].mean()).astype(int)

    df['Catch Rate'] = df['Catch Rate'].astype(str).str.extract(r'(\d+)').astype(float)
    df['Catch Rate'] = df['Catch Rate'].fillna(df['Catch Rate'].mean()).astype(int)

    # Tratar tipos textuais
    df['Type'] = df['Type'].fillna('Normal')
    types_split = df['Type'].str.split(', ', expand=True)
    df['Type1'] = types_split[0]
    df['Type2'] = types_split[1].fillna(types_split[0])
    
    return df

if __name__ == "__main__":
    df_limpo = limpar_dados_pokemon()
    print("Sucesso! O dataset possui", df_limpo.shape[0], "pokémons limpos.")