"""
History module for the sprint simulator.

This module provides snapshot classes and history collection
for recording simulation state over time.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.feature import FeatureStage


if TYPE_CHECKING:
    from src.employee import Employee
    from src.feature import Feature
    from src.timebox import Tick


@dataclass(frozen=True)
class FeatureSnapshot:
    """
    Immutable snapshot of a Feature's state at a specific point in time.

    Used for historical recording and reporting.

    Attributes:
        name: Feature identifier.
        current_stage: The stage the feature was in at snapshot time.
        remaining_efforts: Remaining effort for each stage.
        total_capacity: Original total estimated effort.
        is_done: Whether the feature was complete.
        development_contributors: Names of developers who worked on development.
    """

    name: str
    current_stage: FeatureStage
    remaining_efforts: dict[FeatureStage, float]
    total_capacity: float
    is_done: bool
    development_contributors: frozenset[str]

    @classmethod
    def from_feature(cls, feature: Feature) -> FeatureSnapshot:
        """
        Create a snapshot from a Feature instance.

        Args:
            feature: Feature to snapshot.

        Returns:
            New FeatureSnapshot with current feature state.
        """
        return cls(
            name=feature.name,
            current_stage=feature.current_stage,
            remaining_efforts=feature.get_remaining_efforts(),
            total_capacity=feature.total_capacity,
            is_done=feature.is_done,
            development_contributors=feature.development_contributors,
        )


@dataclass(frozen=True)
class EmployeeSnapshot:
    """
    Immutable snapshot of an Employee's state at a specific point in time.

    Used for historical recording and reporting.

    Attributes:
        name: Employee identifier.
        has_worked: Whether the employee worked during this tick.
        current_task: Name of the feature being worked on, or "Idle".
    """

    name: str
    has_worked: bool
    current_task: str | None

    @classmethod
    def from_employee(cls, employee: Employee) -> EmployeeSnapshot:
        """
        Create a snapshot from an Employee instance.

        Args:
            employee: Employee to snapshot.

        Returns:
            New EmployeeSnapshot with current employee state.
        """
        return cls(
            name=employee.name,
            has_worked=employee.has_worked,
            current_task=getattr(employee, "current_task_name", None),
        )


@dataclass(frozen=True)
class TickSnapshot:
    """
    Complete immutable snapshot of simulation state at a specific tick.

    Contains the state of all features and employees at a moment in time.

    Attributes:
        tick: The time point this snapshot represents.
        features: List of feature snapshots.
        employees: List of employee snapshots.
    """

    tick: Tick
    features: list[FeatureSnapshot]
    employees: list[EmployeeSnapshot]


class SprintHistory:
    """
    Collector for simulation snapshots over time.

    Maintains an ordered list of tick snapshots for analysis and reporting.

    Example:
        >>> history = SprintHistory()
        >>> history.record(tick, features, employees)
        >>> len(history.history)
        1
    """

    def __init__(self) -> None:
        """Initialize an empty history collector."""
        self._history: list[TickSnapshot] = []

    def record(
        self,
        tick: Tick,
        features: list[Feature],
        employees: list[Employee],
    ) -> None:
        """
        Record the current state of the simulation.

        Creates snapshots of all features and employees and appends
        them to the history.

        Args:
            tick: Current simulation time point.
            features: List of active features to snapshot.
            employees: List of employees to snapshot.
        """
        snapshot = TickSnapshot(
            tick=tick,
            features=[FeatureSnapshot.from_feature(f) for f in features],
            employees=[EmployeeSnapshot.from_employee(e) for e in employees],
        )
        self._history.append(snapshot)

    @property
    def history(self) -> list[TickSnapshot]:
        """
        Get the recorded history.

        Returns:
            List of all recorded tick snapshots in chronological order.
        """
        return self._history

    def get_feature_timeline(self, feature_name: str) -> list[FeatureSnapshot]:
        """
        Get the timeline of a specific feature across all ticks.

        Args:
            feature_name: Name of the feature to track.

        Returns:
            List of feature snapshots for the named feature.
        """
        result = []
        for tick_snapshot in self._history:
            for feature_snapshot in tick_snapshot.features:
                if feature_snapshot.name == feature_name:
                    result.append(feature_snapshot)
                    break
        return result

    def get_employee_timeline(self, employee_name: str) -> list[EmployeeSnapshot]:
        """
        Get the timeline of a specific employee across all ticks.

        Args:
            employee_name: Name of the employee to track.

        Returns:
            List of employee snapshots for the named employee.
        """
        result = []
        for tick_snapshot in self._history:
            for employee_snapshot in tick_snapshot.employees:
                if employee_snapshot.name == employee_name:
                    result.append(employee_snapshot)
                    break
        return result
