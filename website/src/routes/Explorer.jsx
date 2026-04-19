import { useState } from 'react';
import TabNav from '../components/explorer/TabNav.jsx';
import Cascade from '../components/explorer/tabs/Cascade.jsx';
import PredictionModels from '../components/explorer/tabs/PredictionModels.jsx';
import Shap from '../components/explorer/tabs/Shap.jsx';
import RL from '../components/explorer/tabs/RL.jsx';
import Microsim from '../components/explorer/tabs/Microsim.jsx';
import Equity from '../components/explorer/tabs/Equity.jsx';
import Validation from '../components/explorer/tabs/Validation.jsx';
import Downloads from '../components/explorer/tabs/Downloads.jsx';

const TAB_MAP = {
  cascade: Cascade,
  models: PredictionModels,
  shap: Shap,
  rl: RL,
  microsim: Microsim,
  equity: Equity,
  validation: Validation,
  downloads: Downloads,
};

export default function Explorer() {
  const [active, setActive] = useState('cascade');
  const Active = TAB_MAP[active];
  return (
    <main className="max-w-6xl mx-auto px-6 py-12">
      <header className="mb-8">
        <h1 className="font-serif text-5xl">Explorer</h1>
        <p className="mt-3 text-muted max-w-2xl">
          Researcher-grade data from the full dropout analytical pipeline.
        </p>
      </header>
      <TabNav active={active} onChange={setActive} />
      <section
        role="tabpanel"
        id={`tabpanel-${active}`}
        aria-labelledby={`tab-${active}`}
        tabIndex={0}
      >
        <Active />
      </section>
    </main>
  );
}
