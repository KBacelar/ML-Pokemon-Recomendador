import { backendApi } from './api';
import { getPokemonList } from './pokemonService';

const USE_MOCK = process.env.REACT_APP_USE_MOCK !== 'false';

const MOCK_POOL_SIZE = 60;

function calculatePower(pokemon) {
  const s = pokemon.stats || {};
  const hp = s.hp || 0;
  const atk = s.attack || 0;
  const def = s.defense || 0;
  const spa = s['special-attack'] || 0;
  const spd = s['special-defense'] || 0;
  const spe = s.speed || 0;
  return Math.round(hp * 0.8 + atk * 1.2 + def * 1.0 + spa * 1.2 + spd * 1.0 + spe * 0.9);
}

function winProbability(myPower, opponentPower) {
  if (myPower + opponentPower === 0) return 50;
  const raw = myPower / (myPower + opponentPower);
  const sharpened = 1 / (1 + Math.exp(-8 * (raw - 0.5)));
  return Math.round(sharpened * 100);
}

async function mockMatchups(pokemon, { minWinRate = 50, limit = 20 } = {}) {
  const { results: pool } = await getPokemonList(MOCK_POOL_SIZE, 0);
  const myPower = calculatePower(pokemon);

  const matchups = pool
    .filter((p) => p.id !== pokemon.id)
    .map((opponent) => {
      const opponentPower = calculatePower(opponent);
      const winRate = winProbability(myPower, opponentPower);
      return {
        opponent,
        winRate,
        myPower,
        opponentPower,
      };
    })
    .filter((m) => m.winRate >= minWinRate)
    .sort((a, b) => b.winRate - a.winRate)
    .slice(0, limit);

  return {
    pokemon: { id: pokemon.id, name: pokemon.name },
    power: myPower,
    totalEvaluated: pool.length - 1,
    likelyWins: matchups,
    source: 'mock',
  };
}

export async function fetchMatchups(pokemon, options = {}) {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 400));
    return mockMatchups(pokemon, options);
  }

  try {
    const { data } = await backendApi.post('/battle/matchups', {
      pokemon: { id: pokemon.id, name: pokemon.name },
      minWinRate: options.minWinRate ?? 50,
      limit: options.limit ?? 20,
    });
    return { ...data, source: 'backend' };
  } catch (err) {
    console.warn('[battleService] backend indisponível, usando mock:', err.message);
    return mockMatchups(pokemon, options);
  }
}
