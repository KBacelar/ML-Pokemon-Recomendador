import { useEffect, useState } from 'react';
import PokemonCard from '../components/PokemonCard';
import { getPokemonList } from '../services/pokemonService';
import './Pokedex.css';

const PAGE_SIZE = 24;

export default function Pokedex() {
  const [pokemons, setPokemons] = useState([]);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    getPokemonList(PAGE_SIZE, page * PAGE_SIZE)
      .then((res) => !cancelled && setPokemons(res.results))
      .catch((err) => !cancelled && setError(err.message))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [page]);

  return (
    <div className="pokedex">
      <header className="pokedex__header">
        <h1>Pokédex</h1>
        <p>Explore os Pokémon disponíveis para a batalha.</p>
      </header>

      {error && <div className="pokedex__error">{error}</div>}

      <div className="pokedex__grid">
        {loading && <div className="pokedex__loading">Carregando...</div>}
        {!loading &&
          pokemons.map((p) => <PokemonCard key={p.id} pokemon={p} onClick={() => {}} />)}
      </div>

      <div className="pokedex__pagination">
        <button onClick={() => setPage((p) => Math.max(0, p - 1))} disabled={page === 0 || loading}>
          ← Anterior
        </button>
        <span>Página {page + 1}</span>
        <button onClick={() => setPage((p) => p + 1)} disabled={loading}>
          Próxima →
        </button>
      </div>
    </div>
  );
}
