from __future__ import annotations
from typing import ClassVar, List
from src.feature import Feature, FeatureStage


class Employee:
    """
    Base employee entity 👤
    """

    effective_stages: ClassVar[List[FeatureStage]] = []
    SLOTS_PER_DAY: ClassVar[int] = 2

    def __init__(self, name: str, productivity_per_day: float = 1.0) -> None:
        self.name = name
        self.productivity_per_day = productivity_per_day
        self._worked_this_tick = False

    @property
    def productivity_per_tick(self) -> float:
        """Productivity normalized to half-day."""
        return self.productivity_per_day / self.SLOTS_PER_DAY

    def can_work_stage(self, stage: FeatureStage) -> bool:
        return stage in self.effective_stages

    def reset_tick(self) -> None:
        self._worked_this_tick = False

    def work(self, feature: Feature) -> None:
        """
        Perform work on a feature for a single tick 🛠
        """
        print(f"👨‍💻 {self.name} working on {feature.name} [{feature.current_stage.name}]")
        feature.work(self.productivity_per_tick)
        self._worked_this_tick = True

    def idle(self) -> None:
        print(f"😴 {self.name} is idle this tick")

    @property
    def has_worked(self) -> bool:
        return self._worked_this_tick


class Developer(Employee):
    effective_stages = [FeatureStage.DEVELOPMENT]


class SystemAnalyst(Employee):
    effective_stages = [FeatureStage.ANALYTICS]


class QA(Employee):
    effective_stages = [FeatureStage.TESTING]
