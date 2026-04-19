import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { useScenarioStore } from '../../state/scenario.js';
import { formatNaira, formatPct } from '../../lib/format.js';
import { useEffect, useState } from 'react';
import { loadData } from '../../lib/dataLoader.js';
import { buildCubeIndex, interpolateScenario } from '../../lib/interp.js';

export default function DashboardOverlay({ visible = true }) {
  const [cube, setCube] = useState(null);
  const { budget, rule, sms_rrr, chw_rrr } = useScenarioStore();
  useEffect(() => { loadData('scenario_cube').then((r) => setCube(buildCubeIndex(r))); }, []);
  const live = cube ? interpolateScenario(cube, { budget, rule, sms_rrr, chw_rrr }) : null;

  const cards = [
    { label: 'Recommended', value: 'Risk-targeted CHW', sub: 'Top 30% risk → CHW, rest → SMS' },
    { label: 'DTP3 uplift', value: live ? formatPct(live.dtp3_mean, 1) : '—' },
    { label: 'ICER vs S0', value: '₦8,007', sub: 'per DTP3 completion' },
    { label: 'Budget', value: formatNaira(budget) },
    { label: 'Concentration index', value: live ? live.concentration_index.toFixed(3) : '—' },
    { label: 'Downloads', value: '→' },
  ];

  return (
    <motion.aside
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: visible ? 1 : 0, y: visible ? 0 : 40 }}
      transition={{ duration: 0.8, staggerChildren: 0.1 }}
      className="fixed bottom-8 inset-x-8 z-20 grid grid-cols-2 md:grid-cols-3 gap-4 max-w-6xl mx-auto"
    >
      {cards.map((c, i) => (
        <motion.div
          key={c.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.08, duration: 0.4 }}
          className="rounded-2xl border border-white/10 bg-abyss/70 backdrop-blur-md p-4"
        >
          <div className="text-xs uppercase tracking-wider text-muted">{c.label}</div>
          <div className="mt-1 font-serif text-2xl tabular-nums">{c.value}</div>
          {c.sub && <div className="text-xs text-muted mt-1">{c.sub}</div>}
        </motion.div>
      ))}
      <div className="col-span-full flex gap-4 justify-center mt-4">
        <Link to="/policy" className="px-6 py-3 bg-saffron text-abyss rounded-full font-semibold hover:bg-saffron/90">See full dashboard →</Link>
        <Link to="/simulation" className="px-6 py-3 border border-white/20 rounded-full hover:bg-white/5">Try scenarios →</Link>
      </div>
    </motion.aside>
  );
}
