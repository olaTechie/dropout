import { useEffect, useState } from 'react';
import { loadData } from '../../lib/dataLoader.js';
import { formatNaira, formatPct } from '../../lib/format.js';

export default function ScenarioTable() {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    loadData('scenarios').then(setRows);
  }, []);

  if (!rows.length) {
    return (
      <div className="rounded-[1.75rem] border border-white/10 bg-white/5 px-5 py-6 text-sm text-muted">
        Loading scenarios…
      </div>
    );
  }

  return (
    <div className="overflow-auto rounded-[1.75rem] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.07),rgba(255,255,255,0.03))] shadow-[0_24px_80px_rgba(0,0,0,0.2)]">
      <table className="w-full text-sm">
        <thead className="bg-dusk/70 text-moonlight">
          <tr className="text-left">
            <th className="px-5 py-4 font-medium">Scenario</th>
            <th className="px-5 py-4 font-medium tabular-nums">DTP3 (95% CI)</th>
            <th className="px-5 py-4 font-medium tabular-nums">Cost / child</th>
            <th className="px-5 py-4 font-medium tabular-nums">Concentration index</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id} className="border-t border-white/6 hover:bg-white/6 transition">
              <td className="px-5 py-4">
                <div className="font-medium text-moonlight">{r.id}</div>
              </td>
              <td className="px-5 py-4 tabular-nums">
                <span className="font-medium text-moonlight">{formatPct(r.dtp3_mean, 1)}</span>
                <span className="text-xs text-muted ml-2">
                  ({formatPct(r.dtp3_ci_low, 1)}–{formatPct(r.dtp3_ci_high, 1)})
                </span>
              </td>
              <td className="px-5 py-4 tabular-nums">{formatNaira(r.cost_per_child_mean)}</td>
              <td className="px-5 py-4 tabular-nums">{r.concentration_index.toFixed(3)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
