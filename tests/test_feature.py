"""
Unit tests for the Feature class.

Tests cover feature lifecycle, stage transitions, and code review mechanics.
"""

import pytest

from src.employee import Developer, SystemAnalyst
from src.feature import Feature, FeatureStage


class TestFeatureBasics:
    """Tests for basic feature functionality."""

    def test_feature_initialization(self, sample_feature: Feature) -> None:
        """Feature initializes with correct stage and remaining efforts."""
        assert sample_feature.name == "Test Feature"
        assert sample_feature.current_stage == FeatureStage.ANALYTICS
        assert not sample_feature.is_done

    def test_feature_work_reduces_effort(self, sample_feature: Feature) -> None:
        """Working on a feature reduces remaining effort."""
        initial = sample_feature.get_remaining_efforts()[FeatureStage.ANALYTICS]
        sample_feature.work(0.5)
        remaining = sample_feature.get_remaining_efforts()[FeatureStage.ANALYTICS]

        assert remaining == pytest.approx(initial - 0.5)

    def test_feature_effort_does_not_go_negative(self, sample_feature: Feature) -> None:
        """Effort cannot go below zero."""
        sample_feature.work(100.0)  # Way more than needed
        remaining = sample_feature.get_remaining_efforts()[FeatureStage.ANALYTICS]

        assert remaining == 0.0

    def test_total_capacity_calculation(self, sample_feature: Feature) -> None:
        """Total capacity includes all stages including auto-added code review."""
        # Analytics: 2.0 + Development: 4.0 + Code Review: 0.8 + Testing: 2.0
        expected = 2.0 + 4.0 + 0.8 + 2.0
        assert sample_feature.total_capacity == pytest.approx(expected)


class TestFeatureStageAdvancement:
    """Tests for stage transitions."""

    def test_feature_advancement_to_next_stage(
        self, sample_feature: Feature
    ) -> None:
        """Feature moves to next stage when current is finished."""
        # Finish analytics
        sample_feature.work(2.0)
        is_done = sample_feature.try_advance()

        assert not is_done
        assert sample_feature.current_stage == FeatureStage.DEVELOPMENT

    def test_feature_completion_after_all_stages(
        self, sample_feature: Feature
    ) -> None:
        """Feature is completed after all stages are done."""
        # Analytics
        sample_feature.work(2.0)
        sample_feature.try_advance()

        # Development
        sample_feature.work(4.0)
        sample_feature.try_advance()

        # Code Review (auto-added)
        sample_feature.work(0.8)
        sample_feature.try_advance()

        # Testing
        sample_feature.work(2.0)
        is_done = sample_feature.try_advance()

        assert is_done
        assert sample_feature.is_done

    def test_feature_does_not_advance_with_remaining_effort(
        self, sample_feature: Feature
    ) -> None:
        """Feature stays in current stage if effort remains."""
        sample_feature.work(1.0)  # Only half of analytics
        result = sample_feature.try_advance()

        assert not result
        assert sample_feature.current_stage == FeatureStage.ANALYTICS


class TestFeatureCodeReview:
    """Tests for code review mechanics."""

    def test_code_review_auto_added(self, sample_feature: Feature) -> None:
        """Code review is automatically added when development exists."""
        efforts = sample_feature.get_remaining_efforts()

        assert FeatureStage.CODE_REVIEW in efforts
        assert efforts[FeatureStage.CODE_REVIEW] == pytest.approx(0.8)  # 20% of 4.0

    def test_code_review_not_added_without_development(self) -> None:
        """Code review is not added if feature has no development stage."""
        feature = Feature(
            name="Analytics Only",
            stage_capacities={FeatureStage.ANALYTICS: 2.0},
            initial_stage=FeatureStage.ANALYTICS,
        )

        assert FeatureStage.CODE_REVIEW not in feature.get_remaining_efforts()

    def test_custom_review_coefficient(self) -> None:
        """Review coefficient can be customized per feature."""
        feature = Feature(
            name="Custom Review",
            stage_capacities={FeatureStage.DEVELOPMENT: 10.0},
            initial_stage=FeatureStage.DEVELOPMENT,
            review_coefficient=0.3,  # 30%
        )

        review_effort = feature.get_remaining_efforts()[FeatureStage.CODE_REVIEW]
        assert review_effort == pytest.approx(3.0)  # 30% of 10.0

    def test_explicit_code_review_preserved(self) -> None:
        """Explicitly provided code review capacity is preserved."""
        feature = Feature(
            name="Explicit Review",
            stage_capacities={
                FeatureStage.DEVELOPMENT: 10.0,
                FeatureStage.CODE_REVIEW: 5.0,  # Explicit value
            },
            initial_stage=FeatureStage.DEVELOPMENT,
        )

        # Should use the explicit value, not auto-calculate
        review_effort = feature.get_remaining_efforts()[FeatureStage.CODE_REVIEW]
        assert review_effort == 5.0


