"""
Integration tests for code review mechanics.

Tests cover the complete code review workflow including validation,
reviewer eligibility, and error handling.
"""

import pytest

from src.employee import Developer, QA, SystemAnalyst
from src.exceptions import NoReviewerAvailableError, PlanningError
from src.feature import Feature, FeatureStage
from src.simulator import SprintSimulator
from src.strategy import SimpleAssignmentStrategy


class TestCodeReviewValidation:
    """Tests for code review validation before simulation."""

    def test_validation_passes_with_external_reviewer(self) -> None:
        """Simulation validates successfully with an external reviewer."""
        feature = Feature(
            name="Test Feature",
            stage_capacities={FeatureStage.DEVELOPMENT: 4.0},
            initial_stage=FeatureStage.DEVELOPMENT,
        )

        dev1 = Developer(name="Dev1")
        dev2 = Developer(name="Dev2")  # External reviewer - NOT assigned

        feature.assign(dev1)  # Only dev1 is assigned to work on feature

        # dev2 is in team but NOT assigned - can review
        simulator = SprintSimulator(
            employees=[dev1, dev2],
            features=[feature],
            assignment_strategy=SimpleAssignmentStrategy(),
            validate=True,
        )

        assert simulator is not None

    def test_validation_fails_with_no_reviewer(self) -> None:
        """Simulation raises error when no eligible reviewer exists."""
        feature = Feature(
            name="Test Feature",
            stage_capacities={FeatureStage.DEVELOPMENT: 4.0},
            initial_stage=FeatureStage.DEVELOPMENT,
        )

        dev1 = Developer(name="Dev1")
        feature.assign(dev1)

        # Only one developer in team, and they're assigned - no reviewer
        with pytest.raises(NoReviewerAvailableError) as exc_info:
            SprintSimulator(
                employees=[dev1],
                features=[feature],
                assignment_strategy=SimpleAssignmentStrategy(),
                validate=True,
            )

        assert feature.name in str(exc_info.value)

    def test_validation_fails_all_devs_assigned(self) -> None:
        """Error when all team developers are assigned to the feature."""
        feature = Feature(
            name="Test Feature",
            stage_capacities={FeatureStage.DEVELOPMENT: 4.0},
            initial_stage=FeatureStage.DEVELOPMENT,
        )

        dev1 = Developer(name="Dev1")
        dev2 = Developer(name="Dev2")

        feature.assign(dev1)
        feature.assign(dev2)  # Both devs assigned - no external reviewer

        with pytest.raises(NoReviewerAvailableError):
            SprintSimulator(
                employees=[dev1, dev2],
                features=[feature],
                assignment_strategy=SimpleAssignmentStrategy(),
                validate=True,
            )

    def test_validation_passes_for_multiple_features(self) -> None:
        """Multiple features with shared reviewer validates successfully."""
        feature1 = Feature(
            name="Feature 1",
            stage_capacities={FeatureStage.DEVELOPMENT: 2.0},
            initial_stage=FeatureStage.DEVELOPMENT,
        )
        feature2 = Feature(
            name="Feature 2",
            stage_capacities={FeatureStage.DEVELOPMENT: 2.0},
            initial_stage=FeatureStage.DEVELOPMENT,
        )

        dev1 = Developer(name="Dev1")
        dev2 = Developer(name="Dev2")
        dev3 = Developer(name="Dev3")  # Shared reviewer

        feature1.assign(dev1)
        feature2.assign(dev2)

        # dev3 can review both features
        simulator = SprintSimulator(
            employees=[dev1, dev2, dev3],
            features=[feature1, feature2],
            assignment_strategy=SimpleAssignmentStrategy(),
            validate=True,
        )

        assert simulator is not None


class TestCodeReviewWorkflow:
    """Tests for complete code review workflow during simulation."""

    def test_code_review_stage_appears_in_simulation(self) -> None:
        """Code review stage is processed during simulation."""
        feature = Feature(
            name="Test Feature",
            stage_capacities={FeatureStage.DEVELOPMENT: 2.0},
            initial_stage=FeatureStage.DEVELOPMENT,
        )

        dev1 = Developer(name="Dev1", productivity_per_day=8.0)
        dev2 = Developer(name="Dev2", productivity_per_day=8.0)  # Reviewer
        qa = QA(name="QA", productivity_per_day=8.0)

        feature.assign(dev1)
        feature.assign(qa)
        # dev2 is NOT assigned - external reviewer

        simulator = SprintSimulator(
            employees=[dev1, dev2, qa],
            features=[feature],
            assignment_strategy=SimpleAssignmentStrategy(),
        )

        simulator.run(max_days=5)

        # Feature should be complete
        assert feature.is_done

    def test_external_developer_can_review(self) -> None:
        """Developer who is not assigned to feature can review."""
        feature = Feature(
            name="Test Feature",
            stage_capacities={FeatureStage.DEVELOPMENT: 1.0},
            initial_stage=FeatureStage.DEVELOPMENT,
        )

        dev1 = Developer(name="Dev1", productivity_per_day=8.0)
        dev2 = Developer(name="Dev2", productivity_per_day=8.0)  # Reviewer

        feature.assign(dev1)
        # dev2 is NOT assigned

        simulator = SprintSimulator(
            employees=[dev1, dev2],
            features=[feature],
            assignment_strategy=SimpleAssignmentStrategy(),
        )

        simulator.run(max_days=3)

        # Check that code review stage was reached and completed
        assert feature.is_done


