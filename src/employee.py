from __future__ import annotations

from typing import ClassVar, List
from src.feature import Feature, FeatureStage


class Employee:
    """
    Base employee entity 👤
    """

    effective_stages: ClassVar[List[FeatureStage]] = []
    HOURS_PER_DAY: ClassVar[int] = 8

    def __init__(
        self,
        name: str,
        productivity_per_day: float = 1.0,
    ) -> None:
        self.name = name
        self.productivity_per_day = productivity_per_day
        self._worked_this_tick = False

    # ------------------------------------------------------------------ #
    # Productivity
    # ------------------------------------------------------------------ #

    @property
    def productivity_per_hour(self) -> float:
        return self.productivity_per_day / self.HOURS_PER_DAY

    # ------------------------------------------------------------------ #
    # Capability
    # ------------------------------------------------------------------ #

    def can_work_stage(self, stage: FeatureStage) -> bool:
        return stage in self.effective_stages

    # ------------------------------------------------------------------ #
    # Tick lifecycle
    # ------------------------------------------------------------------ #

    def reset_tick(self) -> None:
        self._worked_this_tick = False

    @property
    def has_worked(self) -> bool:
        return self._worked_this_tick

    # ------------------------------------------------------------------ #
    # Actions
    # ------------------------------------------------------------------ #

    def work(self, feature: Feature) -> None:
        """
        Perform work on feature for 1 hour.
        """
        print(
            f"👨‍💻 {self.name} working on "
            f"{feature.name} [{feature.current_stage.name}]"
        )

        feature.work(self.productivity_per_hour, self)
        self._worked_this_tick = True

    def idle(self) -> None:
        print(f"😴 {self.name} is idle this hour")


# ---------------------------------------------------------------------- #
# Roles
# ---------------------------------------------------------------------- #


class Developer(Employee):
    """
    Developer — DEVELOPMENT + REVIEW
    """

    effective_stages = [
        FeatureStage.DEVELOPMENT,
        FeatureStage.REVIEW,
    ]


class SystemAnalyst(Employee):
    effective_stages = [FeatureStage.ANALYTICS]


class QA(Employee):
    effective_stages = [FeatureStage.TESTING]