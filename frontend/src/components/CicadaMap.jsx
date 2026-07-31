import { useEffect, useRef, useState } from 'react';
import { IconLayers } from './Icons.jsx';

const KEY = import.meta.env.VITE_AMAP_KEY;
const SECURITY = import.meta.env.VITE_AMAP_SECURITY;

// 丰富度分级色（与 styles.css 变量保持一致）
export const LEVEL_COLOR = { 高: '#e5484d', 中: '#f59e0b', 低: '#6bbf59' };
export const LEVEL_LABELS = { 高: '高 · 知名聚集区', 中: '中 · 稳定栖息', 低: '低 · 城区点缀' };

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

function infoHTML(d) {
  const c = LEVEL_COLOR[d.abundance] || '#f59e0b';
  return `<div style="min-width:220px;font:13px/1.65 'PingFang SC','Microsoft YaHei',sans-serif;color:#2c3e33">
    <div style="font-size:15px;font-weight:700;color:${c}">${d.name}</div>
    <div style="color:#5c7268;margin:2px 0 8px">${d.district} · 丰富度 <b style="color:${c}">${d.abundance}</b></div>
    <div>常见种类：${d.species || '—'}</div>
    <div>高发期：${d.peak_season || '—'}</div>
  </div>`;
}

const NO_KEY_HINT = (
  <div className="amap-hint">
    未配置高德地图 Key。请在 <code>frontend/.env</code> 设置 <code>VITE_AMAP_KEY</code> 与
    <code>VITE_AMAP_SECURITY</code>（参考 <code>.env.example</code>），重启 dev 即可显示地图。
  </div>
);

export default function CicadaMap({ points, onReady }) {
  const elRef = useRef(null);
  const mapRef = useRef(null);
  const infoRef = useRef(null);
  const clusterRef = useRef(null);
  const onReadyRef = useRef(onReady);
  const [ready, setReady] = useState(false);
  const [mapErr, setMapErr] = useState(null);

  useEffect(() => { onReadyRef.current = onReady; }, [onReady]);

  // 初始化地图（仅一次）
  useEffect(() => {
    let cancelled = false;
    if (!KEY) return; // 无 Key 由外部提示
    loadAMap()
      .then((AMap) => {
        if (cancelled || !elRef.current) return;
        const map = new AMap.Map(elRef.current, {
          zoom: 10,
          center: [116.4, 39.95],
          mapStyle: 'amap://styles/normal',
        });
        const info = new AMap.InfoWindow({ offset: new AMap.Pixel(0, -12) });
        mapRef.current = map;
        infoRef.current = info;
        setReady(true);
        onReadyRef.current &&
          onReadyRef.current({
            flyTo: (p) => {
              map.setZoomAndCenter(15, [p.lng, p.lat]);
              info.setContent(infoHTML(p));
              info.open(map, [p.lng, p.lat]);
            },
          });
      })
      .catch((e) => { if (!cancelled) setMapErr(e.message); });
    return () => {
      cancelled = true;
      if (mapRef.current) { mapRef.current.destroy(); mapRef.current = null; }
    };
  }, []);

  // 点位变化 -> 重建聚类
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
            m.setOffset(new AMap.Pixel(-20, -20));
          } else {
            const d = ctx.data[0].point;
            const cls = d.abundance === '高' ? 'high' : d.abundance === '中' ? 'mid' : 'low';
            m.setContent(`<div class="cicada-marker ${cls}" title="${d.name}"></div>`);
            m.setOffset(new AMap.Pixel(-11, -11));
            m.on('click', () => {
              infoRef.current.setContent(infoHTML(d));
              infoRef.current.open(mapRef.current, m.getPosition());
            });
          }
        },
      });
    });
  }, [ready, points]);

  return (
    <>
      <div id="map" ref={elRef} />
      {!KEY && NO_KEY_HINT}
      {KEY && !ready && !mapErr && (
        <div className="map-loading">
          <div className="ring" />
          地图加载中…
        </div>
      )}
      {mapErr && <div className="amap-hint">⚠️ {mapErr}</div>}
      {ready && points.length > 0 && (
        <div className="map-legend">
          <div className="ttl"><IconLayers width={14} height={14} /> 丰富度图例</div>
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
