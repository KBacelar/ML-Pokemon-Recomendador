import { useState } from 'react';
import BattleSlot from '../components/BattleSlot';
import PokemonPicker from '../components/PokemonPicker';
import MatchupList from '../components/MatchupList';
import { fetchMatchups } from '../services/battleService';
import './BattleField.css';

export default function BattleField() {
  const [challenger, setChallenger] = useState(null); //guarda o Pokémon selecionado 
  const [pickerOpen, setPickerOpen] = useState(false); // controla a abertura do modal de seleção de Pokémon
  const [matchups, setMatchups] = useState(null); // guarda os resultados dos matchups retornados pela API
  const [loading, setLoading] = useState(false); // indica se a análise de matchups está em andamento
  const [error, setError] = useState(null); // guarda mensagens de erro caso a análise falhe
  const [minWinRate, setMinWinRate] = useState(50); // guarda o valor mínimo de taxa de vitória para filtrar os matchups exibidos

  function handleSelect(pokemon) {
    setChallenger(pokemon);
    setMatchups(null);
    setError(null);
  }

  async function handleAnalyze() {
    if (!challenger) return;
    setLoading(true);
    setError(null);
    setMatchups(null);
    try {
      const res = await fetchMatchups(challenger, { minWinRate });
      setMatchups(res);
    } catch (err) {
      setError(err.message || 'Erro ao calcular matchups.');
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setChallenger(null);
    setMatchups(null);
    setError(null);
  }

  return (
    <div className="battle">
      <header className="battle__header">
        <h1>Campo de Batalha</h1>
        <p>
          Escolha um Pokémon e descubra quais adversários ele tem maior chance de vencer.
        </p>
      </header>

      <div className="battle__arena">
        <div className="battle__sky" />
        <div className="battle__ground" />

        <div className="battle__slots battle__slots--single">
          <BattleSlot
            side="left"
            pokemon={challenger}
            onPick={() => setPickerOpen(true)}
          />
        </div>
      </div>

      {challenger && (
        <div className="battle__controls">
          <label className="battle__threshold">
            <span>Mostrar adversários com chance de vitória maior ou igual a</span>
            <div className="battle__threshold-row">
              <input
                type="range"
                min={50}
                max={95}
                step={5}
                value={minWinRate}
                onChange={(e) => setMinWinRate(Number(e.target.value))}
              />
              <strong>{minWinRate}%</strong>
            </div>
          </label>
        </div>
      )}

      <div className="battle__actions">
        <button
          className="battle__btn battle__btn--primary"
          onClick={handleAnalyze}
          disabled={!challenger || loading}
        >
          {loading ? 'Analisando...' : 'ANALISAR MATCHUPS'}
        </button>
        <button className="battle__btn" onClick={handleReset} disabled={!challenger}>
          Reiniciar
        </button>
      </div>

      {error && <div className="battle__error">{error}</div>}

      <MatchupList
        matchups={matchups}
        loading={loading}
        error={null}
        pokemonName={challenger?.name}
      />

      <PokemonPicker
        open={pickerOpen}
        onClose={() => setPickerOpen(false)}
        onSelect={handleSelect}
        title="Escolher seu desafiante"
      />
    </div>
  );
}
