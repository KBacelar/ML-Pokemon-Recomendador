import { pokeApi } from './api';

const TYPE_COLORS = {
  normal: '#A8A77A',
  fire: '#EE8130',
  water: '#6390F0',
  electric: '#F7D02C',
  grass: '#7AC74C',
  ice: '#96D9D6',
  fighting: '#C22E28',
  poison: '#A33EA1',
  ground: '#E2BF65',
  flying: '#A98FF3',
  psychic: '#F95587',
  bug: '#A6B91A',
  rock: '#B6A136',
  ghost: '#735797',
  dragon: '#6F35FC',
  dark: '#705746',
  steel: '#B7B7CE',
  fairy: '#D685AD',
};

export const getTypeColor = (type) => TYPE_COLORS[type.toLowerCase()] || '#777';

const mapPokemon = (data) => ({
  id: data.id,
  name: data.name,
  image:
    data.sprites?.other?.['official-artwork']?.front_default ||
    data.sprites?.front_default,
  sprite: data.sprites?.front_default,
  types: data.types.map((t) => t.type.name),
  stats: data.stats.reduce((acc, s) => {
    acc[s.stat.name] = s.base_stat;
    return acc;
  }, {}),
  height: data.height,
  weight: data.weight,
});

export async function getPokemonList(limit = 24, offset = 0) {
  const { data } = await pokeApi.get(`/pokemon?limit=${limit}&offset=${offset}`);
  const details = await Promise.all(
    data.results.map((p) => pokeApi.get(`/pokemon/${p.name}`).then((r) => mapPokemon(r.data)))
  );
  return { results: details, total: data.count };
}

export async function getPokemonByName(name) {
  const { data } = await pokeApi.get(`/pokemon/${name.toLowerCase()}`);
  return mapPokemon(data);
}
