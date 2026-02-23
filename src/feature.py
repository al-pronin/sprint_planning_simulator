from __future__ import annotations

from enum import Enum
from typing import Dict, List, TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from src.employee import Employee


class FeatureStage(Enum):
    """
    Delivery lifecycle stages of a feature 📦
    """

    ANALYTICS = "analytics"
    DEVELOPMENT = "development"
    REVIEW = "review"
    TESTING = "testing"


class Feature:
    """
    Represents a feature moving through delivery stages.

    Responsibilities:
        - Track remaining effort per stage
        - Track current stage
        - Store last developer (author)
        - Handle stage transitions (except review logic)

    Review decision logic is intentionally NOT here.
    It is delegated to ReviewEngine (SRP).
    """

    STAGE_ORDER: List[FeatureStage] = [
        FeatureStage.ANALYTICS,
        FeatureStage.DEVELOPMENT,
        FeatureStage.REVIEW,
        FeatureStage.TESTING,
    ]

    def __init__(
        self,
        name: str,
        stage_capacities: Dict[FeatureStage, float],
        initial_stage: FeatureStage,
    ) -> None:
        self.name = name
        self._remaining: Dict[FeatureStage, float] = stage_capacities.copy()
        self.current_stage: FeatureStage = initial_stage
        self.assignees: List["Employee"] = []

        # 👇 NEW: track author of development
        self.last_developer: Optional["Employee"] = None

    # ------------------------------------------------------------------ #
    # Assignment
    # ------------------------------------------------------------------ #

    def assign(self, employee: "Employee") -> None:
        if employee not in self.assignees:
            self.assignees.append(employee)

    # ------------------------------------------------------------------ #
    # Capability
    # ------------------------------------------------------------------ #

    def can_be_worked_by(self, employee: "Employee") -> bool:
        """
        Checks whether an employee can work on current stage.
        """
        if employee not in self.assignees:
            return False

        if self.is_done:
            return False

        if not employee.can_work_stage(self.current_stage):
            return False

        # REVIEW specific rule: reviewer != author
        if (
            self.current_stage == FeatureStage.REVIEW
            and self.last_developer is not None
            and employee == self.last_developer
        ):
            return False

        return True

    # ------------------------------------------------------------------ #
    # Work
    # ------------------------------------------------------------------ #

    def work(self, effort: float, employee: "Employee") -> None:
        """
        Applies effort to current stage.

        If stage is DEVELOPMENT — remember author.
        """
        remaining = self._remaining[self.current_stage]
        remaining -= effort
        self._remaining[self.current_stage] = max(0.0, round(remaining, 2))

        if self.current_stage == FeatureStage.DEVELOPMENT:
            self.last_developer = employee

        print(
            f"   🔧 {self.name} [{self.current_stage.name}] "
            f"remaining: {self._remaining[self.current_stage]}"
        )

    # ------------------------------------------------------------------ #
    # Stage transitions
    # ------------------------------------------------------------------ #

    def move_to_stage(self, stage: FeatureStage) -> None:
        """
        Force move to specific stage.
        Used by ReviewEngine for rejection flow.
        """
        self.current_stage = stage
        print(f"↩️ {self.name} moved back to {stage.name}")

    def try_advance(self) -> bool:
        """
        Move to next stage if current finished.

        Returns:
            True if feature fully completed.
        """
        if self._remaining[self.current_stage] > 0:
            return False

        print(f"✅ {self.name} finished {self.current_stage.name}")

        current_index = self.STAGE_ORDER.index(self.current_stage)

        for next_stage in self.STAGE_ORDER[current_index + 1:]:
            if next_stage in self._remaining:
                self.current_stage = next_stage
                print(f"➡️ {self.name} moved to {self.current_stage.name}")
                return False

        print(f"🎉 Feature {self.name} fully completed!")
        return True

    # ------------------------------------------------------------------ #
    # State
    # ------------------------------------------------------------------ #

    @property
    def is_done(self) -> bool:
        return all(value <= 0 for value in self._remaining.values())