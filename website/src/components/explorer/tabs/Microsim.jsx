import { useEffect, useState } from 'react';
import { loadData } from '../../../lib/dataLoader.js';
import { formatNaira, formatPct } from '../../../lib/format.js';

export default function Microsim() {
  const [scenarios, setScenarios] = useState([]);
  useEffect(() => { loadData('scenarios').then(setScenarios); }, []);

  return (
    <div>
      <h2 className="font-serif text-3xl mb-4">Microsimulation — 6 primary scenarios</h2>
      <p className="text-muted max-w-3xl mb-8">
        10,000 synthetic children × 1,000 bootstrap iterations × PSA on RRR and costs × cluster-bootstrap on PSUs. All values reflect full uncertainty propagation.
      </p>
      <div className="rounded-2xl border border-white/10 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-dusk">
            <tr className="text-left">
              <th className="px-4 py-3">Scenario</th>
              <th className="px-4 py-3 tabular-nums">DTP3</th>
              <th className="px-4 py-3 tabular-nums">Cost/child</th>
              <th className="px-4 py-3 tabular-nums">Concentration index</th>
              <th className="px-4 py-3 tabular-nums">Wealth gap</th>
            </tr>
          </thead>
          <tbody>
            {scenarios.map((s) => (
              <tr key={s.id} className="border-t border-white/5">
                <td className="px-4 py-3">{s.id}</td>
                <td className="px-4 py-3 tabular-nums">{formatPct(s.dtp3_mean, 1)}</td>
                <td className="px-4 py-3 tabular-nums">{formatNaira(s.cost_per_child_mean)}</td>
                <td className="px-4 py-3 tabular-nums">{s.concentration_index.toFixed(3)}</td>
                <td className="px-4 py-3 tabular-nums">{s.wealth_gap.toFixed(3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
