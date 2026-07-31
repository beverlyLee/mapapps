"""数据仓库抽象接口（ABC）。

所有数据源（Excel / 数据库）都实现此接口，业务层只依赖抽象，
切换数据源时无需改动路由与前端。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from app.schemas import CicadaPoint, CicadaStats, SpeciesInfo


class CicadaRepository(ABC):
    """捉知了点位数据访问接口。"""

    @abstractmethod
    def list_points(self) -> List[CicadaPoint]:
        ...

    @abstractmethod
    def get_point(self, point_id: int) -> Optional[CicadaPoint]:
        ...

    @abstractmethod
    def list_species(self) -> List[SpeciesInfo]:
        ...

    @abstractmethod
    def get_stats(self) -> CicadaStats:
        ...

    # ---- 以下为「未来写库」预留接口（Excel 实现默认不支持）----
    def add_point(self, point: CicadaPoint) -> CicadaPoint:
        raise NotImplementedError("当前数据源不支持写入")

    def update_point(self, point_id: int, point: CicadaPoint) -> Optional[CicadaPoint]:
        raise NotImplementedError("当前数据源不支持写入")

    def delete_point(self, point_id: int) -> bool:
        raise NotImplementedError("当前数据源不支持写入")
