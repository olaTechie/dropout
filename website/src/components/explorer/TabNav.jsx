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
      className="mb-8 flex min-w-max gap-3 overflow-x-auto rounded-full border border-white/10 bg-white/5 p-2 shadow-[0_18px_60px_rgba(0,0,0,0.14)]"
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
            className={`rounded-full px-4 py-3 text-sm whitespace-nowrap transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-saffron/60 ${
              selected
                ? 'bg-saffron text-abyss font-semibold shadow-[0_8px_24px_rgba(245,176,66,0.22)]'
                : 'text-muted hover:bg-white/7 hover:text-moonlight'
            }`}
          >
            {t.label}
          </button>
        );
      })}
    </div>
  );
}
