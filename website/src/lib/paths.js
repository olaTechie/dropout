const BASE = import.meta.env.BASE_URL || '/';

export function withBase(path = '') {
  const base = BASE.endsWith('/') ? BASE : `${BASE}/`;
  const normalizedPath = path.replace(/^\/+/, '');
  return `${base}${normalizedPath}`.replace(/\/{2,}/g, '/');
}

export function buildHashURL(route, search = '') {
  const normalizedRoute = route.startsWith('/') ? route : `/${route}`;
  const normalizedSearch = search
    ? `?${search.replace(/^\?/, '')}`
    : '';
  return `${window.location.origin}${withBase('')}#${normalizedRoute}${normalizedSearch}`;
}
