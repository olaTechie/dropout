import { withBase } from '../../../lib/paths.js';

const FILES = [
  { name: 'Scenario catalogue', href: withBase('data/scenarios.json'), kind: 'JSON' },
  { name: 'Cascade summary', href: withBase('data/cascade.json'), kind: 'JSON' },
  { name: 'Scenario cube', href: withBase('data/scenario_cube.json'), kind: 'JSON' },
  { name: 'Validation report', href: withBase('data/validation.json'), kind: 'JSON' },
  { name: 'Source code (GitHub)', href: 'https://github.com/olatechie/dropout', kind: 'Code' },
];

export default function Downloads() {
  return (
    <div>
      <h2 className="font-serif text-3xl mb-4">Downloads</h2>
      <p className="text-muted max-w-3xl mb-8">
        Raw data, scenario cube, and source code for replication.
      </p>
      <ul className="space-y-3">
        {FILES.map((f) => (
          <li key={f.href}>
            <a href={f.href} target={f.href.startsWith('http') ? '_blank' : '_self'} rel="noreferrer" className="flex items-center justify-between rounded-xl border border-white/10 bg-dusk/30 p-4 hover:border-saffron/40 transition">
              <span>{f.name}</span>
              <span className="text-xs font-mono text-muted">{f.kind}</span>
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
