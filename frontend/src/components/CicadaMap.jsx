import { useEffect, useRef, useState } from 'react';
import { IconLayers } from './Icons.jsx';

const KEY = import.meta.env.VITE_AMAP_KEY;
const SECURITY = import.meta.env.VITE_AMAP_SECURITY;

export const LEVEL_COLOR = { 高: '#e5484d', 中: '#f59e0b', 低: '#5bbf7a' };
export const LEVEL_LABELS = { 高: '高', 中: '中', 低: '低' };

const DEFAULT_CENTER = [116.4, 39.95];

let amapPromise = null;
function loadAMap() {
  if (typeof window !== 'undefined' && window.AMap) return Promise.resolve(window.AMap);
  if (amapPromise) return amapPromise;
  amapPromise = new Promise((resolve, reject) => {
    if (SECURITY) window._AMapSecurityConfig = { securityJsCode: SECURITY };
    const s = document.createElement('script');
    s.src = `https://webapi.amap.com/maps?v=2.0&key=${KEY}`;
    s.async = true;
    s.onload = () => (window.AMap ? resolve(window.AMap) : reject(new Error('AMap 未就绪')));
    s.onerror = () => reject(new Error('高德脚本加载失败（请检查 Key 与网络）'));
    document.head.appendChild(s);
  });
  return amapPromise;
}

const NO_KEY_HINT = (
  <div className="amap-hint">
    未配置高德地图 Key。请在 <code>frontend/.env</code> 设置 <code>VITE_AMAP_KEY</code> 与
    <code>VITE_AMAP_SECURITY</code>（参考 <code>.env.example</code>），重启 dev 即可显示地图。
  </div>
);

export default function CicadaMap({ points, region, onReady, onSelectPoint }) {
  const elRef = useRef(null);
  const mapRef = useRef(null);
  const clusterRef = useRef(null);
  const boundaryRef = useRef(null);
  const districtSearchRef = useRef(null);
  const onReadyRef = useRef(onReady);
  const onSelectRef = useRef(onSelectPoint);
  const regionRef = useRef(region);
  const [ready, setReady] = useState(false);
  const [mapErr, setMapErr] = useState(null);

  useEffect(() => { onReadyRef.current = onReady; }, [onReady]);
  useEffect(() => { onSelectRef.current = onSelectPoint; }, [onSelectPoint]);
  useEffect(() => { regionRef.current = region; }, [region]);

  useEffect(() => {
    let cancelled = false;
    if (!KEY) return;
    loadAMap()
      .then((AMap) => {
        if (cancelled || !elRef.current) return;
        const map = new AMap.Map(elRef.current, {
          zoom: 10,
          center: DEFAULT_CENTER,
          mapStyle: 'amap://styles/normal',
        });
        mapRef.current = map;
        setReady(true);
        onReadyRef.current &&
          onReadyRef.current({
            flyTo: (p) => map.setZoomAndCenter(15, [p.lng, p.lat]),
          });
      })
      .catch((e) => { if (!cancelled) setMapErr(e.message); });
    return () => {
      cancelled = true;
      if (mapRef.current) { mapRef.current.destroy(); mapRef.current = null; }
    };
  }, []);

  useEffect(() => {
    if (!ready || !window.AMap || !mapRef.current) return;
    const AMap = window.AMap;
    if (clusterRef.current) { clusterRef.current.setMap(null); clusterRef.current = null; }
    const data = points.map((p) => ({ lnglat: [p.lng, p.lat], point: p }));
    AMap.plugin(['AMap.MarkerCluster'], () => {
      clusterRef.current = new AMap.MarkerCluster(mapRef.current, data, {
        gridSize: 60,
        renderMarker(ctx) {
          const m = ctx.marker;
          if (ctx.count > 1) {
            m.setContent(`<div class="cluster">${ctx.count}</div>`);
            m.setOffset(new AMap.Pixel(-19, -19));
          } else {
            const d = ctx.data[0].point;
            const cls = d.abundance === '高' ? 'high' : d.abundance === '中' ? 'mid' : 'low';
            m.setContent(`<div class="cicada-marker ${cls}" title="${d.name}"></div>`);
            m.setOffset(new AMap.Pixel(-9, -9));
            m.on('click', () => onSelectRef.current && onSelectRef.current(d));
          }
        },
      });
    });
  }, [ready, points]);

  useEffect(() => {
    if (!ready || !window.AMap || !mapRef.current) return;
    const { province, city, district } = region || {};
    const AMap = window.AMap;
    const map = mapRef.current;

    if (!province && !city && !district) {
      if (boundaryRef.current) { map.remove(boundaryRef.current); boundaryRef.current = null; }
      districtSearchRef.current = null;
      map.setZoomAndCenter(10, DEFAULT_CENTER);
      return;
    }

    const areaName = [province, city, district].filter(Boolean).join('');
    if (!areaName) return;

    if (districtSearchRef.current) { districtSearchRef.current.search(areaName); return; }

    AMap.plugin(['AMap.DistrictSearch'], () => {
      districtSearchRef.current = new AMap.DistrictSearch({
        level: district ? 'district' : city ? 'city' : 'province',
        subdistrict: 0,
        extensions: 'all',
      });
      districtSearchRef.current.search(areaName, (status, result) => {
        if (status !== 'complete' || !result?.districtList?.length) return;
        const bounds = result.districtList[0].boundaries;
        if (boundaryRef.current) { map.remove(boundaryRef.current); boundaryRef.current = null; }
        if (bounds && bounds.length > 0) {
          boundaryRef.current = new AMap.Polygon(bounds, {
            strokeColor: '#1f8a5b',
            strokeWeight: 2,
            fillColor: '#1f8a5b',
            fillOpacity: 0.1,
          });
          boundaryRef.current.setMap(map);
          map.setFitView([boundaryRef.current]);
        }
      });
    });
  }, [ready, region]);

  return (
    <>
      <div id="map" ref={elRef} />
      {!KEY && NO_KEY_HINT}
      {KEY && !ready && !mapErr && (
        <div className="map-loading"><div className="ring" />地图加载中…</div>
      )}
      {mapErr && <div className="amap-hint">⚠️ {mapErr}</div>}
      {ready && points.length > 0 && (
        <div className="map-legend">
          <div className="ttl"><IconLayers width={14} height={14} /> 丰富度</div>
          {['高', '中', '低'].map((lv) => (
            <div className="row" key={lv}>
              <span className="dot" style={{ background: LEVEL_COLOR[lv] }} />
              {LEVEL_LABELS[lv]}
            </div>
          ))}
        </div>
      )}
    </>
  );
}
