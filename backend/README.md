# 后端（Python · FastAPI）

捉知了位置标记网站的服务端：提供点位 / 统计 / 物种 API，**首版数据源为 Excel**，并预留**可切换的数据库接口**。

## 快速开始

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # 或用受管 venv
pip install -r requirements.txt

# 生成 Excel 数据源（首次）
python gen_excel.py

# 启动
uvicorn app.main:app --reload --port 8000
```

- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/health

## 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/cicada/points` | 全部点位 |
| GET | `/api/cicada/points/{id}` | 单点位详情 |
| GET | `/api/cicada/stats` | 统计（总数/区/丰富度分级） |
| GET | `/api/cicada/species` | 四种常见鸣蝉说明 |

## 从 Excel 切换到数据库

数据层已抽象为 `CicadaRepository`，切换**零改动业务代码**：

1. 配置环境变量（或改 `app/config.py`）：
   ```bash
   export DATA_SOURCE=db
   export DATABASE_URL="postgresql+psycopg://user:pwd@host:5432/cicada"  # 默认本地 SQLite
   ```
2. 灌库（把 Excel 数据写进数据库）：
   ```bash
   python seed_db.py
   ```
3. 重启 `uvicorn` 即可——路由与前端无需任何修改。

> 数据库实现位于 `app/data/db_repository.py`（SQLAlchemy 2.0，已含建表与增删改接口）。
