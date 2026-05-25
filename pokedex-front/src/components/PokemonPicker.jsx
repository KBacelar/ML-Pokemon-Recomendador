import { useEffect, useMemo, useState } from 'react';
import PokemonCard from './PokemonCard';
import { getPokemonList, getPokemonByName } from '../services/pokemonService';
import './PokemonPicker.css';

const PAGE_SIZE = 24;

export default function PokemonPicker({ open, onClose, onSelect, title }) {
  const [pokemons, setPokemons] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState('');
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    getPokemonList(PAGE_SIZE, page * PAGE_SIZE)
      .then((res) => {
        if (!cancelled) setPokemons(res.results);
      })
      .catch((err) => !cancelled && setError(err.message))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [open, page]);

  const filtered = useMemo(() => {
    if (!search.trim()) return pokemons;
    const term = search.trim().toLowerCase();
    return pokemons.filter((p) => p.name.includes(term));
  }, [pokemons, search]);

  async function handleDirectSearch(e) {
    e.preventDefault();
    if (!search.trim()) return;
    setSearching(true);
    setError(null);
    try {
      const p = await getPokemonByName(search.trim());
      onSelect(p);
      onClose();
    } catch {
      setError(`Pokémon "${search}" não encontrado.`);
    } finally {
      setSearching(false);
    }
  }

  if (!open) return null;

  return (
    <div className="picker-backdrop" onClick={onClose}>
      <div className="picker" onClick={(e) => e.stopPropagation()}>
        <div className="picker__header">
          <h2>{title || 'Escolher Pokémon'}</h2>
          <button className="picker__close" onClick={onClose} aria-label="fechar">×</button>
        </div>

        <form className="picker__search" onSubmit={handleDirectSearch}>
          <input
            type="text"
            placeholder="Buscar por nome (ex: pikachu, charizard)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button type="submit" disabled={searching || !search.trim()}>
            {searching ? '...' : 'Buscar'}
          </button>
        </form>

        {error && <div className="picker__error">{error}</div>}

        <div className="picker__grid">
          {loading && <div className="picker__loading">Carregando pokédex...</div>}
          {!loading &&
            filtered.map((p) => (
              <PokemonCard
                key={p.id}
                pokemon={p}
                compact
                onClick={() => {
                  onSelect(p);
                  onClose();
                }}
              />
            ))}
          {!loading && filtered.length === 0 && (
            <div className="picker__loading">Nenhum pokémon nesta página.</div>
          )}
        </div>

        <div className="picker__pagination">
          <button onClick={() => setPage((p) => Math.max(0, p - 1))} disabled={page === 0 || loading}>
            ← Anterior
          </button>
          <span>Página {page + 1}</span>
          <button onClick={() => setPage((p) => p + 1)} disabled={loading}>
            Próxima →
          </button>
        </div>
      </div>
    </div>
  );
}
