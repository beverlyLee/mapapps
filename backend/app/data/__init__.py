"""数据仓库工厂：依据配置返回 Excel 或 数据库 实现。

注意：在调用时读取环境变量（而非模块导入时），
便于运行时切换数据源，业务代码零改动。
"""
from __future__ import annotations

import os

from app.data.repository import CicadaRepository


def get_repository() -> CicadaRepository:
    source = os.getenv("DATA_SOURCE", "excel").lower()
    if source == "db":
        from app.data.db_repository import DBCicadaRepository
        return DBCicadaRepository()
    from app.data.excel_repository import ExcelCicadaRepository
    return ExcelCicadaRepository()
