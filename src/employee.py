"""
Employee module for the sprint simulator.

This module defines the Employee base class and specialized roles
(Developer, SystemAnalyst, QA) with their stage capabilities.
"""

from __future__ import annotations

from typing import ClassVar

from src.config import HOURS_PER_DAY
from src.feature import Feature, FeatureStage


class Employee:
    """
    Base employee entity representing a team member.

    An employee has productivity metrics and can work on specific
    feature stages based on their role. Productivity affects how
    much effort they contribute per time unit.

    Attributes:
        name: Display name for the employee.
        productivity_per_day: Base productivity units per working day.

    Example:
        >>> dev = Developer(name="Alice", productivity_per_day=1.5)
        >>> dev.can_work_stage(FeatureStage.DEVELOPMENT)
        True
        >>> dev.can_work_stage(FeatureStage.TESTING)
        False
    """

    effective_stages: ClassVar[list[FeatureStage]] = []

    def __init__(
        self,
        name: str,
        productivity_per_day: float = 1.0,
    ) -> None:
        """
        Initialize an employee.

        Args:
            name: Employee display name for logging and display.
            productivity_per_day: Total effort units produced per working day.
                Higher values mean the employee completes work faster.
        """
        self.name = name
        self.productivity_per_day = productivity_per_day
        self._worked_this_tick = False
        self.current_task_name: str | None = None

    # ------------------------------------------------------------------ #
    # Productivity
    # ------------------------------------------------------------------ #

    @property
    def productivity_per_hour(self) -> float:
        """
        Productivity normalized to a single hour.

        Returns:
            Effort units produced in one hour of work.
        """
        return self.productivity_per_day / HOURS_PER_DAY

    # ------------------------------------------------------------------ #
    # Capability
    # ------------------------------------------------------------------ #

    def can_work_stage(self, stage: FeatureStage) -> bool:
        """
        Check if this employee can work on a given stage.

        This checks role capability only, not availability or
        feature-specific constraints (like code review eligibility).

        Args:
            stage: The feature stage to check.

        Returns:
            True if the employee's role can work on this stage.
        """
        return stage in self.effective_stages

    # ------------------------------------------------------------------ #
    # Tick lifecycle
    # ------------------------------------------------------------------ #

    def reset_tick(self) -> None:
        """
        Reset per-tick state before processing a new hour.

        This should be called at the start of each simulation tick.
        """
        self._worked_this_tick = False
        self.current_task_name = None

    @property
    def has_worked(self) -> bool:
        """
        Check if employee performed work in the current tick.

        Returns:
            True if work() was called this tick, False otherwise.
        """
        return self._worked_this_tick

    # ------------------------------------------------------------------ #
    # Actions
    # ------------------------------------------------------------------ #

    def work(self, feature: Feature) -> None:
        """
        Perform work on a feature for a single hour.

        This applies the employee's hourly productivity to the feature's
        current stage and records the task as active.

        For DEVELOPMENT stage, registers the employee as a contributor
        (affecting code review eligibility).

        Args:
            feature: Feature to work on.
        """
        print(
            f"👨‍💻 {self.name} working on "
            f"{feature.name} [{feature.current_stage.display_name()}]"
        )

        # Track development contributors for code review eligibility
        if feature.current_stage == FeatureStage.DEVELOPMENT:
            feature.register_development_contributor(self)

        feature.work(self.productivity_per_hour)
        self._worked_this_tick = True
        self.current_task_name = feature.name

    def idle(self) -> None:
        """
        Mark the employee as idle for this tick.

        Called when no suitable work is available.
        """
        print(f"😴 {self.name} is idle this hour")
        self.current_task_name = "Idle"

    def __repr__(self) -> str:
        """
        String representation for debugging.

        Returns:
            Class name and employee name.
        """
        return f"{self.__class__.__name__}({self.name!r})"


# ---------------------------------------------------------------------- #
# Concrete roles
# ---------------------------------------------------------------------- #


class Developer(Employee):
    """
    Developer role specialized for implementation work.

    Developers can work on:
    - DEVELOPMENT: Writing and implementing code
    - CODE_REVIEW: Reviewing peers' code (if not involved in development)

    Note:
        Code review eligibility is determined at the feature level,
        not here. This class only defines role capabilities.

    Example:
        >>> dev = Developer(name="Bob")
        >>> FeatureStage.DEVELOPMENT in dev.effective_stages
        True
        >>> FeatureStage.CODE_REVIEW in dev.effective_stages
        True
    """

    effective_stages = [FeatureStage.DEVELOPMENT, FeatureStage.CODE_REVIEW]


class SystemAnalyst(Employee):
    """
    System Analyst role specialized for requirements and analysis.

    System Analysts can work on:
    - ANALYTICS: Requirements gathering and analysis

    Example:
        >>> analyst = SystemAnalyst(name="Carol")
        >>> analyst.can_work_stage(FeatureStage.ANALYTICS)
        True
    """

    effective_stages = [FeatureStage.ANALYTICS]


class QA(Employee):
    """
    QA Engineer role specialized for testing.

    QA Engineers can work on:
    - TESTING: Quality assurance and validation

    Example:
        >>> qa = QA(name="Dave")
        >>> qa.can_work_stage(FeatureStage.TESTING)
        True
    """

    effective_stages = [FeatureStage.TESTING]
