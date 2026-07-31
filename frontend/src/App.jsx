import { useEffect, useState, useCallback, useRef } from 'react';
import { fetchPoints, fetchStats, fetchSpecies } from './api';
import CicadaMap from './components/CicadaMap.jsx';
import Sidebar from './components/Sidebar.jsx';
import { IconMenu, IconX } from './components/Icons.jsx';

export default function App() {
  const [points, setPoints] = useState([]);
  const [stats, setStats] = useState(null);
  const [species, setSpecies] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const mapApi = useRef(null);

  const handleReady = useCallback((api) => { mapApi.current = api; }, []);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    Promise.all([fetchPoints(), fetchStats(), fetchSpecies()])
      .then(([p, s, sp]) => {
        setPoints(p);
        setStats(s);
        setSpecies(sp);
      })
      .catch((e) => setError(e.message || String(e)))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  const onSelect = (pt) => {
    if (mapApi.current) mapApi.current.flyTo(pt);
    if (drawerOpen) setDrawerOpen(false); // 移动端选中后收起抽屉
  };

  return (
    <div className={`app${drawerOpen ? ' drawer-open' : ''}`}>
      <Sidebar
        stats={stats}
        species={species}
        points={points}
        loading={loading}
        error={error}
        onRetry={load}
        onSelect={onSelect}
        onClose={() => setDrawerOpen(false)}
      />
      <div className="map-wrap">
        <CicadaMap points={points} onReady={handleReady} />
      </div>

      <div className="backdrop" onClick={() => setDrawerOpen(false)} />
      <button
        className="drawer-toggle"
        aria-label={drawerOpen ? '关闭列表' : '打开列表'}
        onClick={() => setDrawerOpen((v) => !v)}
      >
        {drawerOpen ? <IconX width={18} height={18} className="close-x" /> : <IconMenu width={18} height={18} />}
        {drawerOpen ? '关闭' : '点位列表'}
      </button>
    </div>
  );
}
