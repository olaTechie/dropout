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

export function clearCache() {
  cache.clear();
}
