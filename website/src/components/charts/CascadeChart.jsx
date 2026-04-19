import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts';
import { loadData } from '../../lib/dataLoader.js';

export default function CascadeChart() {
  const [data, setData] = useState(null);

  useEffect(() => {
    loadData('cascade').then(setData);
  }, []);

  if (!data) return <div className="text-muted">Loading cascade…</div>;

  return (
    <div className="w-full h-96 rounded-2xl border border-white/10 bg-dusk/30 p-6">
      <ResponsiveContainer>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1A2340" />
          <XAxis dataKey="zone" stroke="#9AA3B8" style={{ fontSize: 12 }} />
          <YAxis stroke="#9AA3B8" style={{ fontSize: 12 }} label={{ value: 'Coverage %', angle: -90, position: 'insideLeft', fill: '#9AA3B8' }} />
          <Tooltip contentStyle={{ background: '#0D1220', border: '1px solid #1A2340', color: '#F4F0E6' }} />
          <Legend />
          <Bar dataKey="dtp1_pct" name="DTP1" fill="#F5B042" />
          <Bar dataKey="dtp2_pct" name="DTP2" fill="#5A7BFF" />
          <Bar dataKey="dtp3_pct" name="DTP3" fill="#47B7A0" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
