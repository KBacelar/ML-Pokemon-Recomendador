import { getTypeColor } from '../services/pokemonService';
import './PokemonCard.css';

export default function PokemonCard({ pokemon, onClick, selected, compact = false }) {
  if (!pokemon) return null;

  const primaryColor = getTypeColor(pokemon.types[0]);

  const getImgSrc = (name) =>
  `${process.env.REACT_APP_BACKEND_URL}/dados/pokemon_img/${name}.png`;

  return (
    <button
      type="button"
      className={`pokemon-card ${selected ? 'pokemon-card--selected' : ''} ${
        compact ? 'pokemon-card--compact' : ''
      }`}
      style={{ '--type-color': primaryColor }}
      onClick={() => onClick?.(pokemon)}
    >
      <div className="pokemon-card__id">#{String(pokemon.id).padStart(3, '0')}</div>
      <div className="pokemon-card__image-wrap">
        <img
          //src={pokemon.image} 
          src={getImgSrc(pokemon.name)}
          alt={pokemon.name}
          className="pokemon-card__image"
          loading="lazy"
        />
      </div>
      <h3 className="pokemon-card__name">{pokemon.name}</h3>
      <div className="pokemon-card__types">
        {pokemon.types.map((t) => (
          <span
            key={t}
            className="pokemon-card__type"
            style={{ background: getTypeColor(t) }}
          >
            {t}
          </span>
        ))}
      </div>
    </button>
  );
}
