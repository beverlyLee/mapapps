import { LEVEL_COLOR, LEVEL_LABELS } from './CicadaMap.jsx';
import {
  IconLeaf, IconAlert, IconRefresh, IconLocation, IconX, IconBug, IconList,
} from './Icons.jsx';

export default function Sidebar({ stats, species, points, loading, error, onRetry, onSelect, onClose, region, onResetRegion, selected, onClearDetail }) {
  const levels = stats?.levels || { 高: 0, 中: 0, 低: 0 };
  const isEmpty = !loading && !error && points.length === 0;

  const hasRegion = region?.province || region?.city || region?.district;
  const regionLabel = [region?.province, region?.city, region?.district, region?.town]
    .filter(Boolean).join(' › ');

  if (selected) {
    return (
      <aside id="sidebar">
        <div className="brand">
          <span className="logo"><IconLeaf width={20} height={20} /></span>
          <h1>蝉了么</h1>
        </div>
        <DetailView
          point={selected}
          onBack={onClearDetail}
        />
      </aside>
    );
  }

  return (
    <aside id="sidebar">
      <div className="brand">
        <span className="logo"><IconLeaf width={20} height={20} /></span>
        <h1>蝉了么</h1>
      </div>
      <p className="tag">北京知了（蝉）聚集位置 · 抓知了指南</p>

      {error && (
        <div className="error" role="alert">
          <IconAlert width={18} height={18} />
          <span>数据加载失败：{error}</span>
          <button className="retry" onClick={onRetry}>
            <IconRefresh width={13} height={13} /> 重试
          </button>
        </div>
      )}

      {hasRegion && (
        <div className="region-pill">
          <IconLocation width={13} height={13} />
          <span>{regionLabel}</span>
          <button className="reset-btn" onClick={onResetRegion}>返回全部</button>
        </div>
      )}

      <div className="summary">
        <div className="stat"><div className="num">{loading ? '—' : (stats?.total ?? '—')}</div><div className="lbl">聚集点位</div></div>
        <div className="stat"><div className="num">{loading ? '—' : (stats?.districts ?? '—')}</div><div className="lbl">覆盖区县</div></div>
        <div className="stat"><div className="num">{loading ? '—' : species.length}</div><div className="lbl">常见种类</div></div>
      </div>

      <h3 className="section-title">点位清单（点击查看详情）</h3>
      {loading ? (
        [0, 1, 2, 3].map((i) => <div key={i} className="skel block" />)
      ) : isEmpty ? (
        <div className="empty">暂无点位数据，请检查数据源。</div>
      ) : (
        <div id="plist">
          {points.map((p) => (
            <button
              className="item"
              key={p.id}
              onClick={() => onSelect(p)}
            >
              <span className="dot" style={{ background: LEVEL_COLOR[p.abundance] || 'var(--accent)' }} />
              <div className="nm">{p.name}</div>
              <div className="d">
                {[p.district, p.town].filter(Boolean).join(' · ') || p.city} · {p.species}
              </div>
            </button>
          ))}
        </div>
      )}

      {!loading && species.length > 0 && (
        <details className="species-fold">
          <summary><IconBug width={14} height={14} /> 常见鸣蝉</summary>
          {species.map((s) => (
            <div className="species" key={s.name}>
              <b>{s.name}</b>（{s.alias}）
              <div className="meta">{s.habitat} · 高发 {s.season}</div>
            </div>
          ))}
        </details>
      )}
    </aside>
  );
}

function DetailView({ point, onBack }) {
  const p = point;
  return (
    <div className="detail">
      <button className="back" onClick={onBack}>
        <IconList width={15} height={15} /> 返回列表
      </button>

      {p.image_url && (
        <img
          className="photo"
          src={p.image_url}
          alt={p.name}
          loading="lazy"
          onError={(e) => { e.currentTarget.style.display = 'none'; }}
        />
      )}

      <h2 className="name">{p.name}</h2>
      <div className="tags">
        <span className="lv" style={{ background: LEVEL_COLOR[p.abundance] || 'var(--accent)' }}>
          {LEVEL_LABELS[p.abundance] || p.abundance}
        </span>
        <span className="sp">{p.species}</span>
      </div>
      <div className="region-line">
        {[p.province, p.city, p.district, p.town].filter(Boolean).join(' › ')}
        {p.peak_season ? ` · 高发期 ${p.peak_season}` : ''}
      </div>
      {p.detail && <p className="text">{p.detail}</p>}
    </div>
  );
}
