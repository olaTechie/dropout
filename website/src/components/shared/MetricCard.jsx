export default function MetricCard({ label, value, sublabel, tone = 'default' }) {
  const tones = {
    default: 'bg-dusk border-white/10',
    positive: 'bg-dusk border-verdigris/50',
    warning: 'bg-dusk border-saffron/50',
    negative: 'bg-dusk border-terracotta/50',
  };
  return (
    <div className={`rounded-2xl border p-6 ${tones[tone]}`}>
      <div className="text-xs uppercase tracking-wider text-muted">{label}</div>
      <div className="mt-2 font-serif text-4xl tabular-nums">{value}</div>
      {sublabel && <div className="mt-1 text-sm text-muted">{sublabel}</div>}
    </div>
  );
}
