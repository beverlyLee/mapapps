"""Pydantic 数据模型。"""
from __future__ import annotations

from pydantic import BaseModel


class CicadaPoint(BaseModel):
    id: int
    name: str
    province: str = "北京市"
    city: str = "北京市"
    district: str = ""
    town: str = ""
    lng: float
    lat: float
    species: str = ""
    peak_season: str = ""
    abundance: str = "中"
    is_famous: bool = False
    detail: str = ""
    image_url: str = ""

    @classmethod
    def from_row(cls, row: dict) -> "CicadaPoint":
        abundance = str(row.get("abundance") or "中").strip() or "中"
        is_famous = row.get("is_famous")
        if is_famous is None:
            is_famous = abundance == "高"
        else:
            is_famous = bool(is_famous) if not isinstance(is_famous, bool) \
                else is_famous
        return cls(
            id=int(row.get("id")),
            name=str(row.get("name") or ""),
            province=str(row.get("province") or "北京市"),
            city=str(row.get("city") or row.get("province") or "北京市"),
            district=str(row.get("district") or ""),
            town=str(row.get("town") or ""),
            lng=float(row.get("lng")),
            lat=float(row.get("lat")),
            species=str(row.get("species") or ""),
            peak_season=str(row.get("peak_season") or ""),
            abundance=abundance,
            is_famous=is_famous,
            detail=str(row.get("detail") or ""),
            image_url=str(row.get("image_url") or ""),
        )


class SpeciesInfo(BaseModel):
    name: str
    alias: str = ""
    habitat: str = ""
    season: str = ""


class CicadaStats(BaseModel):
    total: int
    districts: int
    levels: dict[str, int]
    by_district: dict[str, int]


class DistrictStats(BaseModel):
    total: int
    levels: dict[str, int]
    by_town: dict[str, int] = {}


class RegionNode(BaseModel):
    province: str
    cities: list["CityNode"] = []


class CityNode(BaseModel):
    city: str
    districts: list[str] = []


RegionNode.model_rebuild()


class SearchResult(BaseModel):
    points: list[CicadaPoint]
    total: int
