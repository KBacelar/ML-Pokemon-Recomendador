import shapRn from "../assets/shap-rn.png";
import shapRL from "../assets/shap-rl.png";
import shapRf from "../assets/shap-rf.png";
import "./Shap.css";
export default function Sharp() {
  return (
    <div className="shap">
      <header className="shap__header">
        <h1>Análise SHAP</h1>
        <h3>
          As análises SHAP são uma técnica baseada na Teoria de Jogos, utilizada
          para interpretar modelos de Machine Learning. Ela calcula a
          contribuição de cada variável (feature) para a decisão final do
          modelo.
        </h3>
      </header>
      <div className="shap__content">
        <img src={shapRn} alt="Análise SHARP" />
        <img src={shapRL} alt="Análise SHARP" />
        <img src={shapRf} alt="Análise SHARP" />
      </div>
    </div>
  );
}
