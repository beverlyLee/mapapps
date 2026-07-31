"""Excel -> 数据库 灌库脚本（切换数据源为 db 时使用）。

步骤：
  1. 设置环境变量 DATA_SOURCE=db（及可选的 DATABASE_URL，默认本地 SQLite）
  2. 运行：python seed_db.py
  3. 启动后端即走数据库数据源
"""
from __future__ import annotations

from sqlalchemy import select

from app.data.excel_repository import ExcelCicadaRepository
from app.data.db_repository import DBCicadaRepository, CicadaPointModel
from app.config import DATABASE_URL


def main() -> None:
    excel = ExcelCicadaRepository()
    points = excel.list_points()
    print(f"从 Excel 读取 {len(points)} 条点位，准备写入数据库：{DATABASE_URL}")

    db = DBCicadaRepository()
    # 清空旧表后重新灌入
    with db._session_factory() as s:
        for m in s.scalars(select(CicadaPointModel)).all():
            s.delete(m)
        s.commit()
    for p in points:
        db.add_point(p)
    print(f"灌库完成，数据库现有 {len(db.list_points())} 条点位。")


if __name__ == "__main__":
    main()
