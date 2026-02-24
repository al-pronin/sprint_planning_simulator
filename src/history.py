from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, TYPE_CHECKING
from src.feature import FeatureStage

if TYPE_CHECKING:
    from src.feature import Feature
    from src.employee import Employee
    from src.timebox import Tick


@dataclass(frozen=True)
class FeatureSnapshot:
    """
    Snapshot of a Feature's state at a specific point in time. 📦
    """
    name: str
    current_stage: FeatureStage
    remaining_efforts: Dict[FeatureStage, float]
    total_capacity: float  # Added for progress calculation
    is_done: bool

    @classmethod
    def from_feature(cls, feature: Feature) -> FeatureSnapshot:
        """
        Creates a snapshot from a Feature instance.
        """
        return cls(
            name=feature.name,
            current_stage=feature.current_stage,
            remaining_efforts=feature.get_remaining_efforts(),
            total_capacity=feature.total_capacity,
            is_done=feature.is_done,
        )


@dataclass(frozen=True)
class EmployeeSnapshot:
    """
    Snapshot of an Employee's state at a specific point in time. 👤
    """
    name: str
    has_worked: bool
    current_task: str | None  # Name of the feature or "Idle"

    @classmethod
    def from_employee(cls, employee: Employee) -> EmployeeSnapshot:
        """
        Creates a snapshot from an Employee instance.
        """
        return cls(
            name=employee.name,
            has_worked=employee.has_worked,
            current_task=getattr(employee, "current_task_name", None),
        )


@dataclass(frozen=True)
class TickSnapshot:
    """
    Complete state of the simulation at a specific tick. ⏳
    """
    tick: Tick
    features: List[FeatureSnapshot]
    employees: List[EmployeeSnapshot]


class SprintHistory:
    """
    Collector for simulation snapshots over time. 📚
    """

    def __init__(self) -> None:
        self._history: List[TickSnapshot] = []

    def record(self, tick: Tick, features: List[Feature], employees: List[Employee]) -> None:
        """
        Records the current state of the simulation.
        """
        snapshot = TickSnapshot(
            tick=tick,
            features=[FeatureSnapshot.from_feature(f) for f in features],
            employees=[EmployeeSnapshot.from_employee(e) for e in employees],
        )
        self._history.append(snapshot)

    @property
    def history(self) -> List[TickSnapshot]:
        """
        Returns the recorded history.
        """
        return self._history