"""数据库数据源实现（SQLAlchemy 2.0，可切换）。

默认未启用；当 config.DATA_SOURCE == "db" 时由工厂返回本实现。
切换步骤见 backend/README.md：配置 DATABASE_URL -> 运行 seed_db.py 灌库 -> 启动。
业务层（路由/前端）无需任何改动。
"""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import (Column, Float, Boolean, Integer, String, create_engine,
                        select)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import DATABASE_URL
from app.data.repository import CicadaRepository
from app.schemas import CicadaPoint, CicadaStats, SpeciesInfo

# 与 Excel 仓库共用物种说明
_SPECIES = [
    SpeciesInfo(name="黑蚱蝉", alias="麻季鸟儿", habitat="城区最常见，体型最大全黑", season="6–8月"),
    SpeciesInfo(name="蒙古寒蝉", alias="伏天儿", habitat="山区偏多，偏绿", season="7–9月"),
    SpeciesInfo(name="鸣鸣蝉", alias="斑透翅蝉", habitat="山区，蓝绿纹", season="8月集中"),
    SpeciesInfo(name="蟪蛄", alias="小热热儿", habitat="最小，树皮伪装", season="5月最早"),
]


class Base(DeclarativeBase):
    pass


class CicadaPointModel(Base):
    __tablename__ = "cicada_points"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    district = Column(String(64), nullable=False)
    lng = Column(Float, nullable=False)
    lat = Column(Float, nullable=False)
    species = Column(String(255), default="")
    peak_season = Column(String(64), default="")
    abundance = Column(String(8), default="中")
    is_famous = Column(Boolean, default=False)


class DBCicadaRepository(CicadaRepository):
    def __init__(self, url: str = DATABASE_URL):
        self._engine = create_engine(url, future=True)
        # 自动建表（首次运行创建；已存在则忽略）
        Base.metadata.create_all(self._engine)
        self._session_factory = sessionmaker(bind=self._engine, future=True)

    def _to_schema(self, m: CicadaPointModel) -> CicadaPoint:
        return CicadaPoint(
            id=m.id, name=m.name, district=m.district, lng=m.lng, lat=m.lat,
            species=m.species or "", peak_season=m.peak_season or "",
            abundance=m.abundance or "中", is_famous=bool(m.is_famous),
        )

    def _rows(self, session: Session) -> List[CicadaPointModel]:
        return list(session.scalars(select(CicadaPointModel)).all())

    def list_points(self) -> List[CicadaPoint]:
        with self._session_factory() as s:
            return [self._to_schema(m) for m in self._rows(s)]

    def get_point(self, point_id: int) -> Optional[CicadaPoint]:
        with self._session_factory() as s:
            m = s.get(CicadaPointModel, point_id)
            return self._to_schema(m) if m else None

    def list_species(self) -> List[SpeciesInfo]:
        return _SPECIES

    def get_stats(self) -> CicadaStats:
        with self._session_factory() as s:
            models = self._rows(s)
        levels = {"高": 0, "中": 0, "低": 0}
        by_district: dict[str, int] = {}
        for m in models:
            levels[m.abundance or "中"] = levels.get(m.abundance or "中", 0) + 1
            by_district[m.district] = by_district.get(m.district, 0) + 1
        return CicadaStats(
            total=len(models),
            districts=len(by_district),
            levels=levels,
            by_district=by_district,
        )

    # ---- 写库接口（Excel 实现不支持，这里完整实现）----
    def add_point(self, point: CicadaPoint) -> CicadaPoint:
        with self._session_factory() as s:
            m = CicadaPointModel(**point.model_dump())
            s.add(m)
            s.commit()
            s.refresh(m)
            return self._to_schema(m)

    def update_point(self, point_id: int, point: CicadaPoint) -> Optional[CicadaPoint]:
        with self._session_factory() as s:
            m = s.get(CicadaPointModel, point_id)
            if not m:
                return None
            for k, v in point.model_dump().items():
                setattr(m, k, v)
            s.commit()
            s.refresh(m)
            return self._to_schema(m)

    def delete_point(self, point_id: int) -> bool:
        with self._session_factory() as s:
            m = s.get(CicadaPointModel, point_id)
            if not m:
                return False
            s.delete(m)
            s.commit()
            return True
