export function formatNaira(v) {
  if (v >= 1e9) return `₦${(v / 1e9).toFixed(v < 1e10 ? 1 : 0)}B`;
  if (v >= 1e6) return `₦${(v / 1e6).toFixed(0)}M`;
  if (v >= 1e3) return `₦${Math.round(v).toLocaleString('en-NG')}`;
  return `₦${Math.round(v)}`;
}

export function formatPct(v, digits = 0) {
  return `${(v * 100).toFixed(digits)}%`;
}

export function formatNumber(v) {
  return Math.round(v).toLocaleString('en-NG');
}
