export default function MetricCard({ label, value, sublabel, tone = 'default' }) {
  const tones = {
    default: 'border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.08),rgba(255,255,255,0.04))]',
    positive: 'border-verdigris/45 bg-[linear-gradient(180deg,rgba(71,183,160,0.16),rgba(255,255,255,0.04))]',
    warning: 'border-saffron/45 bg-[linear-gradient(180deg,rgba(245,176,66,0.16),rgba(255,255,255,0.04))]',
    negative: 'border-terracotta/45 bg-[linear-gradient(180deg,rgba(198,85,58,0.16),rgba(255,255,255,0.04))]',
  };
  return (
    <div className={`rounded-[1.75rem] border p-6 shadow-[0_20px_70px_rgba(0,0,0,0.16)] backdrop-blur-sm ${tones[tone]}`}>
      <div className="text-xs uppercase tracking-wider text-muted">{label}</div>
      <div className="mt-3 font-serif text-4xl tabular-nums text-moonlight">{value}</div>
      {sublabel && <div className="mt-2 text-sm text-muted">{sublabel}</div>}
    </div>
  );
}
