import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, CartesianGrid } from 'recharts';
import { loadData } from '../../../lib/dataLoader.js';

export default function Shap() {
  const [data, setData] = useState(null);
  useEffect(() => { loadData('shap_summary').then(setData); }, []);
  if (!data) return <div className="text-muted">Loading…</div>;

  const DOMAINS = ['Predisposing', 'Enabling', 'Need', 'Dynamic'];
  const chart = DOMAINS.map((d) => ({
    domain: d,
    T1: data.t1?.andersen_domains?.[d] ?? 0,
    T2: data.t2?.andersen_domains?.[d] ?? 0,
    Full: data.full?.andersen_domains?.[d] ?? 0,
  }));

  return (
    <div>
      <h2 className="font-serif text-3xl mb-4">SHAP · Andersen domain decomposition</h2>
      <p className="text-muted max-w-3xl mb-8">
        Mean absolute SHAP by Andersen domain for each transition-specific model. Dynamic temporal features dominate all three models, challenging the original hypothesis.
      </p>
      <div className="w-full h-96 rounded-2xl border border-white/10 bg-dusk/30 p-6">
        <ResponsiveContainer>
          <BarChart data={chart}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1A2340" />
            <XAxis dataKey="domain" stroke="#9AA3B8" style={{ fontSize: 12 }} />
            <YAxis stroke="#9AA3B8" style={{ fontSize: 12 }} label={{ value: 'Mean |SHAP|', angle: -90, position: 'insideLeft', fill: '#9AA3B8' }} />
            <Tooltip contentStyle={{ background: '#0D1220', border: '1px solid #1A2340', color: '#F4F0E6' }} />
            <Legend />
            <Bar dataKey="T1" fill="#F5B042" />
            <Bar dataKey="T2" fill="#5A7BFF" />
            <Bar dataKey="Full" fill="#47B7A0" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
