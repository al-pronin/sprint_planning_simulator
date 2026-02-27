"""
Unit tests for Employee classes.

Tests cover employee capabilities, productivity, and stage eligibility.
"""

import pytest

from src.employee import Developer, QA, SystemAnalyst
from src.feature import FeatureStage


class TestEmployeeBasics:
    """Tests for basic employee functionality."""

    def test_employee_initialization(self, developer: Developer) -> None:
        """Employee initializes with correct attributes."""
        assert developer.name == "Dev"
        assert developer.productivity_per_day == 8.0

    def test_productivity_per_hour(self, developer: Developer) -> None:
        """Hourly productivity is daily productivity divided by 8."""
        expected = 8.0 / 8  # 1.0
        assert developer.productivity_per_hour == pytest.approx(expected)

    def test_custom_productivity(self) -> None:
        """Employee can have custom productivity."""
        dev = Developer(name="FastDev", productivity_per_day=16.0)
        assert dev.productivity_per_hour == pytest.approx(2.0)

    def test_tick_reset(self, developer: Developer) -> None:
        """Reset tick clears work state."""
        developer._worked_this_tick = True
        developer.current_task_name = "Something"
        developer.reset_tick()

        assert not developer.has_worked
        assert developer.current_task_name is None


class TestDeveloperCapabilities:
    """Tests for Developer stage capabilities."""

    def test_developer_can_work_development(self, developer: Developer) -> None:
        """Developer can work on DEVELOPMENT stage."""
        assert developer.can_work_stage(FeatureStage.DEVELOPMENT)

    def test_developer_can_work_code_review(self, developer: Developer) -> None:
        """Developer can work on CODE_REVIEW stage."""
        assert developer.can_work_stage(FeatureStage.CODE_REVIEW)

    def test_developer_cannot_work_analytics(self, developer: Developer) -> None:
        """Developer cannot work on ANALYTICS stage."""
        assert not developer.can_work_stage(FeatureStage.ANALYTICS)

    def test_developer_cannot_work_testing(self, developer: Developer) -> None:
        """Developer cannot work on TESTING stage."""
        assert not developer.can_work_stage(FeatureStage.TESTING)


class TestAnalystCapabilities:
    """Tests for SystemAnalyst stage capabilities."""

    def test_analyst_can_work_analytics(self, analyst: SystemAnalyst) -> None:
        """Analyst can work on ANALYTICS stage."""
        assert analyst.can_work_stage(FeatureStage.ANALYTICS)

    def test_analyst_cannot_work_development(self, analyst: SystemAnalyst) -> None:
        """Analyst cannot work on DEVELOPMENT stage."""
        assert not analyst.can_work_stage(FeatureStage.DEVELOPMENT)

    def test_analyst_cannot_work_code_review(self, analyst: SystemAnalyst) -> None:
        """Analyst cannot work on CODE_REVIEW stage."""
        assert not analyst.can_work_stage(FeatureStage.CODE_REVIEW)


class TestQACapabilities:
    """Tests for QA stage capabilities."""

    def test_qa_can_work_testing(self, qa_engineer: QA) -> None:
        """QA can work on TESTING stage."""
        assert qa_engineer.can_work_stage(FeatureStage.TESTING)

    def test_qa_cannot_work_development(self, qa_engineer: QA) -> None:
        """QA cannot work on DEVELOPMENT stage."""
        assert not qa_engineer.can_work_stage(FeatureStage.DEVELOPMENT)

    def test_qa_cannot_work_code_review(self, qa_engineer: QA) -> None:
        """QA cannot work on CODE_REVIEW stage."""
        assert not qa_engineer.can_work_stage(FeatureStage.CODE_REVIEW)


class TestEmployeeWork:
    """Tests for employee work actions."""

    def test_employee_work_sets_state(
        self, developer: Developer, dev_only_feature
    ) -> None:
        """Working on a feature updates employee state."""
        dev_only_feature.assign(developer)
        developer.work(dev_only_feature)

        assert developer.has_worked
        assert developer.current_task_name == dev_only_feature.name

    def test_employee_idle_sets_state(self, developer: Developer) -> None:
        """Idling updates employee state."""
        developer.idle()

        assert not developer.has_worked
        assert developer.current_task_name == "Idle"

    def test_work_registers_development_contributor(
        self, developer: Developer, dev_only_feature
    ) -> None:
        """Working on development registers employee as contributor."""
        dev_only_feature.assign(developer)
        developer.work(dev_only_feature)

        assert developer.name in dev_only_feature.development_contributors
