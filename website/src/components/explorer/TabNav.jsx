import { NavLink, useSearchParams } from 'react-router-dom';

const TABS = [
  { id: 'cascade', label: 'Cascade' },
  { id: 'models', label: 'Prediction models' },
  { id: 'shap', label: 'SHAP / Andersen' },
  { id: 'rl', label: 'Offline RL' },
  { id: 'microsim', label: 'Microsim' },
  { id: 'equity', label: 'Equity' },
  { id: 'validation', label: 'Validation' },
  { id: 'downloads', label: 'Downloads' },
];

export default function TabNav({ active, onChange }) {
  return (
    <div className="border-b border-white/5 mb-8 overflow-x-auto">
      <ul className="flex gap-6 min-w-max">
        {TABS.map((t) => (
          <li key={t.id}>
            <button
              onClick={() => onChange(t.id)}
              className={`py-3 text-sm border-b-2 transition ${
                active === t.id ? 'border-saffron text-moonlight' : 'border-transparent text-muted hover:text-moonlight'
              }`}
            >
              {t.label}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
