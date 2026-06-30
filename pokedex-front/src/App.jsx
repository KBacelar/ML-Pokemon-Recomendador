import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import BattleField from "./pages/BattleField";
import Pokedex from "./pages/Pokedex";
import "./App.css";
import Shap from "./pages/Shap";

export default function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <nav className="app__nav">
          <div className="app__brand">
            <span className="app__pokeball" aria-hidden="true" />
            <span>Pokédex Battle</span>
          </div>
          <div className="app__links">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `app__link ${isActive ? "app__link--active" : ""}`
              }
            >
              Campo de Batalha
            </NavLink>
            <NavLink
              to="/pokedex"
              className={({ isActive }) =>
                `app__link ${isActive ? "app__link--active" : ""}`
              }
            >
              Pokédex
            </NavLink>
            <NavLink
              to="/shap"
              className={({ isActive }) =>
                `app__link ${isActive ? "app__link--active" : ""}`
              }
            >
              Análise SHAP
            </NavLink>
          </div>
        </nav>

        <main className="app__main">
          <Routes>
            <Route path="/" element={<BattleField />} />
            <Route path="/pokedex" element={<Pokedex />} />
            <Route path="/shap" element={<Shap />} />
          </Routes>
        </main>

        <footer className="app__footer">
          Dados de Pokémon via PokéAPI · Comparação de forças via backend
        </footer>
      </div>
    </BrowserRouter>
  );
}
