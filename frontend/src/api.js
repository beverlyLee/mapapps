const noCacheInit = {
  cache: 'no-store',
  pragma: 'no-cache',
  headers: { 'Cache-Control': 'no-cache, no-store, must-revalidate' },
};

async function getJSON(url) {
  const sep = url.includes('?') ? '&' : '?';
  const r = await fetch(`${url}${sep}_t=${Date.now()}`, noCacheInit);
  if (!r.ok) throw new Error(`请求失败 ${r.status}: ${url}`);
  return r.json();
}

export const fetchPoints = (params = {}) => {
  const qs = new URLSearchParams(params).toString();
  return getJSON(`/api/cicada/points${qs ? '?' + qs : ''}`);
};

export const fetchStats = (params = {}) => {
  const qs = new URLSearchParams(params).toString();
  return getJSON(`/api/cicada/stats${qs ? '?' + qs : ''}`);
};

export const fetchSpecies = () => getJSON('/api/cicada/species');
export const fetchPoint = (id) => getJSON(`/api/cicada/points/${id}`);
export const fetchRegions = () => getJSON('/api/cicada/regions');
export const fetchSearch = (q) => getJSON(`/api/cicada/search?q=${encodeURIComponent(q)}`);
export const fetchDistrictStats = (district) => getJSON(`/api/cicada/districts/${encodeURIComponent(district)}/stats`);
