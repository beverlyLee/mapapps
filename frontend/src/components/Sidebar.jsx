import { LEVEL_COLOR, LEVEL_LABELS } from './CicadaMap.jsx';
import {
  IconLeaf, IconBarChart, IconMapPin, IconLayers, IconBug, IconList,
  IconAlert, IconRefresh,
} from './Icons.jsx';

export default function Sidebar({ stats, species, points, loading, error, onRetry, onSelect, onClose }) {
  const levels = stats?.levels || { 高: 0, 中: 0, 低: 0 };
  const byDistrict = stats?.by_district || {};
  const max = Math.max(1, ...Object.values(byDistrict));
  const isEmpty = !loading && !error && points.length === 0;

  return (
    <aside id="sidebar">
      <div className="brand">
        <span className="logo"><IconLeaf width={22} height={22} /></span>
        <h1>捉知了位置标记</h1>
      </div>
      <p className="sub">
        北京知了（蝉）聚集位置 · 高德地图。点位坐标为公园大致中心点（GCJ-02），用于科普 / 演示。
      </p>

      {error && (
        <div className="error" role="alert">
          <IconAlert width={18} height={18} />
          <span>数据加载失败：{error}</span>
          <button className="retry" onClick={onRetry}>
            <IconRefresh width={13} height={13} /> 重试
          </button>
        </div>
      )}

      {/* 数据概览 */}
      <div className="card">
        <h2><IconBarChart width={16} height={16} /> 数据概览</h2>
        {loading ? (
          <>
            <div className="skel line" style={{ width: '70%' }} />
            <div className="skel line" style={{ width: '55%' }} />
            <div className="skel line" style={{ width: '60%' }} />
          </>
        ) : (
          <>
            <div className="stat-row"><span>聚集点位总数</span><span className="v">{stats?.total ?? '—'}</span></div>
            <div className="stat-row"><span>覆盖行政区</span><span className="v">{stats?.districts ?? '—'}</span></div>
            <div className="stat-row"><span>常见鸣蝉种类</span><span className="v">{species.length || '—'}</span></div>
          </>
        )}
      </div>

      {/* 各区聚集密度 */}
      <div className="card">
        <h2><IconMapPin width={16} height={16} /> 各区聚集密度</h2>
        {loading ? (
          [0, 1, 2, 3].map((i) => <div key={i} className="skel block" />)
        ) : Object.keys(byDistrict).length === 0 ? (
          <div className="empty">暂无分区数据</div>
        ) : (
          Object.entries(byDistrict)
            .sort((a, b) => b[1] - a[1])
            .map(([k, v]) => (
              <div key={k}>
                <div className="bar-label"><span>{k}</span><span>{v}</span></div>
                <div className="bar"><i style={{ width: `${(v / max) * 100}%` }} /></div>
              </div>
            ))
        )}
      </div>

      {/* 丰富度分级 */}
      <div className="card">
        <h2><IconLayers width={16} height={16} /> 丰富度分级</h2>
        {['高', '中', '低'].map((lv) => (
          <div className="stat-row" key={lv}>
            <span>
              <span className="legend-dot" style={{ background: LEVEL_COLOR[lv] }} />
              {LEVEL_LABELS[lv]}
            </span>
            <span className="v">{loading ? '·' : (levels[lv] ?? 0)}</span>
          </div>
        ))}
      </div>

      {/* 北京四种常见鸣蝉 */}
      <div className="card">
        <h2><IconBug width={16} height={16} /> 北京常见鸣蝉</h2>
        {loading ? (
          [0, 1, 2, 3].map((i) => <div key={i} className="skel line" style={{ width: '85%' }} />)
        ) : species.length === 0 ? (
          <div className="empty">暂无种类数据</div>
        ) : (
          species.map((s) => (
            <div className="species" key={s.name}>
              <b>{s.name}</b>（{s.alias}）
              <div className="meta">{s.habitat} · 高发 {s.season}</div>
            </div>
          ))
        )}
      </div>

      {/* 点位清单 */}
      <div className="card">
        <h2><IconList width={16} height={16} /> 点位清单（点击飞至）</h2>
        {loading ? (
          [0, 1, 2].map((i) => <div key={i} className="skel block" />)
        ) : isEmpty ? (
          <div className="empty">暂无点位数据，请检查数据源。</div>
        ) : (
          <div id="plist">
            {points.map((p) => (
              <div
                className="item"
                key={p.id}
                role="button"
                tabIndex={0}
                onClick={() => onSelect(p)}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') onSelect(p); }}
              >
                <span className="lv" style={{ background: LEVEL_COLOR[p.abundance] || 'var(--green-500)' }}>
                  {p.abundance}
                </span>
                <div className="nm">{p.name}</div>
                <div className="d">{p.district} · {p.species}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}
