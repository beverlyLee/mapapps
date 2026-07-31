"""蝉了么点位 REST 路由。"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.data import get_repository
from app.data.repository import CicadaRepository
from app.schemas import (
    CicadaPoint, CicadaStats, DistrictStats,
    RegionNode, SearchResult, SpeciesInfo,
)

router = APIRouter(prefix="/api/cicada", tags=["cicada"])


def get_repo() -> CicadaRepository:
    return get_repository()


@router.get("/points", response_model=list[CicadaPoint])
def list_points(
    province: Optional[str] = Query(None, description="省份"),
    city: Optional[str] = Query(None, description="城市"),
    district: Optional[str] = Query(None, description="区县"),
    town: Optional[str] = Query(None, description="乡镇/村级模糊匹配"),
    repo: CicadaRepository = Depends(get_repo),
):
    return repo.filter_points(
        province=province, city=city, district=district, town=town,
    )


@router.get("/points/{point_id}", response_model=CicadaPoint)
def get_point(point_id: int, repo: CicadaRepository = Depends(get_repo)):
    point = repo.get_point(point_id)
    if point is None:
        raise HTTPException(status_code=404, detail="点位不存在")
    return point


@router.get("/stats", response_model=CicadaStats)
def stats(
    province: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    repo: CicadaRepository = Depends(get_repo),
):
    return repo.get_stats(province=province, city=city, district=district)


@router.get("/districts/{district}/stats", response_model=DistrictStats)
def district_stats(
    district: str,
    repo: CicadaRepository = Depends(get_repo),
):
    return repo.get_district_stats(district)


@router.get("/regions", response_model=list[RegionNode])
def regions(repo: CicadaRepository = Depends(get_repo)):
    return repo.get_regions()


@router.get("/search", response_model=SearchResult)
def search(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    repo: CicadaRepository = Depends(get_repo),
):
    return repo.search(q)


@router.get("/species", response_model=list[SpeciesInfo])
def species(repo: CicadaRepository = Depends(get_repo)):
    return repo.list_species()
