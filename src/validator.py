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

    Example:
        >>> validator = SprintValidator()
        >>> validator.validate(features, employees)
        True  # or raises PlanningError
    """

    def validate(
        self,
        features: list[Feature],
        employees: list[Employee],
    ) -> bool:
        """
        Validate the sprint configuration.

        Runs all validation checks and raises on the first error found.

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

        return True

    def _validate_features(self, features: list[Feature]) -> None:
        """
        Validate feature configurations.

        Args:
            features: Features to validate.

        Raises:
            PlanningError: If any feature has invalid configuration.
        """
        if not features:
            raise PlanningError("No features provided for simulation")

        for feature in features:
            if not feature.assignees:
                raise PlanningError(
                    f"Feature has no assigned employees",
                    feature_name=feature.name,
                )

    def _validate_employees(self, employees: list[Employee]) -> None:
        """
        Validate employee configurations.

        Args:
            employees: Employees to validate.

        Raises:
            PlanningError: If any employee has invalid configuration.
        """
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

        For each feature with a CODE_REVIEW stage, checks that at least
        one developer exists who:
        1. Is a Developer (can do code review)
        2. Is NOT assigned to the feature's development

        Args:
            features: Features to validate.
            employees: Available employees.

        Raises:
            NoReviewerAvailableError: If a feature lacks eligible reviewers.
        """
        # Get all developers in the team
        team_developers = [e for e in employees if isinstance(e, Developer)]

        for feature in features:
            # Only check features with code review stage
            if not feature.has_code_review:
                continue

            # Find developers assigned to this feature (who did development)
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

        Args:
            features: Features to check.
            employees: Team members to check.

        Returns:
            List of warning messages.
        """
        warnings = []

        # Check for underutilized employees
        for employee in employees:
            has_work = False
            for feature in features:
                if employee in feature.assignees:
                    has_work = True
                    break
                # Check if employee can work on any stage
                for stage in feature.STAGE_ORDER:
                    if stage in feature.get_remaining_efforts():
                        if employee.can_work_stage(stage):
                            # For code review, check eligibility
                            if stage == FeatureStage.CODE_REVIEW:
                                if employee.name not in feature.development_contributors:
                                    has_work = True
                                    break
                            else:
                                has_work = True
                                break
                if has_work:
                    break

            if not has_work:
                warnings.append(
                    f"Employee {employee.name} may have no eligible work"
                )

        # Check for features with only one developer (single point of failure)
        for feature in features:
            dev_count = sum(1 for e in feature.assignees if isinstance(e, Developer))
            if feature.has_code_review and dev_count == 1:
                warnings.append(
                    f"Feature {feature.name} has only one developer assigned; "
                    f"external reviewer will be required"
                )

        return warnings
