# Consolida os resultados dos scripts anteriores e gera um relatório HTML
# com tabelas, gráficos embutidos em base64 e análise das métricas

import pandas as pd
import base64
from datetime import datetime
import os

os.makedirs('../resultados', exist_ok=True)

# Conferir se os arquivos pré-requisitos foram gerados
arquivos_necessarios = [
    '../resultados/resultados_avaliacao.csv',
    '../resultados/matrizes_confusao.png',
    '../resultados/comparacao_modelos.png',
    '../resultados/teste_pokemons_novos.csv',
    '../resultados/teste_pokemons_confianca.png'
]

faltando = [a for a in arquivos_necessarios if not os.path.exists(a)]
if faltando:
    print("Arquivos faltando. Execute os scripts anteriores antes:")
    for a in faltando:
        print(f"  - {a}")
    exit(1)

df_avaliacao = pd.read_csv('../resultados/resultados_avaliacao.csv')
df_testes_novos = pd.read_csv('../resultados/teste_pokemons_novos.csv')

# Codificar imagens em base64 para embutir no HTML
def image_to_base64(image_path):
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

img_matrizes = image_to_base64('../resultados/matrizes_confusao.png')
img_comparacao = image_to_base64('../resultados/comparacao_modelos.png')
img_confianca = image_to_base64('../resultados/teste_pokemons_confianca.png')

# Score geral por modelo = média das duas métricas
scores_gerais = {}
for modelo in df_avaliacao['Modelo'].unique():
    df_modelo = df_avaliacao[df_avaliacao['Modelo'] == modelo]
    scores_gerais[modelo] = df_modelo['Média'].mean()

melhor_modelo_geral = max(scores_gerais, key=scores_gerais.get)

melhor_precision = df_avaliacao[df_avaliacao['Métrica'] == 'Precision'].nlargest(1, 'Média').iloc[0]
melhor_recall = df_avaliacao[df_avaliacao['Métrica'] == 'Recall'].nlargest(1, 'Média').iloc[0]

# Função auxiliar para buscar métrica específica de um modelo
def metrica(modelo, nome):
    return df_avaliacao[(df_avaliacao['Modelo'] == modelo) & (df_avaliacao['Métrica'] == nome)]['Média'].values[0]

# Montar linhas da tabela principal, destacando o melhor modelo geral
tabela_html = ""
for modelo in df_avaliacao['Modelo'].unique():
    df_modelo = df_avaliacao[df_avaliacao['Modelo'] == modelo]
    row_class = 'best-model' if modelo == melhor_modelo_geral else ''
    for _, row in df_modelo.iterrows():
        tabela_html += f"""
        <tr class="{row_class}">
            <td>{row['Modelo']}</td>
            <td>{row['Métrica']}</td>
            <td>{row['Média']:.4f}</td>
            <td>±{row['Desvio Padrão']:.4f}</td>
        </tr>"""

# Linhas da tabela de testes sintéticos
tabela_testes = ""
for _, row in df_testes_novos.iterrows():
    tabela_testes += f"""
            <tr>
                <td><strong>{row['Pokémon']}</strong></td>
                <td>{row['RF_Vitoria']} ({row['RF_Confianca']})</td>
                <td>{row['LR_Vitoria']} ({row['LR_Confianca']})</td>
                <td>{row['NN_Vitoria']} ({row['NN_Confianca']})</td>
            </tr>"""

