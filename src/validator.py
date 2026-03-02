"""
Validation module for the sprint simulator.

This module provides validation logic to check sprint configuration
before simulation starts, catching planning errors early.
"""

from __future__ import annotations

from src.employee import Developer, Employee
from src.exceptions import NoReviewerAvailableError, PlanningError
from src.feature import Feature, FeatureStage


class SprintValidator:
    """
    Validator for sprint configuration before simulation.

    Performs pre-flight checks to ensure the sprint can be simulated
    successfully, catching configuration errors early with clear messages.
    """

    def validate(
        self,
        features: list[Feature],
        employees: list[Employee],
    ) -> bool:
        """
        Validate the sprint configuration.

        Args:
            features: Features to be simulated.
            employees: Team members in the sprint.

        Returns:
            True if validation passes.

        Raises:
            PlanningError: If any validation check fails.
        """
        self._validate_features(features)
        self._validate_employees(employees)
        self._validate_code_review_coverage(features, employees)
        # Note: No bug fix validation per requirements

        return True

    def _validate_features(self, features: list[Feature]) -> None:
        """Validate feature configurations."""
        if not features:
            raise PlanningError("No features provided for simulation")

        for feature in features:
            if not feature.assignees:
                raise PlanningError(
                    f"Feature has no assigned employees",
                    feature_name=feature.name,
                )

    def _validate_employees(self, employees: list[Employee]) -> None:
        """Validate employee configurations."""
        if not employees:
            raise PlanningError("No employees provided for simulation")

        for employee in employees:
            if employee.productivity_per_day <= 0:
                raise PlanningError(
                    f"Employee {employee.name} has invalid productivity: "
                    f"{employee.productivity_per_day}"
                )

    def _validate_code_review_coverage(
        self,
        features: list[Feature],
        employees: list[Employee],
    ) -> None:
        """
        Validate that all features with code review have eligible reviewers.

        For each feature with CODE_REVIEW stage, checks that at least
        one developer exists who is NOT assigned to development.
        """
        team_developers = [e for e in employees if isinstance(e, Developer)]

        for feature in features:
            # Only check features with code review stage
            if not feature.has_code_review:
                continue

            # Find developers assigned to this feature
            assigned_dev_names = {
                e.name for e in feature.assignees if isinstance(e, Developer)
            }

            # Find eligible reviewers (not assigned to this feature)
            eligible_reviewers = [
                dev for dev in team_developers
                if dev.name not in assigned_dev_names
            ]

            if not eligible_reviewers:
                raise NoReviewerAvailableError(
                    feature_name=feature.name,
                    assigned_developers=list(assigned_dev_names),
                    available_developers=[d.name for d in team_developers],
                )

    def get_validation_warnings(
        self,
        features: list[Feature],
        employees: list[Employee],
    ) -> list[str]:
        """
        Get non-fatal warnings about the sprint configuration.

        These warnings indicate potential issues that don't prevent
        simulation but may indicate suboptimal planning.
        """
        warnings = []

        # Check for features with only one developer
        for feature in features:
            dev_count = sum(1 for e in feature.assignees if isinstance(e, Developer))
            if feature.has_code_review and dev_count == 1:
                warnings.append(
                    f"Feature {feature.name} has only one developer assigned; "
                    f"external reviewer will be required"
                )

        # Check for QA assignment
        for feature in features:
            if FeatureStage.TESTING in feature.get_remaining_efforts():
                qa_assigned = any(
                    e.can_work_stage(FeatureStage.TESTING)
                    for e in feature.assignees
                )
                if not qa_assigned:
                    warnings.append(
                        f"Feature {feature.name} has testing stage but no QA assigned"
                    )

        return warnings
