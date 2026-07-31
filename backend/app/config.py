"""应用配置：数据源开关、路径、地图 Key。"""
from __future__ import annotations

import os
from pathlib import Path

# backend/ 目录
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# ---- 数据源切换开关 ----
# "excel" -> 读取 Excel（首版）；"db" -> 读取数据库（需先 seed_db.py 灌库）
DATA_SOURCE = os.getenv("DATA_SOURCE", "excel").lower()

EXCEL_FILE = os.getenv("CICADA_EXCEL", str(DATA_DIR / "cicada_points.xlsx"))

# 数据库（切换为 db 时使用）。默认本地 SQLite，可改为 postgresql+psycopg://...
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'cicada.db'}")

# 高德地图 Key（也可在前端 .env 配置；此处供需要服务端透传时使用）
AMAP_KEY = os.getenv("AMAP_KEY", "")
AMAP_SECURITY = os.getenv("AMAP_SECURITY", "")
