import { useEffect, useState } from "react";
import PokemonCard from "./PokemonCard";
import { getPokemonList, getPokemonByName } from "../services/pokemonService";
import "./PokemonPicker.css";

const PAGE_SIZE = 24;

export default function PokemonPicker({ open, onClose, onSelect, title }) {
  const [pokemons, setPokemons] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (!open) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    const term = search.trim().toLowerCase();

    if (term) {
      getPokemonByName(term)
        .then((p) => {
          if (!cancelled) {
            setPokemons([p]);
          }
        })
        .catch(() => {
          if (!cancelled) {
            setPokemons([]);
            setError(`Pokémon "${search}" não encontrado na base de dados.`);
          }
        })
        .finally(() => !cancelled && setLoading(false));
    } else {
      getPokemonList(PAGE_SIZE, page * PAGE_SIZE)
        .then((res) => {
          if (!cancelled) setPokemons(res.results);
        })
        .catch((err) => !cancelled && setError(err.message))
        .finally(() => !cancelled && setLoading(false));
    }

    return () => {
      cancelled = true;
    };
  }, [open, page, search]); // O efeito agora reage dinamicamente ao 'search'!

  if (!open) return null;

  return (
    <div className="picker-backdrop" onClick={onClose}>
      <div className="picker" onClick={(e) => e.stopPropagation()}>
        <div className="picker__header">
          <h2>{title || "Escolher Pokémon"}</h2>
          <button
            className="picker__close"
            onClick={onClose}
            aria-label="fechar"
          >
            ×
          </button>
        </div>

        <div className="picker__search">
          <input
            type="text"
            placeholder="Buscar globalmente por nome (ex: pikachu, charizard)..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(0); // Reseta para a página inicial caso o usuário limpe a busca
            }}
          />
        </div>

        {error && <div className="picker__error">{error}</div>}

        <div className="picker__grid">
          {loading && (
            <div className="picker__loading">Buscando na Pokédex...</div>
          )}

          {!loading &&
            pokemons.map((p) => (
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

          {!loading && pokemons.length === 0 && !error && (
            <div className="picker__loading">Nenhum pokémon encontrado.</div>
          )}
        </div>

        {!search.trim() && (
          <div className="picker__pagination">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0 || loading}
            >
              ← Anterior
            </button>
            <span>Página {page + 1}</span>
            <button onClick={() => setPage((p) => p + 1)} disabled={loading}>
              Próxima →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
