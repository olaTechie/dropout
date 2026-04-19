import { useRef } from 'react';

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
  const refs = useRef({});

  const onKeyDown = (e) => {
    const idx = TABS.findIndex((t) => t.id === active);
    if (idx < 0) return;
    let next = idx;
    if (e.key === 'ArrowRight') next = (idx + 1) % TABS.length;
    else if (e.key === 'ArrowLeft') next = (idx - 1 + TABS.length) % TABS.length;
    else if (e.key === 'Home') next = 0;
    else if (e.key === 'End') next = TABS.length - 1;
    else return;
    e.preventDefault();
    const id = TABS[next].id;
    onChange(id);
    refs.current[id]?.focus();
  };

  return (
    <div
      role="tablist"
      aria-label="Explorer sections"
      className="border-b border-white/5 mb-8 overflow-x-auto flex gap-6 min-w-max"
      onKeyDown={onKeyDown}
    >
      {TABS.map((t) => {
        const selected = active === t.id;
        return (
          <button
            key={t.id}
            ref={(el) => { refs.current[t.id] = el; }}
            type="button"
            role="tab"
            id={`tab-${t.id}`}
            aria-selected={selected}
            aria-controls={`tabpanel-${t.id}`}
            tabIndex={selected ? 0 : -1}
            onClick={() => onChange(t.id)}
            className={`py-3 text-sm border-b-2 transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-saffron/60 ${
              selected ? 'border-saffron text-moonlight' : 'border-transparent text-muted hover:text-moonlight'
            }`}
          >
            {t.label}
          </button>
        );
      })}
    </div>
  );
}
