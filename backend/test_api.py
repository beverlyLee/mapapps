"""QA 验证：Excel 路径 + 数据库切换路径。运行：python test_api.py"""
from __future__ import annotations

import os

from sqlalchemy import select

# 默认走 Excel
os.environ.setdefault("DATA_SOURCE", "excel")

from fastapi.testclient import TestClient
from app.main import app
from app.data.excel_repository import ExcelCicadaRepository
from app.data.db_repository import DBCicadaRepository, CicadaPointModel
from app.data import get_repository


def test_excel_path():
    c = TestClient(app)
    assert c.get("/").json()["data_source"] == "excel"
    pts = c.get("/api/cicada/points").json()
    assert len(pts) == 21, f"期望 21 条，实际 {len(pts)}"
    st = c.get("/api/cicada/stats").json()
    assert st["total"] == 21
    assert st["levels"]["高"] == 3, st["levels"]
    assert st["districts"] == 10, st["districts"]
    sp = c.get("/api/cicada/species").json()
    assert len(sp) == 4
    one = c.get("/api/cicada/points/1").json()
    assert one["name"] == "奥林匹克森林公园"
    assert one["is_famous"] is True  # abundance=高 -> is_famous
    assert c.get("/api/cicada/points/999").status_code == 404
    print("✅ Excel 路径：21 点位 / 统计 / 物种 / 详情 / 404 全部通过")


def test_db_switch():
    os.environ["DATA_SOURCE"] = "db"
    excel = ExcelCicadaRepository()
    db = DBCicadaRepository()
    with db._session_factory() as s:
        for m in s.scalars(select(CicadaPointModel)).all():
            s.delete(m)
        s.commit()
    for p in excel.list_points():
        db.add_point(p)

    # 工厂切换验证：配置 db 后返回数据库实现
    repo = get_repository()
    assert isinstance(repo, DBCada := DBCicadaRepository)
    assert len(repo.list_points()) == 21
    # 通过 API（依赖注入会重新取仓库）验证 DB 路径
    c = TestClient(app)
    assert c.get("/api/cicada/points").json().__len__() == 21
    print("✅ 数据库切换路径：工厂返回 DBCicadaRepository，API 经 DB 返回 21 点位")
    os.environ["DATA_SOURCE"] = "excel"  # 还原，避免影响其他流程


if __name__ == "__main__":
    test_excel_path()
    test_db_switch()
    print("\n🎉 全部 QA 用例通过")
