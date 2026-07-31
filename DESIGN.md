# 捉知了位置标记网站 · 设计文档（PRD + 架构）

> 交付总监（齐活林）整理：本文件同时承担**产品需求（PRD）**与**系统架构设计**两个 SOP 阶段产物。

## 一、产品需求（PRD）

### 1.1 目标
做一个**前后端分离**的网站，在**高德地图**上标记「捉知了（蝉）聚集位置」，帮助用户在夏季快速找到知了高产区。

### 1.2 用户故事
- 作为捉知了爱好者，我想在地图上看到各公园/聚集区的位置与丰富度，以便规划夜捕路线。
- 作为运营者，我想通过统一的数据接口管理点位，便于以后从 Excel 平滑切换到数据库。

### 1.3 需求池
| 优先级 | 需求 | 说明 |
|---|---|---|
| P0 | 地图标注聚集点位（高德） | 聚类 + 彩色分级圆点（红高/橙中/绿低） |
| P0 | 点位列表 / 详情 API | GET /api/cicada/points, /points/{id} |
| P0 | 统计 API | 总数、覆盖区、丰富度分级、物种 |
| P0 | Excel 数据源（首版） | openpyxl 读取 backend/data/cicada_points.xlsx |
| P1 | 可切换数据库接口 | 仓库抽象 + SQLAlchemy 实现 + 工厂切换 |
| P1 | 左侧数据分析面板 | 各区密度、丰富度、物种、时间线 |
| P2 | 点击点位飞至 + 信息窗 | 地图交互 |

### 1.4 数据与地图合规
- 坐标为各公园**大致中心点（GCJ-02）**，非精确普查，仅用于科普/演示。
- 高德地图 API Key 由用户自行申请，走环境变量，**不硬编码**。

## 二、系统架构

### 2.1 技术栈
- **后端**：Python 3.12+ / FastAPI + Uvicorn；数据读取 openpyxl；未来 DB 用 SQLAlchemy 2.0。
- **前端**：React 18 + Vite + 原生 AMap JS API 2.0（动态加载，Key 走 env）。
- **分离方式**：前端独立构建（Vite dev server :5173，代理 `/api` → 后端 :8000）；生产可各自部署。

### 2.2 目录与文件清单
```
cicada-map/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py            # 数据源开关 + 路径/Key
│   │   ├── schemas.py           # Pydantic 模型
│   │   ├── data/
│   │   │   ├── __init__.py      # get_repository() 工厂
│   │   │   ├── repository.py    # CicadaRepository(ABC) 抽象接口
│   │   │   ├── excel_repository.py  # Excel 实现（首版）
│   │   │   └── db_repository.py # SQLAlchemy 实现（占位可切换）
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── cicada.py        # REST 路由
│   │   └── main.py              # FastAPI 应用入口 + CORS
│   ├── data/
│   │   └── cicada_points.xlsx   # 数据源（21 点）
│   ├── seed_db.py               # Excel → 数据库 灌库脚本（切换用）
│   ├── requirements.txt
│   └── README.md
└── frontend/
    ├── package.json
    ├── vite.config.js           # /api 代理到 :8000
    ├── index.html
    ├── .env.example             # VITE_AMAP_KEY / VITE_AMAP_SECURITY
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── api.js               # 封装 fetch
        ├── styles.css
        └── components/
            ├── CicadaMap.jsx    # 高德地图 + 聚类 + 信息窗
            └── Sidebar.jsx      # 统计 / 物种 / 点位清单
```

### 2.3 数据模型（Excel 列 = DB 表字段）
| 字段 | 类型 | 说明 |
|---|---|---|
| id | int | 主键 |
| name | str | 公园/聚集区名称 |
| district | str | 行政区 |
| lng | float | 经度 (GCJ-02) |
| lat | float | 纬度 (GCJ-02) |
| species | str | 常见蝉种类（逗号分隔） |
| peak_season | str | 高发期 |
| abundance | str | 高/中/低 |
| is_famous | bool | 是否知名聚集区（= abundance=='高'） |

### 2.4 接口契约
- `GET /api/cicada/points` → `List[CicadaPoint]`
- `GET /api/cicada/points/{id}` → `CicadaPoint`
- `GET /api/cicada/stats` → `{ total, districts, levels:{高,中,低}, by_district:{} }`
- `GET /api/cicada/species` → `List[SpeciesInfo]`

### 2.5 数据源切换设计（核心）
```
CicadaRepository(ABC)
   ├── ExcelCicadaRepository   (默认，读 xlsx)
   └── DBCicadaRepository      (SQLAlchemy，读数据库)
get_repository() 工厂依据 settings.DATA_SOURCE 返回实例
```
切换步骤：改 `DATA_SOURCE=db` + 配置 `DATABASE_URL` + 运行 `python seed_db.py` 灌库即可，业务代码零改动。

### 2.6 依赖关系
`routers → repository 工厂 → (excel | db) 实现 → schemas`；前端 `api.js → /api → routers`。
