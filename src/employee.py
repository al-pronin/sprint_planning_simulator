from __future__ import annotations
from typing import ClassVar, List, Optional
from src.feature import Feature, FeatureStage
from src.config import HOURS_PER_DAY


class Employee:
    """
    Base employee entity 👤

    An employee has:
    - Name
    - Daily productivity (in abstract effort units per day)
    - A set of stages they can effectively work on
    """

    effective_stages: ClassVar[List[FeatureStage]] = []

    def __init__(
        self,
        name: str,
        productivity_per_day: float = 1.0,
    ) -> None:
        """
        Args:
            name: Employee display name.
            productivity_per_day: Total effort units produced per working day.
        """
        self.name = name
        self.productivity_per_day = productivity_per_day
        self._worked_this_tick = False
        self.current_task_name: Optional[str] = None

    # ------------------------------------------------------------------ #
    # Productivity
    # ------------------------------------------------------------------ #

    @property
    def productivity_per_hour(self) -> float:
        """
        Productivity normalized to a single hour.

        Returns:
            Effort units produced in one hour.
        """
        return self.productivity_per_day / HOURS_PER_DAY

    # ------------------------------------------------------------------ #
    # Capability
    # ------------------------------------------------------------------ #

    def can_work_stage(self, stage: FeatureStage) -> bool:
        """
        Checks whether the employee can work on a given stage.
        """
        return stage in self.effective_stages

    # ------------------------------------------------------------------ #
    # Tick lifecycle
    # ------------------------------------------------------------------ #

    def reset_tick(self) -> None:
        """
        Resets per-tick state.
        """
        self._worked_this_tick = False
        self.current_task_name = None

    @property
    def has_worked(self) -> bool:
        """
        Indicates whether employee performed work in current tick.
        """
        return self._worked_this_tick

    # ------------------------------------------------------------------ #
    # Actions
    # ------------------------------------------------------------------ #

    def work(self, feature: Feature) -> None:
        """
        Perform work on a feature for a single hour 🛠

        Args:
            feature: Feature being worked on.
        """
        print(
            f"👨‍💻 {self.name} working on "
            f"{feature.name} [{feature.current_stage.name}]"
        )

        feature.work(self.productivity_per_hour)
        self._worked_this_tick = True
        self.current_task_name = feature.name

    def idle(self) -> None:
        """
        Called when employee has no work for this hour.
        """
        print(f"😴 {self.name} is idle this hour")
        self.current_task_name = "Idle"


# ---------------------------------------------------------------------- #
# Concrete roles
# ---------------------------------------------------------------------- #


class Developer(Employee):
    """
    Developer — responsible for DEVELOPMENT stage.
    """

    effective_stages = [FeatureStage.DEVELOPMENT]


class SystemAnalyst(Employee):
    """
    System Analyst — responsible for ANALYTICS stage.
    """

    effective_stages = [FeatureStage.ANALYTICS]


class QA(Employee):
    """
    QA Engineer — responsible for TESTING stage.
    """

    effective_stages = [FeatureStage.TESTING]
