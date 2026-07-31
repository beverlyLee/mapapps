"""FastAPI 应用入口。"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import DATA_SOURCE
from app.routers import cicada

app = FastAPI(
    title="捉知了位置标记 API",
    description="北京知了（蝉）聚集位置数据接口，前后端分离，数据源可切换 Excel/数据库。",
    version="1.0.0",
)

# 开发期允许前端 Vite(:5173) 跨域访问；生产可改为具体域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cicada.router)


@app.get("/")
def health():
    return {"status": "ok", "data_source": DATA_SOURCE,
            "message": "捉知了位置标记 API 运行中"}


@app.get("/api/health")
def api_health():
    return health()
