"""Pydantic 数据模型。"""
from __future__ import annotations

from pydantic import BaseModel


class CicadaPoint(BaseModel):
    id: int
    name: str
    district: str
    lng: float
    lat: float
    species: str = ""
    peak_season: str = ""
    abundance: str = "中"          # 高 / 中 / 低
    is_famous: bool = False         # 是否知名聚集区（= abundance == "高"）

    @classmethod
    def from_row(cls, row: dict) -> "CicadaPoint":
        """从 Excel / DB 行字典构造，兼容字段名差异与类型。"""
        abundance = str(row.get("abundance") or "中").strip() or "中"
        is_famous = row.get("is_famous")
        if is_famous is None:
            is_famous = abundance == "高"
        else:
            is_famous = bool(is_famous)
        return cls(
            id=int(row.get("id")),
            name=str(row.get("name") or ""),
            district=str(row.get("district") or ""),
            lng=float(row.get("lng")),
            lat=float(row.get("lat")),
            species=str(row.get("species") or ""),
            peak_season=str(row.get("peak_season") or ""),
            abundance=abundance,
            is_famous=is_famous,
        )


class SpeciesInfo(BaseModel):
    name: str
    alias: str = ""
    habitat: str = ""
    season: str = ""


class CicadaStats(BaseModel):
    total: int
    districts: int
    levels: dict[str, int]          # {"高": n, "中": n, "低": n}
    by_district: dict[str, int]     # {区: 数量}
