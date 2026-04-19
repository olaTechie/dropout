import { useScenarioStore } from '../../state/scenario.js';
import { formatNaira } from '../../lib/format.js';

export default function BudgetSlider({ min = 250_000_000, max = 1_500_000_000, step = 25_000_000 }) {
  const budget = useScenarioStore((s) => s.budget);
  const setBudget = useScenarioStore((s) => s.setBudget);

  return (
    <div>
      <div className="flex items-baseline justify-between mb-2">
        <label htmlFor="budget" className="text-sm text-muted">National annual budget</label>
        <span className="font-serif text-2xl tabular-nums">{formatNaira(budget)}</span>
      </div>
      <input
        id="budget"
        type="range"
        min={min}
        max={max}
        step={step}
        value={budget}
        onChange={(e) => setBudget(parseInt(e.target.value, 10))}
        className="w-full accent-saffron"
        aria-label="National budget"
      />
      <div className="mt-1 flex justify-between text-xs text-muted">
        <span>{formatNaira(min)}</span>
        <span>{formatNaira(max)}</span>
      </div>
    </div>
  );
}
