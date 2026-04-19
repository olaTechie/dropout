import { useEffect, useState } from 'react';
import { loadData } from '../../../lib/dataLoader.js';

export default function RL() {
  return (
    <div>
      <h2 className="font-serif text-3xl mb-4">Offline reinforcement learning</h2>
      <p className="text-muted max-w-3xl mb-8">
        Three offline RL algorithms (CQL, IQL, BCQ) trained on the same 3-action trajectory dataset. IQL selected as winner on FQE, with OOD frequency of 0%.
      </p>
      <div className="grid md:grid-cols-3 gap-6">
        {[
          { alg: 'CQL', fqe: 0.700, wis: '—', ood: '0.0%' },
          { alg: 'IQL (winner)', fqe: 0.872, wis: '—', ood: '0.0%' },
          { alg: 'BCQ', fqe: 0.610, wis: '—', ood: '0.0%' },
        ].map((r) => (
          <div key={r.alg} className={`rounded-2xl border p-6 ${r.alg.includes('winner') ? 'border-saffron/70 bg-saffron/5' : 'border-white/10 bg-dusk/30'}`}>
            <div className="font-mono text-xs uppercase text-muted">{r.alg}</div>
            <div className="mt-2 font-serif text-3xl tabular-nums">{r.fqe.toFixed(3)}</div>
            <div className="text-sm text-muted">FQE policy value</div>
            <div className="mt-4 text-sm">OOD frequency: <span className="tabular-nums">{r.ood}</span></div>
          </div>
        ))}
      </div>
    </div>
  );
}
