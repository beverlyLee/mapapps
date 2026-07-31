import { useState, useEffect, useRef } from 'react';
import { fetchRegions, fetchSearch } from '../api';

export default function RegionNavigator({ region, setRegion, onSelectPoint }) {
  const [tree, setTree] = useState([]);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const searchTimer = useRef(null);

  useEffect(() => {
    fetchRegions().then(setTree).catch(() => {});
  }, []);

  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    clearTimeout(searchTimer.current);
    searchTimer.current = setTimeout(async () => {
      try {
        setLoading(true);
        const data = await fetchSearch(searchQuery.trim());
        setSearchResults(data.points || []);
      } catch {
        setSearchResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);
    return () => clearTimeout(searchTimer.current);
  }, [searchQuery]);

  const { province, city, district, town } = region;

  const provinces = tree.map(r => r.province);
  const cities = province ? (tree.find(r => r.province === province)?.cities || []) : [];
  const cityObj = cities.find(c => c.city === city);
  const districts = cityObj?.districts || [];

  const goto = (level, value) => {
    const next = { ...region };
    if (level === 'province') {
      next.province = value;
      next.city = '';
      next.district = '';
      next.town = '';
    } else if (level === 'city') {
      next.city = value;
      next.district = '';
      next.town = '';
    } else if (level === 'district') {
      next.district = value;
      next.town = '';
    } else if (level === 'town') {
      next.town = value;
    } else if (level === 'root') {
      next.province = '';
      next.city = '';
      next.district = '';
      next.town = '';
    }
    setRegion(next);
  };

  const handleSearchSelect = (point) => {
    setRegion({
      province: point.province,
      city: point.city,
      district: point.district,
      town: point.town,
    });
    onSelectPoint?.(point);
    setSearchQuery('');
    setSearchResults([]);
    setSearchOpen(false);
  };

  return (
    <div className="region-navigator">
      <div className="breadcrumb">
        <button
          className={`crumb ${!province ? 'active' : ''}`}
          onClick={() => goto('root')}
        >
          全国
        </button>

        <span className="sep">›</span>
        <select
          className={`crumb-select ${!province ? 'active' : ''}`}
          value={province}
          onChange={e => goto('province', e.target.value)}
        >
          <option value="">选择省份</option>
          {provinces.map(p => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>

        {province && (
          <>
            <span className="sep">›</span>
            <select
              className={`crumb-select ${!city ? 'active' : ''}`}
              value={city}
              onChange={e => goto('city', e.target.value)}
            >
              <option value="">选择城市</option>
              {cities.map(c => (
                <option key={c.city} value={c.city}>{c.city}</option>
              ))}
            </select>
          </>
        )}

        {city && (
          <>
            <span className="sep">›</span>
            <select
              className={`crumb-select ${!district ? 'active' : ''}`}
              value={district}
              onChange={e => goto('district', e.target.value)}
            >
              <option value="">选择区县</option>
              {districts.map(d => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </>
        )}

        {district && (
          <>
            <span className="sep">›</span>
            <select
              className={`crumb-select ${!town ? 'active' : ''}`}
              value={town}
              onChange={e => goto('town', e.target.value)}
            >
              <option value="">全部乡镇/村</option>
              <option value="">全部</option>
            </select>
          </>
        )}
      </div>

      <div className="search-box">
        <input
          type="text"
          placeholder="搜索乡镇、点位名称、蝉种..."
          value={searchQuery}
          onChange={e => { setSearchQuery(e.target.value); setSearchOpen(true); }}
          onFocus={() => setSearchOpen(true)}
          onBlur={() => setTimeout(() => setSearchOpen(false), 200)}
        />
        {searchOpen && (
          <div className="search-dropdown">
            {loading && <div className="search-loading">搜索中...</div>}
            {!loading && searchResults.length === 0 && searchQuery.trim() && (
              <div className="search-empty">无匹配结果</div>
            )}
            {searchResults.map(p => (
              <button
                key={p.id}
                className="search-item"
                onMouseDown={e => e.preventDefault()}
                onClick={() => handleSearchSelect(p)}
              >
                <span className="search-name">{p.name}</span>
                <span className="search-area">
                  {p.province} {p.city} {p.district}{p.town ? ' · ' + p.town : ''}
                </span>
                <span className={`badge badge-${p.abundance}`}>{p.abundance}</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
