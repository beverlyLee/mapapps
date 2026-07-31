"""捉知了点位 REST 路由。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.data import get_repository
from app.data.repository import CicadaRepository
from app.schemas import CicadaPoint, CicadaStats, SpeciesInfo

router = APIRouter(prefix="/api/cicada", tags=["cicada"])


def get_repo() -> CicadaRepository:
    return get_repository()


@router.get("/points", response_model=list[CicadaPoint])
def list_points(repo: CicadaRepository = Depends(get_repo)):
    return repo.list_points()


@router.get("/points/{point_id}", response_model=CicadaPoint)
def get_point(point_id: int, repo: CicadaRepository = Depends(get_repo)):
    point = repo.get_point(point_id)
    if point is None:
        raise HTTPException(status_code=404, detail="点位不存在")
    return point


@router.get("/stats", response_model=CicadaStats)
def stats(repo: CicadaRepository = Depends(get_repo)):
    return repo.get_stats()


@router.get("/species", response_model=list[SpeciesInfo])
def species(repo: CicadaRepository = Depends(get_repo)):
    return repo.list_species()
