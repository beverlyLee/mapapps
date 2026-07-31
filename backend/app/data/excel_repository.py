"""Excel 数据源实现。

使用 openpyxl 读取 backend/data/cicada_points.xlsx，
按文件修改时间（mtime）缓存：Excel 保存变更后，下次请求自动热加载。
"""
from __future__ import annotations

import os
from typing import List, Optional

from openpyxl import load_workbook

from app.config import EXCEL_FILE
from app.data.repository import CicadaRepository
from app.schemas import (
    CityNode, CicadaPoint, CicadaStats, DistrictStats,
    RegionNode, SearchResult, SpeciesInfo,
)

_SPECIES = [
    SpeciesInfo(name="黑蚱蝉", alias="麻季鸟儿", habitat="城区最常见，体型最大全黑", season="6–8月"),
    SpeciesInfo(name="蒙古寒蝉", alias="伏天儿", habitat="山区偏多，偏绿", season="7–9月"),
    SpeciesInfo(name="鸣鸣蝉", alias="斑透翅蝉", habitat="山区，蓝绿纹", season="8月集中"),
    SpeciesInfo(name="蟪蛄", alias="小热热儿", habitat="最小，树皮伪装", season="5月最早"),
]


class ExcelCicadaRepository(CicadaRepository):
    _cache: Optional[List[CicadaPoint]] = None
    _cache_mtime: float = 0.0
    _cache_path: Optional[str] = None

    def __init__(self, path: str = EXCEL_FILE):
        self._path = path

    @classmethod
    def _clear_cache(cls):
        cls._cache = None
        cls._cache_mtime = 0.0
        cls._cache_path = None

    def _load(self) -> List[CicadaPoint]:
        current_mtime = 0.0
        try:
            st = os.stat(self._path)
            current_mtime = st.st_mtime
        except FileNotFoundError:
            return []

        cached = (
            ExcelCicadaRepository._cache is not None
            and ExcelCicadaRepository._cache_path == self._path
            and ExcelCicadaRepository._cache_mtime == current_mtime
        )
        if cached:
            return ExcelCicadaRepository._cache  # type: ignore[return-value]

        wb = load_workbook(self._path, read_only=True, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        wb.close()
        points: List[CicadaPoint] = []
        if rows:
            header = [str(h).strip() if h is not None else "" for h in rows[0]]
            for raw in rows[1:]:
                if raw is None or all(c is None for c in raw):
                    continue
                row = {header[i]: raw[i] for i in range(min(len(header), len(raw)))}
                if row.get("id") in (None, "") or row.get("lng") in (None, ""):
                    continue
                points.append(CicadaPoint.from_row(row))

        ExcelCicadaRepository._cache = points
        ExcelCicadaRepository._cache_mtime = current_mtime
        ExcelCicadaRepository._cache_path = self._path
        return points

    # ---------- 基础 CRUD ----------
    def list_points(self) -> List[CicadaPoint]:
        return self._load()

    def get_point(self, point_id: int) -> Optional[CicadaPoint]:
        for p in self._load():
            if p.id == point_id:
                return p
        return None

    def list_species(self) -> List[SpeciesInfo]:
        return _SPECIES

    # ---------- 地区筛选 ----------
    def filter_points(
        self,
        province: Optional[str] = None,
        city: Optional[str] = None,
        district: Optional[str] = None,
        town: Optional[str] = None,
    ) -> List[CicadaPoint]:
        pts = self._load()
        if province:
            pts = [p for p in pts if p.province == province]
        if city:
            pts = [p for p in pts if p.city == city]
        if district:
            pts = [p for p in pts if p.district == district]
        if town:
            pts = [p for p in pts if town in (p.town or "")]
        return pts

    # ---------- 统计 ----------
    def get_stats(
        self,
        province: Optional[str] = None,
        city: Optional[str] = None,
        district: Optional[str] = None,
    ) -> CicadaStats:
        points = self.filter_points(province=province, city=city, district=district)
        levels = {"高": 0, "中": 0, "低": 0}
        by_district: dict[str, int] = {}
        for p in points:
            levels[p.abundance] = levels.get(p.abundance, 0) + 1
            by_district[p.district] = by_district.get(p.district, 0) + 1
        return CicadaStats(
            total=len(points),
            districts=len(by_district),
            levels=levels,
            by_district=by_district,
        )

    def get_district_stats(self, district: str) -> DistrictStats:
        pts = self.filter_points(district=district)
        levels = {"高": 0, "中": 0, "低": 0}
        by_town: dict[str, int] = {}
        for p in pts:
            levels[p.abundance] = levels.get(p.abundance, 0) + 1
            key = p.town or "其他"
            by_town[key] = by_town.get(key, 0) + 1
        return DistrictStats(
            total=len(pts),
            levels=levels,
            by_town=by_town,
        )

    # ---------- 地区树 ----------
    def get_regions(self) -> List[RegionNode]:
        points = self._load()
        prov_map: dict[str, dict[str, set]] = {}
        for p in points:
            prov = p.province
            city = p.city
            dist = p.district
            prov_map.setdefault(prov, {}).setdefault(city, set()).add(dist)
        result = []
        for prov, city_map in sorted(prov_map.items()):
            cities = [
                CityNode(city=c, districts=sorted(dists))
                for c, dists in sorted(city_map.items())
            ]
            result.append(RegionNode(province=prov, cities=cities))
        return result

    # ---------- 搜索 ----------
    def search(self, query: str) -> SearchResult:
        if not query or len(query.strip()) < 1:
            return SearchResult(points=[], total=0)
        q = query.strip().lower()
        points = self._load()
        matched = [
            p for p in points
            if q in p.name.lower()
            or q in p.district.lower()
            or q in (p.town or "").lower()
            or q in p.species.lower()
            or q in p.province.lower()
            or q in p.city.lower()
        ]
        return SearchResult(points=matched, total=len(matched))
