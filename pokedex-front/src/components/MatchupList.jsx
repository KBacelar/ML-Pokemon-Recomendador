import { getTypeColor } from "../services/pokemonService";
import "./MatchupList.css";

function winRateClass(rate) {
  if (rate >= 85) return "matchup__winrate--strong";
  if (rate >= 70) return "matchup__winrate--good";
  if (rate >= 55) return "matchup__winrate--mild";
  return "matchup__winrate--neutral";
}
const getImgSrc = (name) =>
  `${process.env.REACT_APP_BACKEND_URL}/dados/pokemon_img/${name}.png`;

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
          Com base na análise, <strong>{pokemonName}</strong> não tem vantagem
          clara sobre os Pokémon avaliados. Tente outro!
        </p>
      </div>
    );
  }

  return (
    <div className="matchups">
      <header className="matchups__header">
        <h2>
          Pokémon que <span className="matchups__name">{pokemonName}</span> tem
          maior chance de vencer
        </h2>
        <p className="matchups__meta">
          {matchups.likelyWins.length} resultado(s) avaliados
          <span className="matchups__source">fonte: {matchups.source}</span>
        </p>
      </header>

      <ul className="matchups__list">
        {matchups.likelyWins.map(
          ({ opponent, Chance_RF, Chance_LR, Chance_NN, XP_Recompensa }) => {
            const color =
              getTypeColor(opponent.types[0]) ||
              "#777"; /*Precisa colocar a cor para todos os tipos do Pokémon oponente*/
            return (
              <li
                key={opponent.name}
                className="matchup"
                style={{ "--type-color": color }}
              >
                <div className="matchup__image-wrap">
                  <img
                    src={getImgSrc(opponent.name)}
                    alt={opponent.name}
                    className="matchup__image"
                  />{" "}
                </div>

                <div className="matchup__info">
                  <div className="matchup__info__header">
                    <div className="matchup__info__opponent">
                      <div className="matchup__top">
                        <span className="matchup__name-text">
                          {opponent.name}
                        </span>
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
                    </div>
                    <div className="matchup__info__xp">
                      <span>XP: {XP_Recompensa}</span>
                    </div>
                  </div>
                  <div>
                    <div className="matchup__models-header">
                      <span>Modelos</span>
                      <span>Chance de vitória</span>
                    </div>
                    {[
                      { model: "Random Forest", Chance: Chance_RF },
                      { model: "Regressão Logística", Chance: Chance_LR },
                      { model: "Rede Neural", Chance: Chance_NN },
                    ].map((model) => (
                      <div
                        className="matchup__bar"
                        aria-label={`chance de vitória ${model.Chance}%`}
                        key={model.model}
                      >
                        <div
                          className={`matchup__bar-fill ${winRateClass(model.Chance)}`}
                          style={{ width: `${model.Chance}%` }}
                        />
                        <span className="matchup__bar-text">
                          <span>{model.model}: </span>
                          <span>{model.Chance}%</span>
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </li>
            );
          },
        )}
      </ul>
    </div>
  );
}
