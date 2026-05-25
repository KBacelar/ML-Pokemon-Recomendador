import { getTypeColor } from '../services/pokemonService';
import './BattleSlot.css';

const STAT_LABELS = {
  hp: 'HP',
  attack: 'ATK',
  defense: 'DEF',
  'special-attack': 'SP.ATK',
  'special-defense': 'SP.DEF',
  speed: 'SPD',
};

export default function BattleSlot({
  side,
  pokemon,
  onPick,
  powerPercent,
  isWinner,
  isLoser,
  isTie,
}) {
  if (!pokemon) {
    return (
      <div className={`battle-slot battle-slot--${side} battle-slot--empty`}>
        <button type="button" className="battle-slot__pick" onClick={onPick}>
          <span className="battle-slot__pick-icon">+</span>
          <span>Escolher Pokémon</span>
        </button>
      </div>
    );
  }

  const color = getTypeColor(pokemon.types[0]);

  return (
    <div
      className={`battle-slot battle-slot--${side} ${
        isWinner ? 'battle-slot--winner' : ''
      } ${isLoser ? 'battle-slot--loser' : ''} ${isTie ? 'battle-slot--tie' : ''}`}
      style={{ '--type-color': color }}
    >
      <div className="battle-slot__header">
        <span className="battle-slot__name">{pokemon.name}</span>
        <button type="button" className="battle-slot__swap" onClick={onPick}>
          Trocar
        </button>
      </div>

      {powerPercent != null && (
        <div className="battle-slot__hpbar" aria-label="barra de poder">
          <div
            className="battle-slot__hpbar-fill"
            style={{ width: `${powerPercent}%` }}
          />
          <span className="battle-slot__hpbar-text">{powerPercent}%</span>
        </div>
      )}

      <div className="battle-slot__arena">
        <div className="battle-slot__shadow" />
        <img
          src={pokemon.image}
          alt={pokemon.name}
          className="battle-slot__sprite"
        />
        {isWinner && <div className="battle-slot__badge">VENCEDOR</div>}
        {isTie && <div className="battle-slot__badge battle-slot__badge--tie">EMPATE</div>}
      </div>

      <div className="battle-slot__stats">
        {Object.entries(STAT_LABELS).map(([key, label]) => (
          <div key={key} className="battle-slot__stat">
            <span className="battle-slot__stat-label">{label}</span>
            <span className="battle-slot__stat-value">{pokemon.stats[key] ?? '-'}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
