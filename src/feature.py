"""
Feature module for the sprint simulator.

This module defines the Feature entity and its lifecycle stages,
including code review and bug fix mechanics.
"""

from __future__ import annotations

import random
from enum import Enum
from typing import TYPE_CHECKING

from src.config import BUG_FIX_COEFFICIENT, BUG_PROBABILITY, REVIEW_COEFFICIENT


if TYPE_CHECKING:
    from src.employee import Employee


class FeatureStage(Enum):
    """
    Feature lifecycle stages in order.

    Features progress through stages in order:
    ANALYTICS → DEVELOPMENT → CODE_REVIEW → TESTING → BUG_FIX (conditional)

    BUG_FIX appears only with a certain probability after TESTING.
    """

    ANALYTICS = "analytics"
    DEVELOPMENT = "development"
    CODE_REVIEW = "code_review"
    TESTING = "testing"
    BUG_FIX = "bug_fix"

    def display_name(self) -> str:
        """Human-readable stage name."""
        names = {
            FeatureStage.ANALYTICS: "Analytics",
            FeatureStage.DEVELOPMENT: "Development",
            FeatureStage.CODE_REVIEW: "Code Review",
            FeatureStage.TESTING: "Testing",
            FeatureStage.BUG_FIX: "Bug Fix",
        }
        return names[self]


