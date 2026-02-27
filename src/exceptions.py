"""
Custom exceptions for the sprint simulator.

This module defines domain-specific exceptions used throughout the simulation
to provide clear, actionable error messages for planning and execution errors.
"""


class SimulatorError(Exception):
    """
    Base exception for all simulator-related errors.

    All custom exceptions in the simulator should inherit from this class
    to allow for broad exception handling when needed.
    """

    pass


class PlanningError(SimulatorError):
    """
    Raised when sprint planning validation fails.

    This exception indicates that the sprint configuration is invalid
    and cannot be simulated. Common causes include:
    - No available reviewers for a feature
    - Insufficient team capacity
    - Invalid feature stage configurations

    Attributes:
        message: Human-readable description of the planning error.
        feature_name: Name of the feature that caused the error (if applicable).
    """

    def __init__(self, message: str, feature_name: str | None = None) -> None:
        """
        Initialize the planning error.

        Args:
            message: Description of what went wrong during planning.
            feature_name: Optional name of the problematic feature.
        """
        self.message = message
        self.feature_name = feature_name
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """
        Format the error message with feature context if available.

        Returns:
            Formatted error message string.
        """
        if self.feature_name:
            return f"[{self.feature_name}] {self.message}"
        return f"Planning Error: {self.message}"


class NoReviewerAvailableError(PlanningError):
    """
    Raised when a feature has no eligible code reviewers.

    This occurs when all developers who can work on code review
    are assigned to the feature's development, violating the rule
    that reviewers must not have participated in development.

    Attributes:
        feature_name: Name of the feature lacking reviewers.
        assigned_developers: List of developer names assigned to the feature.
        available_developers: List of developer names who could potentially review.
    """

    def __init__(
        self,
        feature_name: str,
        assigned_developers: list[str],
        available_developers: list[str],
    ) -> None:
        """
        Initialize the no reviewer available error.

        Args:
            feature_name: Name of the feature without reviewers.
            assigned_developers: Names of developers assigned to development.
            available_developers: Names of developers in the team.
        """
        self.assigned_developers = assigned_developers
        self.available_developers = available_developers

        message = (
            f"No eligible code reviewers available. "
            f"Assigned developers: {assigned_developers}. "
            f"Team developers: {available_developers}. "
            f"Reviewers must not participate in development."
        )
        super().__init__(message, feature_name)


class InvalidStageError(SimulatorError):
    """
    Raised when a feature stage transition is invalid.

    This can occur when attempting to advance a feature to a stage
    that doesn't exist or when stage order is violated.
    """

    def __init__(self, message: str, current_stage: str, target_stage: str | None = None) -> None:
        """
        Initialize the invalid stage error.

        Args:
            message: Description of the invalid transition.
            current_stage: The feature's current stage.
            target_stage: The invalid target stage (if applicable).
        """
        self.current_stage = current_stage
        self.target_stage = target_stage
        super().__init__(message)
