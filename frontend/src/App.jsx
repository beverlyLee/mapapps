import { useEffect, useState, useCallback, useRef } from 'react';
import { fetchPoints, fetchStats, fetchSpecies } from './api';
import CicadaMap from './components/CicadaMap.jsx';
import Sidebar from './components/Sidebar.jsx';
import RegionNavigator from './components/RegionNavigator.jsx';
import { IconMenu, IconX } from './components/Icons.jsx';

export default function App() {
  const [points, setPoints] = useState([]);
  const [stats, setStats] = useState(null);
  const [species, setSpecies] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selected, setSelected] = useState(null);
  const [region, setRegion] = useState({
    province: '', city: '', district: '', town: '',
  });
  const mapApi = useRef(null);

  const handleReady = useCallback((api) => { mapApi.current = api; }, []);

  const load = useCallback((r = {}) => {
    setLoading(true);
    setError(null);
    const params = {};
    if (r.province) params.province = r.province;
    if (r.city) params.city = r.city;
    if (r.district) params.district = r.district;
    if (r.town) params.town = r.town;
    Promise.all([
      fetchPoints(params),
      fetchStats(params),
      fetchSpecies(),
    ])
      .then(([p, s, sp]) => {
        setPoints(p);
        setStats(s);
        setSpecies(sp);
      })
      .catch((e) => setError(e.message || String(e)))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(region); }, [region, load]);

  const onSelect = (pt) => {
    if (mapApi.current) mapApi.current.flyTo(pt);
    if (drawerOpen) setDrawerOpen(false);
    setSelected(pt);
  };

  const resetRegion = () => {
    setRegion({ province: '', city: '', district: '', town: '' });
  };

  return (
    <div className={`app${drawerOpen ? ' drawer-open' : ''}`}>
      <Sidebar
        stats={stats}
        species={species}
        points={points}
        loading={loading}
        error={error}
        onRetry={() => load(region)}
        onSelect={onSelect}
        onClose={() => setDrawerOpen(false)}
        region={region}
        onResetRegion={resetRegion}
        selected={selected}
        onClearDetail={() => setSelected(null)}
      />
      <div className="main-area">
        <RegionNavigator
          region={region}
          setRegion={setRegion}
          onSelectPoint={onSelect}
        />
          <div className="map-wrap">
            <CicadaMap points={points} region={region} onReady={handleReady} onSelectPoint={onSelect} />
          </div>
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