class Feature:
    """
    Feature moving through delivery stages.

    Supports automatic CODE_REVIEW generation and conditional BUG_FIX
    stage based on probability after testing completion.

    Attributes:
        name: Feature identifier.
        current_stage: Current stage in the pipeline.
        bug_probability: Probability of bugs appearing after testing.
        bug_fix_coefficient: Multiplier for bug fix effort calculation.
    """

    STAGE_ORDER: list[FeatureStage] = [
        FeatureStage.ANALYTICS,
        FeatureStage.DEVELOPMENT,
        FeatureStage.CODE_REVIEW,
        FeatureStage.TESTING,
        # BUG_FIX is conditional, added dynamically
    ]

    def __init__(
        self,
        name: str,
        stage_capacities: dict[FeatureStage, float],
        initial_stage: FeatureStage,
        review_coefficient: float | None = None,
        bug_probability: float | None = None,
        bug_fix_coefficient: float | None = None,
    ) -> None:
        """
        Initialize feature with stage capacities.

        CODE_REVIEW is auto-generated if DEVELOPMENT exists.
        BUG_FIX is added dynamically after TESTING if bugs are found.

        Args:
            name: Feature identifier.
            stage_capacities: Estimated effort for each stage.
            initial_stage: Starting stage.
            review_coefficient: Override default (20% of dev).
            bug_probability: Override default (30%).
            bug_fix_coefficient: Override default (10% of dev).
        """
        self.name = name
        self._review_coefficient = review_coefficient or REVIEW_COEFFICIENT
        self._bug_probability = (
            bug_probability if bug_probability is not None else BUG_PROBABILITY
        )
        self._bug_fix_coefficient = bug_fix_coefficient or BUG_FIX_COEFFICIENT

        # Store development effort for bug fix calculation
        self._development_effort = stage_capacities.get(FeatureStage.DEVELOPMENT, 0.0)

        # Auto-add CODE_REVIEW
        self._capacities = self._build_capacities(stage_capacities)

        # Remaining effort per stage
        self._remaining = self._capacities.copy()

        # Current stage
        if initial_stage not in self._capacities:
            raise ValueError(
                f"Initial stage {initial_stage} not in capacities. "
                f"Available: {list(self._capacities.keys())}"
            )
        self.current_stage = initial_stage

        # Assigned employees
        self.assignees: list[Employee] = []

        # Contributor tracking for eligibility
        self._dev_contributors: set[str] = set()
        self._testing_contributors: set[str] = set()

        # Bug status
        self._has_bugs: bool | None = None

    def _build_capacities(
        self,
        stage_capacities: dict[FeatureStage, float],
    ) -> dict[FeatureStage, float]:
        """Build complete stage capacities including auto CODE_REVIEW."""
        result = stage_capacities.copy()

        if FeatureStage.DEVELOPMENT in result:
            dev_effort = result[FeatureStage.DEVELOPMENT]
            review_effort = round(dev_effort * self._review_coefficient, 2)

            if FeatureStage.CODE_REVIEW not in result:
                result[FeatureStage.CODE_REVIEW] = review_effort

        return result

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #

    @property
    def has_code_review(self) -> bool:
        """Check if this feature has a code review stage with non-zero effort."""
        return (
            FeatureStage.CODE_REVIEW in self._capacities
            and self._capacities[FeatureStage.CODE_REVIEW] > 0
        )

    @property
    def bug_probability(self) -> float:
        """Probability of bugs appearing after testing."""
        return self._bug_probability

    @property
    def bug_fix_coefficient(self) -> float:
        """Multiplier for bug fix effort calculation."""
        return self._bug_fix_coefficient

    @property
    def total_capacity(self) -> float:
        """Total effort across all stages."""
        return sum(self._capacities.values())

    @property
    def is_done(self) -> bool:
        """Check if all stages are complete."""
        return all(effort <= 0 for effort in self._remaining.values())

    @property
    def has_bugs(self) -> bool | None:
        """Whether bugs were found (None if not determined yet)."""
        return self._has_bugs

    @property
    def development_contributors(self) -> frozenset[str]:
        """Names of developers who contributed to development."""
        return frozenset(self._dev_contributors)

    @property
    def testing_contributors(self) -> frozenset[str]:
        """Names of QA who contributed to testing."""
        return frozenset(self._testing_contributors)

    # ------------------------------------------------------------------ #
    # Assignment & Contributors
    # ------------------------------------------------------------------ #

    def assign(self, employee: Employee) -> None:
        """Assign employee to this feature."""
        if employee not in self.assignees:
            self.assignees.append(employee)

    def register_development_contributor(self, employee: Employee) -> None:
        """Register employee as development contributor."""
        self._dev_contributors.add(employee.name)

    def register_testing_contributor(self, employee: Employee) -> None:
        """Register employee as testing contributor."""
        self._testing_contributors.add(employee.name)

    # ------------------------------------------------------------------ #
    # Work & Stage Management
    # ------------------------------------------------------------------ #

    def get_remaining_efforts(self) -> dict[FeatureStage, float]:
        """Get remaining effort for each stage."""
        return self._remaining.copy()

    def get_stage_capacity(self, stage: FeatureStage) -> float:
        """Get original capacity for a stage."""
        return self._capacities.get(stage, 0.0)

    def work(self, effort: float) -> None:
        """Apply work effort to current stage."""
        if self.current_stage not in self._remaining:
            return

        remaining = self._remaining[self.current_stage] - effort
        self._remaining[self.current_stage] = max(0.0, round(remaining, 2))

        stage_name = self.current_stage.display_name()
        print(
            f"   🔧 {self.name} {stage_name} remaining: "
            f"{self._remaining[self.current_stage]:.1f}h"
        )

    def try_advance(self) -> bool:
        """
        Advance to next stage if current is complete.

        Returns:
            True if feature is fully done, False otherwise.
        """
        if self._remaining.get(self.current_stage, 0) > 0:
            return False

        print(f"✅ {self.name} finished {self.current_stage.display_name()}")

        # TESTING completion: check for bugs
        if self.current_stage == FeatureStage.TESTING:
            return self._handle_testing_completion()

        # BUG_FIX completion: feature is done
        if self.current_stage == FeatureStage.BUG_FIX:
            print(f"🎉 Feature {self.name} fully completed!")
            return True

        # Standard advancement
        idx = self.STAGE_ORDER.index(self.current_stage)

        for next_stage in self.STAGE_ORDER[idx + 1 :]:
            if next_stage in self._remaining:
                self.current_stage = next_stage
                print(f"➡️ {self.name} moved to {self.current_stage.display_name()}")
                return False

        print(f"🎉 Feature {self.name} fully completed!")
        return True

    def _handle_testing_completion(self) -> bool:
        """Handle TESTING completion, possibly adding BUG_FIX."""
        self._has_bugs = random.random() < self._bug_probability

        if self._has_bugs:
            bug_effort = round(self._development_effort * self._bug_fix_coefficient, 2)
            self._remaining[FeatureStage.BUG_FIX] = bug_effort
            self.current_stage = FeatureStage.BUG_FIX

            print(f"🐛 Bugs found in {self.name}! Bug Fix effort: {bug_effort:.1f}h")
            print(f"➡️ {self.name} moved to {self.current_stage.display_name()}")
            return False
        else:
            print(f"✅ No bugs found in {self.name}")
            print(f"🎉 Feature {self.name} fully completed!")
            return True

    def can_be_worked_by(self, employee: Employee) -> bool:
        """
        Check if employee can work on current stage.

        Rules:
        - ANALYTICS, DEVELOPMENT, TESTING: Must be assigned
        - CODE_REVIEW: Any Developer (not assigned to avoid conflict),
          must NOT have done development
        - BUG_FIX: Only contributors (dev or testing)
        """
        if self.is_done:
            return False

        if not employee.can_work_stage(self.current_stage):
            return False

        # CODE_REVIEW: external reviewer allowed, but not contributor
        if self.current_stage == FeatureStage.CODE_REVIEW:
            return employee.name not in self._dev_contributors

        # BUG_FIX: only contributors
        if self.current_stage == FeatureStage.BUG_FIX:
            return (
                employee.name in self._dev_contributors
                or employee.name in self._testing_contributors
            )

        # Other stages: must be assigned
        return employee in self.assignees

    def __repr__(self) -> str:
        """String representation."""
        return f"Feature({self.name!r}, stage={self.current_stage.name})"