# Template HTML com estilo alinhado ao front-end React (cores e fontes)
html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório de Avaliação - ML Pokémon</title>
    <style>
        *, *::before, *::after {{ box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
            margin: 0; padding: 0;
            background:
                radial-gradient(ellipse at top, #1e1b4b 0%, transparent 60%),
                radial-gradient(ellipse at bottom, #1a0b2e 0%, transparent 60%),
                #0a0a1a;
            color: #fff;
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 24px 16px 64px; }}
        .header {{
            background: linear-gradient(180deg, #1a1a2e, #0f0f1c);
            border-bottom: 3px solid #c00;
            padding: 40px 24px;
            text-align: center;
            margin-bottom: 40px;
            border-radius: 10px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2.2em;
            font-weight: 800;
            letter-spacing: 2px;
            text-transform: uppercase;
            background: linear-gradient(135deg, #c00, #ff4444);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .header p {{ margin: 5px 0; opacity: 0.8; }}
        .header .date {{ font-size: 0.9em; opacity: 0.6; margin-top: 15px; }}
        .section {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
        }}
        .section h2 {{
            color: #ff4444;
            margin: 0 0 20px 0;
            font-size: 1.6em;
            border-bottom: 2px solid #c00;
            padding-bottom: 10px;
        }}
        .section h3 {{ color: #ff6666; margin: 25px 0 15px 0; font-size: 1.2em; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            overflow: hidden;
        }}
        thead {{ background: linear-gradient(135deg, #c00, #800); }}
        th {{ padding: 12px; text-align: left; font-size: 0.9em; text-transform: uppercase; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }}
        tr:hover {{ background: rgba(255, 255, 255, 0.05); }}
        .best-model {{ background: rgba(0, 255, 100, 0.1) !important; border-left: 4px solid #0f0; }}
        .metric-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px; margin: 25px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            padding: 22px;
            border-radius: 10px;
            text-align: center;
        }}
        .metric-card h4 {{ margin: 0 0 10px 0; font-size: 0.9em; opacity: 0.9; text-transform: uppercase; }}
        .metric-card .model-name {{ font-size: 1.5em; font-weight: 800; margin: 8px 0; }}
        .image-container {{
            margin: 25px 0;
            text-align: center;
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            border-radius: 10px;
        }}
        .image-container img {{ max-width: 100%; height: auto; border-radius: 8px; }}
        .methodology {{
            background: rgba(255, 255, 255, 0.06);
            border-left: 4px solid #ff4444;
            padding: 18px;
            margin: 15px 0;
            border-radius: 5px;
        }}
        .methodology h4 {{ margin: 0 0 10px 0; color: #ff6666; }}
        .conclusion {{
            background: linear-gradient(135deg, rgba(0, 200, 0, 0.15), rgba(0, 150, 0, 0.15));
            border: 2px solid #0f0;
            padding: 22px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .conclusion h4 {{ margin: 0 0 12px 0; color: #0f0; }}
        .footer {{
            text-align: center;
            padding: 30px 20px;
            opacity: 0.6;
            font-size: 0.9em;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            margin-top: 50px;
        }}
        ::-webkit-scrollbar {{ width: 10px; }}
        ::-webkit-scrollbar-track {{ background: rgba(0, 0, 0, 0.3); }}
        ::-webkit-scrollbar-thumb {{ background: #c00; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Relatório de Avaliação de Modelos</h1>
            <p>Sistema de Predição de Batalhas Pokémon</p>
            <p class="date">Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
        </div>

        <div class="section">
            <h2>1. Resumo Executivo</h2>
            <div class="methodology">
                <h4>Metodologia</h4>
                <ul>
                    <li>Validação cruzada Stratified K-Fold (k=5)</li>
                    <li>Métricas: Precision e Recall</li>
                    <li>Modelos avaliados: Random Forest, Regressão Logística e Rede Neural (MLP)</li>
                    <li>Teste adicional com 5 Pokémons sintéticos para análise de robustez</li>
                </ul>
            </div>

            <h3>Melhores modelos por métrica</h3>
            <div class="metric-cards">
                <div class="metric-card">
                    <h4>Precision</h4>
                    <div class="model-name">{melhor_precision['Modelo']}</div>
                    <div>{melhor_precision['Média']:.4f} ± {melhor_precision['Desvio Padrão']:.4f}</div>
                </div>
                <div class="metric-card">
                    <h4>Recall</h4>
                    <div class="model-name">{melhor_recall['Modelo']}</div>
                    <div>{melhor_recall['Média']:.4f} ± {melhor_recall['Desvio Padrão']:.4f}</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>2. Resultados da Validação Cruzada</h2>
            <p>Média e desvio padrão obtidos em 5 folds (Stratified K-Fold):</p>
            <table>
                <thead>
                    <tr><th>Modelo</th><th>Métrica</th><th>Média</th><th>Desvio Padrão</th></tr>
                </thead>
                <tbody>{tabela_html}
                </tbody>
            </table>
            <p><em>Linha destacada indica o modelo com maior média entre as três métricas.</em></p>

            <h3>Gráfico Comparativo</h3>
            <div class="image-container">
                <img src="data:image/png;base64,{img_comparacao}" alt="Comparação de Modelos">
            </div>
        </div>

        <div class="section">
            <h2>3. Matrizes de Confusão</h2>
            <div class="image-container">
                <img src="data:image/png;base64,{img_matrizes}" alt="Matrizes de Confusão">
            </div>
            <div class="methodology">
                <h4>Interpretação</h4>
                <ul>
                    <li>Diagonal principal: predições corretas</li>
                    <li>Fora da diagonal: erros de classificação</li>
                    <li>Cores mais escuras indicam maior número de ocorrências</li>
                </ul>
            </div>
        </div>

        <div class="section">
            <h2>4. Testes com Pokémons Sintéticos</h2>
            <p>Cinco perfis sintéticos foram submetidos aos três modelos para avaliar o comportamento em cenários extremos:</p>
            <div class="image-container">
                <img src="data:image/png;base64,{img_confianca}" alt="Confiança em Pokémons Sintéticos">
            </div>

            <h3>Detalhamento das predições</h3>
            <table>
                <thead>
                    <tr><th>Pokémon</th><th>Random Forest</th><th>Regressão Logística</th><th>Rede Neural</th></tr>
                </thead>
                <tbody>{tabela_testes}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>5. Análise dos Resultados</h2>

            <h3>5.1. Comparação entre os modelos</h3>
            <ul>
                <li><strong>Rede Neural (MLP)</strong> obteve o melhor desempenho geral: Precision {metrica('Rede Neural', 'Precision'):.4f} e Recall {metrica('Rede Neural', 'Recall'):.4f}. Apresentou também o menor desvio padrão, indicando estabilidade entre os folds.</li>
                <li><strong>Regressão Logística</strong> ficou em segundo lugar (Precision {metrica('Regressão Logística', 'Precision'):.4f}, Recall {metrica('Regressão Logística', 'Recall'):.4f}). O bom desempenho de um modelo linear indica forte componente linear na relação entre features e resultado.</li>
                <li><strong>Random Forest</strong> obteve resultados ligeiramente inferiores (Precision {metrica('Random Forest', 'Precision'):.4f}, Recall {metrica('Random Forest', 'Recall'):.4f}), embora ofereça maior interpretabilidade por permitir a análise de importância de features.</li>
            </ul>

            <h3>5.2. Sobre a metodologia (Stratified K-Fold)</h3>
            <p>O dataset foi dividido em 5 partições estratificadas, preservando a proporção entre vitórias e derrotas. Cada modelo foi treinado e testado 5 vezes, alternando os folds de teste. As métricas reportadas correspondem à média e ao desvio padrão dessas 5 execuções, reduzindo o viés de uma única divisão treino/teste.</p>
            <p>Todos os modelos apresentaram desvio padrão inferior a 0,01, o que indica resultados estáveis em diferentes partições dos dados.</p>

            <h3>5.3. Robustez em dados sintéticos</h3>
            <ul>
                <li>Os três modelos concordaram em 100% das predições nos cinco perfis testados.</li>
                <li>A confiança das predições é coerente com os perfis dos Pokémons (alta para perfis fortes, baixa para o perfil fraco).</li>
                <li>A Rede Neural apresentou confiança próxima de 100% nos perfis vencedores, enquanto o Random Forest mostrou-se mais conservador.</li>
            </ul>

            <div class="conclusion">
                <h4>Conclusão</h4>
                <p>O modelo recomendado para o sistema é a <strong>{melhor_modelo_geral}</strong>, por apresentar o melhor equilíbrio entre Precision ({melhor_precision['Média']:.4f}) e Recall ({melhor_recall['Média']:.4f}), além do menor desvio padrão observado na validação cruzada.</p>
            </div>
        </div>

        <div class="footer">
            <p>Trabalho de Introdução a Machine Learning</p>
            <p>Relatório gerado por avaliacao/scripts/gerar_relatorio.py</p>
        </div>
    </div>
</body>
</html>"""

with open('../resultados/relatorio_completo.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

# Resumo em texto puro para referência rápida
resumo_txt = f"""RELATÓRIO DE AVALIAÇÃO - ML POKÉMON
Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}

METODOLOGIA
-----------
- Validação Cruzada: Stratified K-Fold (k=5)
- Métricas: Precision, Recall
- Modelos: Random Forest, Regressão Logística, Rede Neural
- Testes adicionais: 5 Pokémons sintéticos

MELHORES MODELOS POR MÉTRICA
----------------------------
Precision: {melhor_precision['Modelo']} ({melhor_precision['Média']:.4f} ± {melhor_precision['Desvio Padrão']:.4f})
Recall:    {melhor_recall['Modelo']} ({melhor_recall['Média']:.4f} ± {melhor_recall['Desvio Padrão']:.4f})

MELHOR MODELO GERAL
-------------------
{melhor_modelo_geral}

ARQUIVOS GERADOS
----------------
- relatorio_completo.html
- resumo_avaliacao.txt
- resultados_avaliacao.csv
- teste_pokemons_novos.csv
- matrizes_confusao.png
- comparacao_modelos.png
- teste_pokemons_confianca.png
"""

with open('../resultados/resumo_avaliacao.txt', 'w', encoding='utf-8') as f:
    f.write(resumo_txt)

print("Arquivos gerados em avaliacao/resultados/:")
print("  - relatorio_completo.html")
print("  - resumo_avaliacao.txt")
