# 捉知了位置标记网站（前后端分离）

在**高德地图**上标记北京「捉知了（蝉）」聚集位置。**后端 Python / FastAPI** 首版用 **Excel** 作数据源，
并通过仓库抽象**预留可切换的数据库接口**；**前端 React + Vite** 独立构建，开发期由 Vite 代理 `/api` 联调。

## 技术架构（前后端分离）
```
浏览器 ──> React 前端 (:5173) ──/api 代理──> FastAPI 后端 (:8000) ──> 数据仓库(Excel / DB)
               高德 JS API 2.0 渲染地图                  │
                                            CicadaRepository(ABC)
                                            ├── ExcelCicadaRepository  (openpyxl)
                                            └── DBCicadaRepository     (SQLAlchemy 2.0)
                                            get_repository() 按 DATA_SOURCE 运行时切换
```
业务代码对数据源无感知：切 Excel / DB 只改环境变量，**路由与前端零改动**。

## 目录
```
cicada-map/
├── backend/            # FastAPI：Excel 数据源 + 数据库接口
│   ├── app/            # 配置 / schema / routers / data(仓库抽象)
│   ├── data/cicada_points.xlsx   # 首版数据源（21 个北京点位）
│   ├── gen_excel.py    # 生成示例 Excel（含 21 条种子）
│   ├── seed_db.py      # 把 Excel 灌入数据库
│   ├── test_api.py     # QA：Excel 路径 + 数据库切换路径
│   └── requirements.txt
├── frontend/           # React + Vite + 高德地图 JS API
│   ├── src/components/ # CicadaMap.jsx / Sidebar.jsx / Icons.jsx
│   ├── src/styles.css  # 设计系统（Organic Biophilic + Bento Grid）
│   ├── .env.example    # 高德 Key 占位
│   └── vite.config.js  # /api 代理到 :8000
└── DESIGN.md           # PRD + 架构设计
```

---

## 1. 运行方法（本机已验证）

### 1.1 启动后端（:8000）
```bash
cd cicada-map/backend

# 依赖已在本工作区的受管 venv 中装好；若换机器：
#   python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
# 本机直接用已装好的解释器（示例路径，按实际调整）：
#   /Users/liboyang/.workbuddy/binaries/python/envs/default/bin/python -m uvicorn app.main:app --port 8000

uvicorn app.main:app --reload --port 8000
# 健康检查： http://localhost:8000/api/health
# 接口文档： http://localhost:8000/docs
```
> 首次运行若缺少 `data/cicada_points.xlsx`，先执行 `python gen_excel.py`。

### 1.2 配置高德地图 Key（前端必须）
地图需要高德 Web 端(JS API) 密钥，自行到 https://lbs.amap.com/ 免费申请：
```bash
cd cicada-map/frontend
cp .env.example .env
# 编辑 .env 填入：
#   VITE_AMAP_KEY=你的_web端_js_key
#   VITE_AMAP_SECURITY=你的_安全密钥
```
未配置 Key 时前端会显示提示卡片（不影响其余数据面板），配置后重启 dev 即出地图。

### 1.3 启动前端（:5173）
```bash
cd cicada-map/frontend
npm install            # 首次
npm run dev            # http://localhost:5173
```
开发期 Vite 自动把 `/api` 代理到 `:8000`，前后端分离联调开箱即用。
生产构建：`npm run build`，产物在 `dist/`，可托管到任意静态服务器（独立部署后端时改 `vite.config.js` 的 proxy 指向真实域名）。

### 1.4 打开使用
浏览器访问 **http://localhost:5173** → 左侧数据面板（概览 / 各区密度 / 丰富度分级 / 鸣蝉种类 / 点位清单），
右侧高德地图标记聚集点（按丰富度红/黄/绿着色，聚合显示数量）。点击左侧任一点位，地图平滑飞至并弹出信息窗。
**窄屏（≤860px）** 自动切换为抽屉式列表，右下角「点位列表」按钮开合。

---

## 2. 接口一览
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/cicada/points` | 全部点位（21 条） |
| GET | `/api/cicada/points/{id}` | 单点详情（不存在返回 404） |
| GET | `/api/cicada/stats` | 统计：总数 / 行政区数 / 分级 / 各区密度 |
| GET | `/api/cicada/species` | 北京四种常见鸣蝉 |
| GET | `/api/health` | 健康检查（含当前 data_source） |

## 3. 切换到数据库（之后）
```bash
cd cicada-map/backend
export DATA_SOURCE=db
# 默认本地 SQLite（data/cicada.db）；也可指定：
#   export DATABASE_URL="postgresql+psycopg://user:pwd@host:5432/cicada"
python seed_db.py        # 把 Excel 数据灌入数据库（幂等清空重写）
# 重启 uvicorn —— 路由与前端零改动
```
`DBCicadaRepository` 已用 SQLAlchemy 2.0 实现 `list/get/stats` 及写库 `add/update/delete`，
表结构由 `Base.metadata.create_all` 自动创建。

---

## 4. 前端设计说明（本轮 redesign）
- **设计系统**：Organic Biophilic + Bento Grid（圆角 16px、自然绿主色、柔和阴影、留白）。
- **图标**：改用 Lucide 风格 SVG（描边、24×24、currentColor），移除全部 emoji 图标。
- **状态全覆盖**：骨架屏（加载中）、空态、错误条 + 重试按钮；地图区有加载遮罩与无 Key 提示。
- **地图增强**：丰富度图例浮层、高丰富度点位脉冲动效、聚合点悬停放大。
- **响应式**：≤860px 切换为抽屉式列表（带遮罩），地图全屏；`prefers-reduced-motion` 已尊重。
- **可访问性**：交互元素 `cursor:pointer` + 焦点环、色彩非唯一指示（文字+色块）、对比度达标。

## 5. 验收结果（本轮）
| 项 | 结果 |
|----|------|
| 后端 QA（Excel 路径 21 点位 / 统计 / 物种 / 详情 / 404） | ✅ 通过 |
| 数据库切换路径（工厂返回 DBCicadaRepository，API 经 DB 返回 21 点位） | ✅ 通过 |
| 前端生产构建（`vite build`，31 模块） | ✅ 无错误 |
| 本地联调：后端 :8000 健康 + 数据 | ✅ 200 / 21 条 |
| 前端 :5173 服务 + 经 Vite 代理取数 | ✅ 200 / stats 透传成功 |
| DB 模式实时实例（:8001，data_source=db） | ✅ 21 条 |

## 6. 数据说明
点位依据公开报道与昆虫科普资料整理，坐标为各公园大致中心点（GCJ-02），用于科普 / 演示，非精确普查。
