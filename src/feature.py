"""
Feature module for the sprint simulator.

This module defines the Feature entity and its lifecycle stages,
including the code review stage that occurs between development and testing.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from src.config import REVIEW_COEFFICIENT


if TYPE_CHECKING:
    from src.employee import Employee


class FeatureStage(Enum):
    """
    Enumeration of possible feature lifecycle stages.

    Features progress through these stages in order:
    ANALYTICS → DEVELOPMENT → CODE_REVIEW → TESTING

    Each stage may require different types of employees to complete.

    Attributes:
        ANALYTICS: Initial analysis and requirements gathering.
        DEVELOPMENT: Implementation and coding phase.
        CODE_REVIEW: Peer review of implemented code.
        TESTING: Quality assurance and validation.
    """

    ANALYTICS = "analytics"
    DEVELOPMENT = "development"
    CODE_REVIEW = "code_review"
    TESTING = "testing"

    def display_name(self) -> str:
        """
        Get a human-readable name for the stage.

        Returns:
            Capitalized stage name with proper formatting.
        """
        names = {
            FeatureStage.ANALYTICS: "Analytics",
            FeatureStage.DEVELOPMENT: "Development",
            FeatureStage.CODE_REVIEW: "Code Review",
            FeatureStage.TESTING: "Testing",
        }
        return names[self]


class Feature:
    """
    Represents a feature moving through delivery stages.

    A feature has estimated effort for each stage and can be worked on
    by assigned team members. The code review effort is automatically
    calculated as a percentage of development effort.

    Attributes:
        name: Human-readable feature identifier.
        current_stage: The stage the feature is currently in.
        assignees: List of employees assigned to work on this feature.

    Example:
        >>> feature = Feature(
        ...     name="Payment Integration",
        ...     stage_capacities={
        ...         FeatureStage.ANALYTICS: 2.0,
        ...         FeatureStage.DEVELOPMENT: 8.0,
        ...         FeatureStage.TESTING: 4.0,
        ...     },
        ...     initial_stage=FeatureStage.ANALYTICS,
        ... )
        >>> # CODE_REVIEW is auto-added with 20% of development effort
        >>> feature.get_remaining_efforts()[FeatureStage.CODE_REVIEW]
        1.6
    """

    STAGE_ORDER: list[FeatureStage] = [
        FeatureStage.ANALYTICS,
        FeatureStage.DEVELOPMENT,
        FeatureStage.CODE_REVIEW,
        FeatureStage.TESTING,
    ]

    def __init__(
        self,
        name: str,
        stage_capacities: dict[FeatureStage, float],
        initial_stage: FeatureStage,
        review_coefficient: float | None = None,
    ) -> None:
        """
        Initialize a feature with stage capacities.

        If DEVELOPMENT stage is defined, CODE_REVIEW is automatically
        added with effort proportional to development effort.

        Args:
            name: Feature identifier for display and logging.
            stage_capacities: Estimated effort for each stage.
            initial_stage: Stage to start the feature in.
            review_coefficient: Override default review effort ratio.
                If None, uses REVIEW_COEFFICIENT from config.

        Raises:
            ValueError: If initial_stage is not in stage_capacities.
        """
        self.name = name
        self._review_coefficient = review_coefficient or REVIEW_COEFFICIENT

        # Auto-add CODE_REVIEW if DEVELOPMENT is defined
        self._stage_capacities = self._calculate_stage_capacities(stage_capacities)

        # Validate initial stage
        if initial_stage not in self._stage_capacities:
            raise ValueError(
                f"Initial stage {initial_stage} must be in stage_capacities. "
                f"Available stages: {list(self._stage_capacities.keys())}"
            )

        self._remaining: dict[FeatureStage, float] = self._stage_capacities.copy()
        self.current_stage = initial_stage
        self.assignees: list[Employee] = []

        # Track developers who worked on this feature (for review eligibility)
        self._development_contributors: set[str] = set()

    def _calculate_stage_capacities(
        self,
        stage_capacities: dict[FeatureStage, float],
    ) -> dict[FeatureStage, float]:
        """
        Calculate final stage capacities including auto-generated CODE_REVIEW.

        Args:
            stage_capacities: User-provided stage capacities.

        Returns:
            Complete stage capacities with CODE_REVIEW if applicable.
        """
        result = stage_capacities.copy()

        # Auto-add CODE_REVIEW after DEVELOPMENT if development exists
        if FeatureStage.DEVELOPMENT in result:
            dev_effort = result[FeatureStage.DEVELOPMENT]
            review_effort = round(dev_effort * self._review_coefficient, 2)

            # Only add if not explicitly provided
            if FeatureStage.CODE_REVIEW not in result:
                result[FeatureStage.CODE_REVIEW] = review_effort

        return result

    @property
    def total_capacity(self) -> float:
        """
        Total estimated effort across all stages.

        Returns:
            Sum of all stage efforts.
        """
        return sum(self._stage_capacities.values())

    @property
    def review_coefficient(self) -> float:
        """
        The coefficient used to calculate review effort.

        Returns:
            Review effort as fraction of development effort.
        """
        return self._review_coefficient

    @property
    def has_code_review(self) -> bool:
        """
        Check if this feature has a code review stage.

        Returns:
            True if CODE_REVIEW stage exists with non-zero effort.
        """
        return (
            FeatureStage.CODE_REVIEW in self._stage_capacities
            and self._stage_capacities[FeatureStage.CODE_REVIEW] > 0
        )

    @property
    def development_contributors(self) -> frozenset[str]:
        """
        Get names of developers who contributed to development.

        These developers are NOT eligible to perform code review.

        Returns:
            Frozen set of developer names.
        """
        return frozenset(self._development_contributors)

    def register_development_contributor(self, employee: Employee) -> None:
        """
        Register an employee as a development contributor.

        Should be called when an employee works on DEVELOPMENT stage.
        Registered contributors cannot perform code review.

        Args:
            employee: The employee who contributed to development.
        """
        if employee.name not in self._development_contributors:
            self._development_contributors.add(employee.name)

    def assign(self, employee: Employee) -> None:
        """
        Assign an employee to work on this feature.

        Args:
            employee: Employee to add to assignees list.
        """
        if employee not in self.assignees:
            self.assignees.append(employee)

    def can_be_worked_by(self, employee: Employee) -> bool:
        """
        Check if an employee can work on this feature's current stage.

        Rules by stage:
        - ANALYTICS, DEVELOPMENT, TESTING: Must be assigned to the feature
        - CODE_REVIEW: Any Developer can review (not required to be assigned),
          but must NOT have contributed to development

        Args:
            employee: Employee to check eligibility for.

        Returns:
            True if the employee can work on current stage.
        """
        if self.is_done:
            return False

        if not employee.can_work_stage(self.current_stage):
            return False

        # Code review special case: external reviewer allowed
        if self.current_stage == FeatureStage.CODE_REVIEW:
            # Reviewer must not have done development
            if employee.name in self._development_contributors:
                return False
            # Any developer can review (even if not assigned)
            return True

        # For other stages, must be assigned to the feature
        if employee not in self.assignees:
            return False

        return True

    def get_remaining_efforts(self) -> dict[FeatureStage, float]:
        """
        Get remaining effort for each stage.

        Returns:
            Copy of remaining efforts dictionary.
        """
        return self._remaining.copy()

    def get_stage_capacity(self, stage: FeatureStage) -> float:
        """
        Get the original capacity for a specific stage.

        Args:
            stage: The stage to query.

        Returns:
            Original estimated effort for the stage, or 0 if not defined.
        """
        return self._stage_capacities.get(stage, 0.0)

    def work(self, effort: float) -> None:
        """
        Apply work effort to the current stage.

        If currently in DEVELOPMENT stage, track the employee as a contributor.

        Args:
            effort: Amount of work effort to apply.
        """
        remaining = self._remaining[self.current_stage]
        remaining -= effort
        self._remaining[self.current_stage] = max(0.0, round(remaining, 2))

        print(
            f"   🔧 {self.name} {self.current_stage.display_name()} remaining: "
            f"{self._remaining[self.current_stage]:.1f}h"
        )

    def try_advance(self) -> bool:
        """
        Attempt to advance to the next stage.

        If current stage is complete (zero remaining effort),
        move to the next defined stage. If no stages remain,
        the feature is complete.

        Returns:
            True if the feature is fully complete, False otherwise.
        """
        if self._remaining[self.current_stage] > 0:
            return False

        print(f"✅ {self.name} finished {self.current_stage.display_name()}")

        current_index = self.STAGE_ORDER.index(self.current_stage)

        for next_stage in self.STAGE_ORDER[current_index + 1 :]:
            if next_stage in self._remaining:
                self.current_stage = next_stage
                print(f"➡️ {self.name} moved to {self.current_stage.display_name()}")
                return False

        print(f"🎉 Feature {self.name} fully completed!")
        return True

    @property
    def is_done(self) -> bool:
        """
        Check if all stages are complete.

        Returns:
            True if all stages have zero remaining effort.
        """
        return all(value <= 0 for value in self._remaining.values())

    def __repr__(self) -> str:
        """
        String representation for debugging.

        Returns:
            Feature name and current stage.
        """
        return f"Feature({self.name!r}, stage={self.current_stage.name})"
