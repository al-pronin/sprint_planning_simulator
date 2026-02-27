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

    A strategy receives the employee and available features, then
    returns the most appropriate feature for that employee to work on.
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

    This strategy assigns employees to the first feature they can work on,
    in the order features are provided. It has no prioritization logic.

    This is the simplest strategy suitable for basic simulations.

    Example:
        >>> strategy = SimpleAssignmentStrategy()
        >>> feature = strategy.choose_feature(developer, features)
    """

    def choose_feature(
        self,
        employee: Employee,
        features: list[Feature],
    ) -> Feature | None:
        """
        Choose the first feature the employee can work on.

        Iterates through features in order and returns the first one
        where can_be_worked_by returns True.

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

    This strategy considers feature priorities and remaining work
    when making assignments. Features closer to completion or with
    higher priority are preferred.

    Attributes:
        prioritize_completion: Whether to favor features closer to done.
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
