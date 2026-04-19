import { useEffect, useState } from 'react';
import { loadData } from '../../lib/dataLoader.js';
import { formatNaira, formatPct } from '../../lib/format.js';

export default function ScenarioTable() {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    loadData('scenarios').then(setRows);
  }, []);

  if (!rows.length) return <div className="text-muted">Loading scenarios…</div>;

  return (
    <div className="overflow-auto rounded-2xl border border-white/10">
      <table className="w-full text-sm">
        <thead className="bg-dusk">
          <tr className="text-left">
            <th className="px-4 py-3 font-medium">Scenario</th>
            <th className="px-4 py-3 font-medium tabular-nums">DTP3 (95% CI)</th>
            <th className="px-4 py-3 font-medium tabular-nums">Cost / child</th>
            <th className="px-4 py-3 font-medium tabular-nums">Concentration index</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id} className="border-t border-white/5 hover:bg-dusk/50">
              <td className="px-4 py-3">{r.id}</td>
              <td className="px-4 py-3 tabular-nums">
                {formatPct(r.dtp3_mean, 1)}
                <span className="text-xs text-muted ml-2">
                  ({formatPct(r.dtp3_ci_low, 1)}–{formatPct(r.dtp3_ci_high, 1)})
                </span>
              </td>
              <td className="px-4 py-3 tabular-nums">{formatNaira(r.cost_per_child_mean)}</td>
              <td className="px-4 py-3 tabular-nums">{r.concentration_index.toFixed(3)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
