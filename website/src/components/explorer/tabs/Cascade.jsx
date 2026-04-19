import CascadeChart from '../../charts/CascadeChart.jsx';
import { useEffect, useState } from 'react';
import { loadData } from '../../../lib/dataLoader.js';
import { formatPct } from '../../../lib/format.js';

export default function Cascade() {
  const [rows, setRows] = useState([]);
  useEffect(() => { loadData('cascade').then(setRows); }, []);

  return (
    <div>
      <h2 className="font-serif text-3xl mb-4">Immunisation cascade by zone</h2>
      <p className="text-muted max-w-3xl mb-8">
        DTP1, DTP2, and DTP3 coverage across Nigeria's six geopolitical zones, with WHO dropout rate. Values from the analytic sample of 3,194 children aged 12–23 months.
      </p>

      <CascadeChart />

      <table className="w-full mt-12 text-sm border border-white/10 rounded-2xl overflow-hidden">
        <thead className="bg-dusk">
          <tr className="text-left">
            <th className="px-4 py-3">Zone</th>
            <th className="px-4 py-3 tabular-nums">n</th>
            <th className="px-4 py-3 tabular-nums">DTP1</th>
            <th className="px-4 py-3 tabular-nums">DTP2</th>
            <th className="px-4 py-3 tabular-nums">DTP3</th>
            <th className="px-4 py-3 tabular-nums">WHO dropout</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.zone} className="border-t border-white/5">
              <td className="px-4 py-3">{r.zone}</td>
              <td className="px-4 py-3 tabular-nums">{r.n}</td>
              <td className="px-4 py-3 tabular-nums">{formatPct(r.dtp1_pct / 100, 1)}</td>
              <td className="px-4 py-3 tabular-nums">{formatPct(r.dtp2_pct / 100, 1)}</td>
              <td className="px-4 py-3 tabular-nums">{formatPct(r.dtp3_pct / 100, 1)}</td>
              <td className="px-4 py-3 tabular-nums">{formatPct(r.who_dropout / 100, 1)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
