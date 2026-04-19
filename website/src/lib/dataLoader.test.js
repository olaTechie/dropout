import { describe, it, expect, beforeEach, vi } from 'vitest';
import { loadData, clearCache } from './dataLoader.js';

describe('dataLoader', () => {
  beforeEach(() => {
    clearCache();
    global.fetch = vi.fn();
  });

  it('fetches JSON from /data/<name>.json', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ foo: 1 }),
    });
    const data = await loadData('cascade');
    expect(fetch).toHaveBeenCalledWith('/dropout/data/cascade.json');
    expect(data).toEqual({ foo: 1 });
  });

  it('caches by name — second call does not refetch', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ cached: true }),
    });
    await loadData('cascade');
    await loadData('cascade');
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it('throws on fetch error', async () => {
    fetch.mockResolvedValueOnce({ ok: false, status: 404 });
    await expect(loadData('missing')).rejects.toThrow();
  });

  it('clearCache allows re-fetch', async () => {
    fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ n: 1 }),
    });
    await loadData('x');
    clearCache();
    await loadData('x');
    expect(fetch).toHaveBeenCalledTimes(2);
  });
});