class TestFeatureAssignees:
    """Tests for feature assignment logic."""

    def test_assign_employee(self, sample_feature: Feature, developer: Developer) -> None:
        """Employee can be assigned to a feature."""
        sample_feature.assign(developer)

        assert developer in sample_feature.assignees

    def test_assign_same_employee_twice(self, sample_feature: Feature, developer: Developer) -> None:
        """Assigning same employee twice doesn't duplicate."""
        sample_feature.assign(developer)
        sample_feature.assign(developer)

        assert len(sample_feature.assignees) == 1

    def test_development_contributor_tracking(
        self, dev_only_feature: Feature, developer: Developer
    ) -> None:
        """Feature tracks developers who contributed to development."""
        dev_only_feature.assign(developer)
        developer.work(dev_only_feature)

        assert developer.name in dev_only_feature.development_contributors


class TestFeatureWorkEligibility:
    """Tests for can_be_worked_by logic."""

    def test_unassigned_employee_cannot_work(
        self, sample_feature: Feature, developer: Developer
    ) -> None:
        """Unassigned employee cannot work on feature."""
        assert not sample_feature.can_be_worked_by(developer)

    def test_assigned_employee_can_work_on_matching_stage(
        self, sample_feature: Feature, analyst: SystemAnalyst
    ) -> None:
        """Assigned employee can work on their eligible stage."""
        sample_feature.assign(analyst)

        assert sample_feature.can_be_worked_by(analyst)

    def test_employee_cannot_work_on_wrong_stage(
        self, sample_feature: Feature, developer: Developer
    ) -> None:
        """Developer cannot work on analytics stage."""
        sample_feature.assign(developer)

        # Feature is in ANALYTICS, developer can't work on that
        assert not sample_feature.can_be_worked_by(developer)

    def test_developer_cannot_review_own_code(
        self, dev_only_feature: Feature, developer: Developer
    ) -> None:
        """Developer who did development cannot do code review."""
        dev_only_feature.assign(developer)

        # Developer does development work (this registers them as contributor)
        developer.work(dev_only_feature)

        # Complete remaining development
        dev_only_feature.work(5.0)
        dev_only_feature.try_advance()

        assert dev_only_feature.current_stage == FeatureStage.CODE_REVIEW
        # Developer contributed to development, cannot review
        assert not dev_only_feature.can_be_worked_by(developer)

    def test_other_developer_can_review(
        self, dev_only_feature: Feature, developer: Developer, developer_two: Developer
    ) -> None:
        """Developer who didn't do development can do code review."""
        dev_only_feature.assign(developer)
        # developer_two is NOT assigned - they're an external reviewer

        # First developer does development work (registers as contributor)
        developer.work(dev_only_feature)

        # Complete development
        dev_only_feature.work(5.0)
        dev_only_feature.try_advance()

        assert dev_only_feature.current_stage == FeatureStage.CODE_REVIEW
        # developer_two didn't contribute to development, can review
        # Even though not assigned, they can review (external reviewer)
        assert dev_only_feature.can_be_worked_by(developer_two)

    def test_completed_feature_cannot_be_worked(
        self, sample_feature: Feature, analyst: SystemAnalyst
    ) -> None:
        """Completed feature rejects all work."""
        sample_feature.assign(analyst)

        # Complete all stages
        for _ in range(10):
            sample_feature.work(10.0)
            sample_feature.try_advance()

        assert sample_feature.is_done
        assert not sample_feature.can_be_worked_by(analyst)


class TestFeatureStageOrder:
    """Tests for stage ordering."""

    def test_stage_order_includes_code_review(self) -> None:
        """Stage order includes CODE_REVIEW between DEVELOPMENT and TESTING."""
        order = Feature.STAGE_ORDER

        assert FeatureStage.CODE_REVIEW in order
        dev_index = order.index(FeatureStage.DEVELOPMENT)
        review_index = order.index(FeatureStage.CODE_REVIEW)
        test_index = order.index(FeatureStage.TESTING)

        assert review_index > dev_index
        assert review_index < test_index


class TestFeatureDisplayNames:
    """Tests for display name formatting."""

    def test_stage_display_names(self) -> None:
        """All stages have proper display names."""
        assert FeatureStage.ANALYTICS.display_name() == "Analytics"
        assert FeatureStage.DEVELOPMENT.display_name() == "Development"
        assert FeatureStage.CODE_REVIEW.display_name() == "Code Review"
        assert FeatureStage.TESTING.display_name() == "Testing"
