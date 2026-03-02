"""
Custom exceptions for the sprint simulator.

This module defines domain-specific exceptions for clear error handling.
"""


class SimulatorError(Exception):
    """Base exception for all simulator-related errors."""

    pass


class PlanningError(SimulatorError):
    """
    Raised when sprint planning validation fails.

    Attributes:
        message: Human-readable error description.
        feature_name: Name of the problematic feature (if applicable).
    """

    def __init__(self, message: str, feature_name: str | None = None) -> None:
        self.message = message
        self.feature_name = feature_name
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if self.feature_name:
            return f"[{self.feature_name}] {self.message}"
        return f"Planning Error: {self.message}"


class NoReviewerAvailableError(PlanningError):
    """
    Raised when a feature has no eligible code reviewers.

    Attributes:
        assigned_developers: Developers assigned to the feature.
        available_developers: All developers in the team.
    """

    def __init__(
        self,
        feature_name: str,
        assigned_developers: list[str],
        available_developers: list[str],
    ) -> None:
        self.assigned_developers = assigned_developers
        self.available_developers = available_developers

        message = (
            f"No eligible code reviewers. "
            f"Assigned: {assigned_developers}. "
            f"Team: {available_developers}."
        )
        super().__init__(message, feature_name)


class NoBugFixContributorsError(PlanningError):
    """
    Raised when a feature has bugs but no one can fix them.

    This can happen if:
    - No developers did development (impossible for bugs)
    - No QA did testing (bug fix requires both)
    """

    def __init__(
        self,
        feature_name: str,
        development_contributors: list[str],
        testing_contributors: list[str],
    ) -> None:
        self.development_contributors = development_contributors
        self.testing_contributors = testing_contributors

        message = (
            f"No eligible bug fix contributors. "
            f"Developers: {development_contributors}. "
            f"QA: {testing_contributors}."
        )
        super().__init__(message, feature_name)
