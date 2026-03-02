"""
Tests for bug fix mechanics in the sprint simulator.

Tests cover bug probability, effort calculation, contributor eligibility,
and the collaborative bug fix workflow.
"""

import pytest

from src.config import BUG_FIX_COEFFICIENT, BUG_PROBABILITY
from src.employee import Developer, QA
from src.feature import Feature, FeatureStage


class TestBugFixProbability:
    """Tests for bug probability configuration."""

    def test_default_bug_probability(self) -> None:
        """Default bug probability is 30%."""
        assert BUG_PROBABILITY == 0.3

    def test_custom_bug_probability(self) -> None:
        """Bug probability can be customized per feature."""
        feature = Feature(
            name="Test Feature",
            stage_capacities={
                FeatureStage.DEVELOPMENT: 5.0,
                FeatureStage.TESTING: 2.0,
            },
            initial_stage=FeatureStage.DEVELOPMENT,
            bug_probability=0.8,
        )

        assert feature.bug_probability == 0.8

    def test_bug_probability_zero(self) -> None:
        """Bug probability of 0 means no bugs after testing."""
        feature = Feature(
            name="Perfect Feature",
            stage_capacities={
                FeatureStage.DEVELOPMENT: 5.0,
                FeatureStage.TESTING: 2.0,
            },
            initial_stage=FeatureStage.DEVELOPMENT,
            bug_probability=0.0,
        )

        # Complete development
        feature.work(5.0)
        assert feature.try_advance() is False
        assert feature.current_stage == FeatureStage.CODE_REVIEW

        # Complete code review
        feature.work(1.0)  # 20% of 5
        assert feature.try_advance() is False
        assert feature.current_stage == FeatureStage.TESTING

        # Complete testing - should finish (no bugs)
        feature.work(2.0)
        result = feature.try_advance()

        assert result is True
        assert feature.is_done
        assert feature.has_bugs is False

    def test_bug_probability_one(self) -> None:
        """Bug probability of 1 means always bugs after testing."""
        feature = Feature(
            name="Buggy Feature",
            stage_capacities={
                FeatureStage.DEVELOPMENT: 5.0,
                FeatureStage.TESTING: 2.0,
            },
            initial_stage=FeatureStage.DEVELOPMENT,
            bug_probability=1.0,
        )

        # Complete all stages up to testing
        feature.work(5.0)  # Development
        feature.try_advance()
        feature.work(1.0)  # Code Review
        feature.try_advance()
        feature.work(2.0)  # Testing
        result = feature.try_advance()

        assert result is False
        assert feature.current_stage == FeatureStage.BUG_FIX
        assert feature.has_bugs is True


class TestBugFixEffort:
    """Tests for bug fix effort calculation."""

    def test_default_bug_fix_coefficient(self) -> None:
        """Default bug fix coefficient is 10%."""
        assert BUG_FIX_COEFFICIENT == 0.1

    def test_bug_fix_effort_calculation(self) -> None:
        """Bug fix effort is calculated as % of development effort."""
        feature = Feature(
            name="Test Feature",
            stage_capacities={
                FeatureStage.DEVELOPMENT: 10.0,
                FeatureStage.TESTING: 3.0,
            },
            initial_stage=FeatureStage.DEVELOPMENT,
            bug_probability=1.0,  # Force bugs
        )

        # Complete all stages up to testing
        feature.work(10.0)  # Development
        feature.try_advance()
        feature.work(2.0)  # Code Review
        feature.try_advance()
        feature.work(3.0)  # Testing
        feature.try_advance()

        remaining = feature.get_remaining_efforts()
        assert FeatureStage.BUG_FIX in remaining
        assert remaining[FeatureStage.BUG_FIX] == pytest.approx(1.0)  # 10% of 10

    def test_custom_bug_fix_coefficient(self) -> None:
        """Bug fix coefficient can be customized per feature."""
        feature = Feature(
            name="Test Feature",
            stage_capacities={
                FeatureStage.DEVELOPMENT: 10.0,
                FeatureStage.TESTING: 3.0,
            },
            initial_stage=FeatureStage.DEVELOPMENT,
            bug_probability=1.0,
            bug_fix_coefficient=0.2,  # 20%
        )

        feature.work(10.0)
        feature.try_advance()
        feature.work(2.0)
        feature.try_advance()
        feature.work(3.0)
        feature.try_advance()

        remaining = feature.get_remaining_efforts()
        assert remaining[FeatureStage.BUG_FIX] == pytest.approx(2.0)  # 20% of 10


