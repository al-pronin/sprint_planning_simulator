"""
Employee module for the sprint simulator.

Defines Employee base class and specialized roles (Developer, Analyst, QA)
with their stage capabilities and work methods.
"""

from __future__ import annotations

from typing import ClassVar

from src.config import HOURS_PER_DAY
from src.feature import Feature, FeatureStage


class Employee:
    """
    Base employee entity representing a team member.

    Attributes:
        name: Display name.
        productivity_per_day: Effort units per working day.
        effective_stages: Stages this role can work on.
    """

    effective_stages: ClassVar[list[FeatureStage]] = []

    def __init__(self, name: str, productivity_per_day: float = 8.0) -> None:
        """Initialize employee."""
        self.name = name
        self.productivity_per_day = productivity_per_day
        self._worked_this_tick = False
        self.current_task_name: str | None = None

    @property
    def productivity_per_hour(self) -> float:
        """Effort per hour."""
        return self.productivity_per_day / HOURS_PER_DAY

    def can_work_stage(self, stage: FeatureStage) -> bool:
        """Check if role can work on this stage."""
        return stage in self.effective_stages

    def reset_tick(self) -> None:
        """Reset per-tick state."""
        self._worked_this_tick = False
        self.current_task_name = None

    @property
    def has_worked(self) -> bool:
        """Whether employee worked this tick."""
        return self._worked_this_tick

    def work(self, feature: Feature) -> None:
        """Work on feature for one hour."""
        stage = feature.current_stage

        print(f"👨‍💻 {self.name} working on {feature.name} [{stage.display_name()}]")

        # Register contributors
        if stage == FeatureStage.DEVELOPMENT:
            feature.register_development_contributor(self)
        elif stage == FeatureStage.TESTING:
            feature.register_testing_contributor(self)

        feature.work(self.productivity_per_hour)
        self._worked_this_tick = True
        self.current_task_name = feature.name

    def idle(self) -> None:
        """Mark as idle."""
        print(f"😴 {self.name} is idle this hour")
        self.current_task_name = "Idle"

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}({self.name!r})"


class Developer(Employee):
    """
    Developer: DEVELOPMENT, CODE_REVIEW, BUG_FIX.
    """

    effective_stages = [
        FeatureStage.DEVELOPMENT,
        FeatureStage.CODE_REVIEW,
        FeatureStage.BUG_FIX,
    ]


class SystemAnalyst(Employee):
    """
    System Analyst: ANALYTICS only.
    """

    effective_stages = [FeatureStage.ANALYTICS]


class QA(Employee):
    """
    QA: TESTING, BUG_FIX.
    """

    effective_stages = [FeatureStage.TESTING, FeatureStage.BUG_FIX]
