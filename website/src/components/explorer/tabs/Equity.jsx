import { useEffect, useState } from 'react';
import { loadData } from '../../../lib/dataLoader.js';

export default function Equity() {
  const [rows, setRows] = useState([]);
  useEffect(() => { loadData('scenarios').then(setRows); }, []);

  return (
    <div>
      <h2 className="font-serif text-3xl mb-4">Equity</h2>
      <p className="text-muted max-w-3xl mb-8">
        Three metrics: Wagstaff concentration index, slope index of inequality (SII), and the poorest-richest wealth gap. Computed with survey weights (v005/1e6).
      </p>
      <div className="rounded-2xl border border-white/10 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-dusk">
            <tr className="text-left">
              <th className="px-4 py-3">Scenario</th>
              <th className="px-4 py-3 tabular-nums">Concentration</th>
              <th className="px-4 py-3 tabular-nums">SII</th>
              <th className="px-4 py-3 tabular-nums">Wealth gap</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} className="border-t border-white/5">
                <td className="px-4 py-3">{r.id}</td>
                <td className="px-4 py-3 tabular-nums">{r.concentration_index.toFixed(3)}</td>
                <td className="px-4 py-3 tabular-nums">{r.slope_index.toFixed(3)}</td>
                <td className="px-4 py-3 tabular-nums">{r.wealth_gap.toFixed(3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