class TestBugFixContributors:
    """Tests for contributor tracking and eligibility."""

    def test_register_development_contributor(self) -> None:
        """Developer who does development is registered."""
        feature = Feature(
            name="Test",
            stage_capacities={FeatureStage.DEVELOPMENT: 5.0},
            initial_stage=FeatureStage.DEVELOPMENT,
        )

        dev = Developer(name="Alice")
        feature.register_development_contributor(dev)

        assert "Alice" in feature.development_contributors

    def test_register_testing_contributor(self) -> None:
        """QA who does testing is registered."""
        feature = Feature(
            name="Test",
            stage_capacities={
                FeatureStage.DEVELOPMENT: 5.0,
                FeatureStage.TESTING: 2.0,
            },
            initial_stage=FeatureStage.TESTING,
        )

        qa = QA(name="Bob")
        feature.register_testing_contributor(qa)

        assert "Bob" in feature.testing_contributors

    def test_contributors_frozen(self) -> None:
        """Contributor sets are immutable."""
        feature = Feature(
            name="Test",
            stage_capacities={FeatureStage.DEVELOPMENT: 5.0},
            initial_stage=FeatureStage.DEVELOPMENT,
        )

        dev = Developer(name="Alice")
        feature.register_development_contributor(dev)

        # Should return frozenset
        contributors = feature.development_contributors
        assert isinstance(contributors, frozenset)


class TestCanWorkBugFix:
    """Tests for can_be_worked_by logic in BUG_FIX stage."""

    def test_developer_contributor_can_bugfix(self) -> None:
        """Developer who did development can do bug fix."""
        feature = Feature(
            name="Test",
            stage_capacities={
                FeatureStage.DEVELOPMENT: 5.0,
                FeatureStage.TESTING: 2.0,
            },
            initial_stage=FeatureStage.DEVELOPMENT,
            bug_probability=1.0,
        )

        dev = Developer(name="Alice")
        feature.register_development_contributor(dev)

        # Advance to bug fix
        feature.work(5.0)
        feature.try_advance()
        feature.work(1.0)
        feature.try_advance()
        feature.work(2.0)
        feature.try_advance()

        assert feature.current_stage == FeatureStage.BUG_FIX
        assert feature.can_be_worked_by(dev)

    def test_qa_contributor_can_bugfix(self) -> None:
        """QA who did testing can do bug fix."""
        feature = Feature(
            name="Test",
            stage_capacities={
                FeatureStage.DEVELOPMENT: 5.0,
                FeatureStage.TESTING: 2.0,
            },
            initial_stage=FeatureStage.TESTING,
            bug_probability=1.0,
        )

        dev = Developer(name="Alice")
        qa = QA(name="Bob")

        feature.register_development_contributor(dev)
        feature.register_testing_contributor(qa)

        # Advance to bug fix
        feature.work(2.0)
        feature.try_advance()

        assert feature.current_stage == FeatureStage.BUG_FIX
        assert feature.can_be_worked_by(qa)

    def test_non_contributor_cannot_bugfix(self) -> None:
        """Employee who didn't contribute cannot do bug fix."""
        feature = Feature(
            name="Test",
            stage_capacities={
                FeatureStage.DEVELOPMENT: 5.0,
                FeatureStage.TESTING: 2.0,
            },
            initial_stage=FeatureStage.DEVELOPMENT,
            bug_probability=1.0,  # Force bugs
        )

        # Register contributors
        dev = Developer(name="Dev")
        qa = QA(name="QA")
        feature.register_development_contributor(dev)
        feature.register_testing_contributor(qa)

        # Advance to BUG_FIX
        feature.work(5.0)  # Development
        feature.try_advance()
        feature.work(1.0)  # Code review
        feature.try_advance()
        feature.work(2.0)  # Testing
        feature.try_advance()

        assert feature.current_stage == FeatureStage.BUG_FIX

        # Outsider who didn't contribute cannot work
        outsider = Developer(name="Outsider")
        assert not feature.can_be_worked_by(outsider)


class TestQARoleCapabilities:
    """Tests for QA role capabilities."""

    def test_qa_can_work_testing(self) -> None:
        """QA can work on TESTING stage."""
        qa = QA(name="QA")
        assert FeatureStage.TESTING in qa.effective_stages

    def test_qa_can_work_bug_fix(self) -> None:
        """QA can work on BUG_FIX stage."""
        qa = QA(name="QA")
        assert FeatureStage.BUG_FIX in qa.effective_stages

    def test_qa_cannot_work_development(self) -> None:
        """QA cannot work on DEVELOPMENT stage."""
        qa = QA(name="QA")
        assert FeatureStage.DEVELOPMENT not in qa.effective_stages

    def test_qa_cannot_work_code_review(self) -> None:
        """QA cannot do code review."""
        qa = QA(name="QA")
        assert FeatureStage.CODE_REVIEW not in qa.effective_stages


class TestDeveloperRoleCapabilities:
    """Tests for Developer role capabilities."""

    def test_developer_can_work_bug_fix(self) -> None:
        """Developer can work on BUG_FIX stage."""
        dev = Developer(name="Dev")
        assert FeatureStage.BUG_FIX in dev.effective_stages

    def test_developer_can_work_development(self) -> None:
        """Developer can work on DEVELOPMENT stage."""
        dev = Developer(name="Dev")
        assert FeatureStage.DEVELOPMENT in dev.effective_stages

    def test_developer_can_work_code_review(self) -> None:
        """Developer can do code review."""
        dev = Developer(name="Dev")
        assert FeatureStage.CODE_REVIEW in dev.effective_stages

    def test_developer_cannot_work_testing(self) -> None:
        """Developer cannot work on TESTING stage."""
        dev = Developer(name="Dev")
        assert FeatureStage.TESTING not in dev.effective_stages
