# Pokédex Battle

Front-end em React (Create React App) de uma Pokédex com **análise de matchups** em formato de campo de batalha.

A listagem e os dados base dos Pokémon vêm da [PokéAPI](https://pokeapi.co/).
A análise de força (funcionalidade principal) está preparada para consumir um **backend próprio em desenvolvimento**, cujo algoritmo compara um Pokémon escolhido contra todos os outros e devolve a lista daqueles que ele tem **maior chance de vencer**. Enquanto o backend não está pronto, um **mock** local com a mesma assinatura de resposta é usado.

## Stack

- React 18 + Create React App (`react-scripts` 5)
- React Router DOM 6 (navegação)
- Axios (chamadas HTTP)
- CSS puro com tema "campo de batalha"

## Funcionalidades

- **Campo de Batalha** (rota `/`): escolha um Pokémon, defina o limite mínimo de chance de vitória e o sistema lista os adversários que ele tem maior probabilidade de vencer, ordenados pela maior chance.
- **Pokédex** (rota `/pokedex`): lista paginada de Pokémon.
- **Picker com busca**: é possível buscar qualquer Pokémon por nome diretamente na PokéAPI.

## Como rodar o projeto completo (back + front)

O projeto tem duas partes que rodam ao mesmo tempo, cada uma no seu próprio terminal:

- **Back-end** (Flask + modelos de ML) — pasta raiz `iml-front/`
- **Front-end** (React) — pasta `iml-front/pokedex-front/`

### Pré-requisitos

- **Python 3** 
- **Node.js** (verifique com `node -v`)

### Terminal 1 — Back-end (Flask + ML)

```bash
cd ~/Desktop/iml-front
source venv/bin/activate
python app.py
```

Você deve ver:

```
--- Carregando modelos treinados em memória ---
Modelos prontos para receber requisições do React!
 * Running on http://127.0.0.1:5000
```

> **Primeira vez numa máquina nova** (ou se o `venv/` não existir): rode antes
>
> ```bash
> python3 -m venv venv
> source venv/bin/activate
> pip install -r requirements.txt
> python pipeline_ml.py    # treina e salva os modelos em modelos_treinados/
> ```

### Terminal 2 — Front-end (React)

Abra um **segundo terminal** (não feche o primeiro):

```bash
cd ~/Desktop/iml-front/pokedex-front
npm install        # só na primeira vez (ou se package.json mudar)
npm start
```

A aplicação sobe em `http://localhost:3000` e abre automaticamente no navegador.

### Para parar tudo

Em cada terminal, aperte **`Ctrl + C`**. Para sair do ambiente virtual no Terminal 1: `deactivate`.

### Build de produção (front)

```bash
npm run build
```

Os arquivos finais ficam em `build/`.

### Troubleshooting

| Problema | Solução |
| --- | --- |
| `ModuleNotFoundError: No module named 'pandas'` | Esqueceu de `source venv/bin/activate` antes do `python app.py` |
| `Port 5000 already in use` | `lsof -ti :5000 \| xargs kill` |
| `Port 3000 already in use` | `lsof -ti :3000 \| xargs kill` |
| `AttributeError: 'LogisticRegression' object has no attribute 'multi_class'` | Modelos `.pkl` estão em versão incompatível. Rode `python pipeline_ml.py` para retreinar |
| CORS error no navegador | Quase sempre é um 500 disfarçado. Olhe o **Terminal 1** para ver o erro real do Flask |
| Mudou algum `.pkl` mas o erro persiste | Pare o Flask (Ctrl+C) e suba de novo — ele não recarrega automaticamente os modelos |

## Variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e ajuste se necessário:

```bash
cp .env.example .env
```

| Variável                  | Padrão                       | Descrição                                                           |
| ------------------------- | ---------------------------- | ------------------------------------------------------------------- |
| `REACT_APP_BACKEND_URL`   | `http://127.0.0.1:5000`      | URL base do backend Flask que faz a análise de matchups.            |
| `REACT_APP_USE_MOCK`      | `true`                       | Se `true`, usa o mock local. Defina como `false` para usar o backend. |

> Variáveis precisam começar com `REACT_APP_` para serem expostas no bundle do CRA. Após alterar o `.env`, reinicie o `npm start`.

Quando `REACT_APP_USE_MOCK=false` e o backend estiver indisponível, o app cai automaticamente no mock (com aviso no console).

## Contrato esperado do backend

`POST {REACT_APP_BACKEND_URL}/battle/matchups`

Request body:

```json
{
  "pokemon": { "id": 6, "name": "charizard" },
  "minWinRate": 50,
  "limit": 20
}
```

Response body esperado:

```json
{
  "pokemon": { "id": 6, "name": "charizard" },
  "power": 540,
  "totalEvaluated": 1024,
  "likelyWins": [
    {
      "opponent": {
        "id": 10,
        "name": "caterpie",
        "image": "https://...",
        "types": ["bug"],
        "stats": { "hp": 45, "attack": 30, "defense": 35, "special-attack": 20, "special-defense": 20, "speed": 45 }
      },
      "winRate": 96,
      "myPower": 540,
      "opponentPower": 95
    }
  ]
}
```

### Notas sobre os campos

- `likelyWins` deve vir **ordenado por `winRate` decrescente**.
- `winRate` é um inteiro de `0` a `100` representando a probabilidade percentual de vitória.
- O campo `opponent` deve trazer pelo menos `id`, `name`, `image` e `types` para que o front consiga renderizar o card. Se o backend não puder enriquecer com `image`/`types`/`stats`, o front pode hidratar via PokéAPI (suporte fácil de adicionar em `services/pokemonService.js`).
- `totalEvaluated` é usado apenas para o texto informativo ("N de X avaliados").

## Estrutura

```
public/
├── index.html                # template HTML do CRA
├── manifest.json
└── favicon.svg
src/
├── components/
│   ├── BattleSlot.jsx        # slot do desafiante no campo de batalha
│   ├── MatchupList.jsx       # lista de adversários que o desafiante vence
│   ├── PokemonCard.jsx       # card individual (usado na pokédex e no picker)
│   └── PokemonPicker.jsx     # modal para escolher pokémon
├── pages/
│   ├── BattleField.jsx       # página principal (análise de matchups)
│   └── Pokedex.jsx           # listagem geral
├── services/
│   ├── api.js                # instâncias axios (pokeapi e backend)
│   ├── pokemonService.js     # dados de pokémon (PokéAPI)
│   └── battleService.js      # matchups (backend + mock)
├── App.jsx                   # layout + rotas
└── index.js                  # bootstrap (createRoot)
```

