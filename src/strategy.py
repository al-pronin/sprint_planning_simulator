"""
Assignment strategy module for the sprint simulator.

This module defines the strategy interface and implementations
for assigning work to employees during simulation.
"""

from __future__ import annotations

from typing import Protocol

from src.employee import Employee
from src.feature import Feature


class AssignmentStrategy(Protocol):
    """
    Protocol defining the interface for work assignment strategies.

    Implementations determine how employees are matched to features
    when there are multiple options available.
    """

    def choose_feature(
        self,
        employee: Employee,
        features: list[Feature],
    ) -> Feature | None:
        """
        Choose the best feature for an employee to work on.

        Args:
            employee: The employee needing assignment.
            features: List of available features.

        Returns:
            The chosen feature, or None if no suitable work exists.
        """
        ...


class SimpleAssignmentStrategy:
    """
    Greedy assignment strategy using first-match logic.

    Assigns employees to the first feature they can work on,
    in the order features are provided.
    """

    def choose_feature(
        self,
        employee: Employee,
        features: list[Feature],
    ) -> Feature | None:
        """
        Choose the first feature the employee can work on.

        Args:
            employee: The employee needing assignment.
            features: List of available features in priority order.

        Returns:
            First suitable feature, or None if no match found.
        """
        for feature in features:
            if feature.can_be_worked_by(employee):
                return feature
        return None


class PriorityBasedAssignmentStrategy:
    """
    Priority-based assignment strategy.

    Considers feature priorities and remaining work when making
    assignments. Features closer to completion or with higher
    priority are preferred.
    """

    def __init__(self, prioritize_completion: bool = True) -> None:
        """
        Initialize the priority-based strategy.

        Args:
            prioritize_completion: If True, favor features with less
                remaining work (closer to completion).
        """
        self.prioritize_completion = prioritize_completion

    def choose_feature(
        self,
        employee: Employee,
        features: list[Feature],
    ) -> Feature | None:
        """
        Choose the best feature based on priority and completion.

        Args:
            employee: The employee needing assignment.
            features: List of available features.

        Returns:
            Most suitable feature, or None if no match found.
        """
        eligible_features = [
            f for f in features if f.can_be_worked_by(employee)
        ]

        if not eligible_features:
            return None

        if self.prioritize_completion:
            # Sort by remaining total effort (ascending)
            eligible_features.sort(
                key=lambda f: sum(f.get_remaining_efforts().values())
            )

        return eligible_features[0]


class BugFixPriorityStrategy:
    """
    Strategy that prioritizes bug fixes over other work.

    Bug fixes are urgent - they block feature completion and
    involve both developers and QA who worked on the feature.
    """

    def choose_feature(
        self,
        employee: Employee,
        features: list[Feature],
    ) -> Feature | None:
        """
        Choose feature with bug fix priority.

        Args:
            employee: The employee needing assignment.
            features: List of available features.

        Returns:
            Feature needing bug fix first, then others.
        """
        from src.feature import FeatureStage

        # First, check for bug fix work
        for feature in features:
            if feature.current_stage == FeatureStage.BUG_FIX:
                if feature.can_be_worked_by(employee):
                    return feature

        # Then, other work
        for feature in features:
            if feature.can_be_worked_by(employee):
                return feature

        return None