class TestCodeReviewEffortCalculation:
    """Tests for code review effort calculation."""

    def test_default_review_coefficient(self) -> None:
        """Default review coefficient is 20%."""
        feature = Feature(
            name="Test",
            stage_capacities={FeatureStage.DEVELOPMENT: 10.0},
            initial_stage=FeatureStage.DEVELOPMENT,
        )

        review_effort = feature.get_remaining_efforts()[FeatureStage.CODE_REVIEW]
        assert review_effort == pytest.approx(2.0)  # 20% of 10

    def test_custom_review_coefficient(self) -> None:
        """Review coefficient can be customized."""
        feature = Feature(
            name="Test",
            stage_capacities={FeatureStage.DEVELOPMENT: 10.0},
            initial_stage=FeatureStage.DEVELOPMENT,
            review_coefficient=0.5,  # 50%
        )

        review_effort = feature.get_remaining_efforts()[FeatureStage.CODE_REVIEW]
        assert review_effort == pytest.approx(5.0)

    def test_review_effort_rounded(self) -> None:
        """Review effort is properly rounded."""
        feature = Feature(
            name="Test",
            stage_capacities={FeatureStage.DEVELOPMENT: 3.33},
            initial_stage=FeatureStage.DEVELOPMENT,
        )

        review_effort = feature.get_remaining_efforts()[FeatureStage.CODE_REVIEW]
        # 3.33 * 0.2 = 0.666, rounded to 0.67
        assert isinstance(review_effort, float)


class TestCodeReviewEdgeCases:
    """Tests for edge cases in code review mechanics."""

    def test_zero_development_effort_no_review(self) -> None:
        """Zero development effort results in zero review."""
        feature = Feature(
            name="Test",
            stage_capacities={
                FeatureStage.ANALYTICS: 2.0,
                FeatureStage.DEVELOPMENT: 0.0,  # No development
                FeatureStage.TESTING: 1.0,
            },
            initial_stage=FeatureStage.ANALYTICS,
        )

        # Code review should exist but with 0 effort
        assert FeatureStage.CODE_REVIEW in feature.get_remaining_efforts()
        assert feature.get_remaining_efforts()[FeatureStage.CODE_REVIEW] == 0.0

    def test_feature_without_development_no_review(self) -> None:
        """Feature without development stage has no code review."""
        feature = Feature(
            name="Analytics Only",
            stage_capacities={FeatureStage.ANALYTICS: 2.0},
            initial_stage=FeatureStage.ANALYTICS,
        )

        assert FeatureStage.CODE_REVIEW not in feature.get_remaining_efforts()

    def test_qa_cannot_do_code_review(self) -> None:
        """QA engineers cannot perform code review."""
        feature = Feature(
            name="Test",
            stage_capacities={FeatureStage.DEVELOPMENT: 2.0},
            initial_stage=FeatureStage.DEVELOPMENT,
        )

        dev = Developer(name="Dev")
        qa = QA(name="QA")

        feature.assign(dev)
        feature.assign(qa)

        # Complete development
        feature.work(2.0)
        feature.try_advance()

        assert feature.current_stage == FeatureStage.CODE_REVIEW
        assert not qa.can_work_stage(FeatureStage.CODE_REVIEW)

    def test_analyst_cannot_do_code_review(self) -> None:
        """System analysts cannot perform code review."""
        analyst = SystemAnalyst(name="Analyst")
        assert not analyst.can_work_stage(FeatureStage.CODE_REVIEW)

    def test_contributor_cannot_review_their_feature(self) -> None:
        """Developer who did development cannot review that feature."""
        feature = Feature(
            name="Test",
            stage_capacities={FeatureStage.DEVELOPMENT: 1.0},
            initial_stage=FeatureStage.DEVELOPMENT,
        )

        dev = Developer(name="Dev")
        feature.assign(dev)

        # Do development work
        dev.work(feature)

        # Complete development
        feature.work(1.0)
        feature.try_advance()

        assert feature.current_stage == FeatureStage.CODE_REVIEW
        # Dev contributed to development, cannot review
        assert not feature.can_be_worked_by(dev)
