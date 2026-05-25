import { getTypeColor } from '../services/pokemonService';
import './MatchupList.css';

function winRateLabel(rate) {
  if (rate >= 85) return 'Vitória quase certa';
  if (rate >= 70) return 'Forte favorito';
  if (rate >= 55) return 'Leve vantagem';
  return 'Disputa equilibrada';
}

function winRateClass(rate) {
  if (rate >= 85) return 'matchup__winrate--strong';
  if (rate >= 70) return 'matchup__winrate--good';
  if (rate >= 55) return 'matchup__winrate--mild';
  return 'matchup__winrate--neutral';
}

export default function MatchupList({ matchups, loading, error, pokemonName }) {
  if (loading) {
    return (
      <div className="matchups">
        <div className="matchups__loading">
          <div className="matchups__spinner" />
          <p>Calculando matchups contra todos os Pokémon...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="matchups__error">{error}</div>;
  }

  if (!matchups) return null;

  if (matchups.likelyWins.length === 0) {
    return (
      <div className="matchups__empty">
        <h3>Nenhum adversário fácil encontrado</h3>
        <p>
          Com base na análise, <strong>{pokemonName}</strong> não tem vantagem clara sobre
          os Pokémon avaliados. Tente outro!
        </p>
      </div>
    );
  }

  return (
    <div className="matchups">
      <header className="matchups__header">
        <h2>
          Pokémon que <span className="matchups__name">{pokemonName}</span> tem maior chance
          de vencer
        </h2>
        <p className="matchups__meta">
          {matchups.likelyWins.length} resultado(s) de {matchups.totalEvaluated} avaliados
          <span className="matchups__source">fonte: {matchups.source}</span>
        </p>
      </header>

      <ul className="matchups__list">
        {matchups.likelyWins.map(({ opponent, winRate, opponentPower }) => {
          const color = getTypeColor(opponent.types[0]);
          return (
            <li
              key={opponent.id}
              className="matchup"
              style={{ '--type-color': color }}
            >
              <div className="matchup__image-wrap">
                <img src={opponent.image} alt={opponent.name} className="matchup__image" />
              </div>

              <div className="matchup__info">
                <div className="matchup__top">
                  <span className="matchup__name-text">{opponent.name}</span>
                  <span className="matchup__id">#{String(opponent.id).padStart(3, '0')}</span>
                </div>

                <div className="matchup__types">
                  {opponent.types.map((t) => (
                    <span
                      key={t}
                      className="matchup__type"
                      style={{ background: getTypeColor(t) }}
                    >
                      {t}
                    </span>
                  ))}
                </div>

                <div className="matchup__bar" aria-label={`chance de vitória ${winRate}%`}>
                  <div
                    className={`matchup__bar-fill ${winRateClass(winRate)}`}
                    style={{ width: `${winRate}%` }}
                  />
                  <span className="matchup__bar-text">
                    {winRate}% — {winRateLabel(winRate)}
                  </span>
                </div>

                {opponentPower != null && (
                  <div className="matchup__power">Poder do adversário: {opponentPower}</div>
                )}
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
