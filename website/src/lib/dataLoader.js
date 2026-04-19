const BASE = import.meta.env.BASE_URL || '/';
const cache = new Map();

export async function loadData(name) {
  if (cache.has(name)) return cache.get(name);
  const url = `${BASE}data/${name}.json`.replace(/\/+/g, '/');
  const promise = fetch(url).then((r) => {
    if (!r.ok) throw new Error(`Failed to load ${name}: ${r.status}`);
    return r.json();
  });
  cache.set(name, promise);
  try {
    return await promise;
  } catch (err) {
    cache.delete(name);
    throw err;
  }
}

/**
 * Picks the discrete scenario row from scenarios.json that best matches the
 * requested policy `rule`. Used as a degraded-state fallback when the
 * 4D scenario_cube.json fails to load (network error, partial deploy, etc.).
 *
 * Returns null if scenarios.json itself is missing — the caller is responsible
 * for surfacing that to the user.
 */
const RULE_TO_SCENARIO_ID = {
  uniform_sms: 'S1: Uniform SMS',
  uniform_chw: 'S2: Uniform CHW',
  top30_risk: 'S3: Risk-Targeted',
  top10_incentive: 'S3: Risk-Targeted',
  rl_optimised: 'S4: RL-Optimised',
};

export async function loadFallbackScenario(rule) {
  try {
    const scenarios = await loadData('scenarios');
    const id = RULE_TO_SCENARIO_ID[rule] || 'S0: Status Quo';
    const row = scenarios.find((s) => s.id === id) || scenarios[0];
    if (!row) return null;
    return {
      dtp3_mean: row.dtp3_mean,
      dtp3_ci_low: row.dtp3_ci_low,
      dtp3_ci_high: row.dtp3_ci_high,
      cost_per_child: row.cost_per_child_mean,
      concentration_index: row.concentration_index,
      _source: 'discrete-fallback',
      _scenarioId: row.id,
    };
  } catch {
    return null;
  }
}

export function clearCache() {
  cache.clear();
}
