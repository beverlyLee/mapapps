// 封装对后端 /api 的调用（开发期由 Vite 代理到 :8000）

async function getJSON(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`请求失败 ${r.status}: ${url}`);
  return r.json();
}

export const fetchPoints = () => getJSON('/api/cicada/points');
export const fetchStats = () => getJSON('/api/cicada/stats');
export const fetchSpecies = () => getJSON('/api/cicada/species');
export const fetchPoint = (id) => getJSON(`/api/cicada/points/${id}`);
