from __future__ import annotations
from enum import Enum
from typing import Dict, List, TYPE_CHECKING


if TYPE_CHECKING:
    from src.employee import Employee


class FeatureStage(Enum):
    ANALYTICS = "analytics"
    DEVELOPMENT = "development"
    TESTING = "testing"


class Feature:
    """
    Represents a feature moving through delivery stages 📦
    """

    STAGE_ORDER: List[FeatureStage] = [
        FeatureStage.ANALYTICS,
        FeatureStage.DEVELOPMENT,
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
        self.current_stage = initial_stage
        self.assignees: List["Employee"] = []

    def assign(self, employee: "Employee") -> None:
        if employee not in self.assignees:
            self.assignees.append(employee)

    def can_be_worked_by(self, employee: "Employee") -> bool:
        if employee not in self.assignees:
            return False
        if not employee.can_work_stage(self.current_stage):
            return False
        if self.is_done:
            return False
        return True

    def work(self, effort: float) -> None:
        remaining = self._remaining[self.current_stage]
        remaining -= effort
        self._remaining[self.current_stage] = max(0.0, round(remaining, 2))

        print(
            f"   🔧 {self.name} {self.current_stage.name} remaining: "
            f"{self._remaining[self.current_stage]}"
        )

    def try_advance(self) -> bool:
        """
        Move to next stage if current finished.
        Returns True if feature completed entirely.
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

    @property
    def is_done(self) -> bool:
        return all(value <= 0 for value in self._remaining.values())
