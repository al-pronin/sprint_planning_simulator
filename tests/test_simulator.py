"""
Unit tests for SprintSimulator.

Tests cover simulation execution, history recording, and validation.
"""

import pytest

from src.employee import Developer, QA, SystemAnalyst
from src.exceptions import PlanningError
from src.feature import Feature, FeatureStage
from src.simulator import SprintSimulator
from src.strategy import SimpleAssignmentStrategy


class TestSimulatorBasics:
    """Tests for basic simulator functionality."""

    def test_simulator_initialization(
        self,
        developer: Developer,
        sample_feature: Feature,
        simple_strategy: SimpleAssignmentStrategy,
    ) -> None:
        """Simulator initializes with correct attributes."""
        sample_feature.assign(developer)

        # Add external reviewer
        dev2 = Developer(name="Reviewer")

        simulator = SprintSimulator(
            employees=[developer, dev2],
            features=[sample_feature],
            assignment_strategy=simple_strategy,
        )

        assert len(simulator.employees) == 2
        assert len(simulator.features) == 1
        assert simulator.history is not None

    def test_simulator_records_history(
        self,
        sample_feature: Feature,
        analyst: SystemAnalyst,
        developer: Developer,
        qa_engineer: QA,
        simple_strategy: SimpleAssignmentStrategy,
    ) -> None:
        """Simulator correctly records history after each tick."""
        sample_feature.assign(analyst)
        sample_feature.assign(developer)
        sample_feature.assign(qa_engineer)

        # Add external reviewer for code review
        dev2 = Developer(name="Reviewer")

        simulator = SprintSimulator(
            employees=[analyst, developer, qa_engineer, dev2],
            features=[sample_feature],
            assignment_strategy=simple_strategy,
            validate=False,
        )

        # Run for 1 day
        simulator.run(max_days=1)

        # 8 hours in a day, so 8 ticks
        assert len(simulator.history.history) == 8

    def test_first_tick_snapshot(
        self,
        sample_feature: Feature,
        analyst: SystemAnalyst,
        developer: Developer,
        qa_engineer: QA,
        simple_strategy: SimpleAssignmentStrategy,
    ) -> None:
        """First tick snapshot contains correct data."""
        sample_feature.assign(analyst)
        sample_feature.assign(developer)
        sample_feature.assign(qa_engineer)

        dev2 = Developer(name="Reviewer")

        simulator = SprintSimulator(
            employees=[analyst, developer, qa_engineer, dev2],
            features=[sample_feature],
            assignment_strategy=simple_strategy,
        )

        simulator.run(max_days=1)

        first_tick = simulator.history.history[0]
        assert first_tick.tick.day == 1
        assert first_tick.tick.hour == 1


class TestSimulatorValidation:
    """Tests for simulator validation."""

    def test_empty_features_raises_error(self, developer: Developer) -> None:
        """Empty features list raises PlanningError."""
        with pytest.raises(PlanningError):
            SprintSimulator(
                employees=[developer],
                features=[],
                assignment_strategy=SimpleAssignmentStrategy(),
            )

    def test_empty_employees_raises_error(self, sample_feature: Feature) -> None:
        """Empty employees list raises PlanningError."""
        with pytest.raises(PlanningError):
            SprintSimulator(
                employees=[],
                features=[sample_feature],
                assignment_strategy=SimpleAssignmentStrategy(),
            )

    def test_feature_without_assignees_raises_error(
        self, developer: Developer
    ) -> None:
        """Feature without assignees raises PlanningError."""
        feature = Feature(
            name="Unassigned",
            stage_capacities={FeatureStage.DEVELOPMENT: 4.0},
            initial_stage=FeatureStage.DEVELOPMENT,
        )

        with pytest.raises(PlanningError):
            SprintSimulator(
                employees=[developer],
                features=[feature],
                assignment_strategy=SimpleAssignmentStrategy(),
            )

    def test_zero_productivity_raises_error(self) -> None:
        """Employee with zero productivity raises PlanningError."""
        feature = Feature(
            name="Test",
            stage_capacities={FeatureStage.DEVELOPMENT: 4.0},
            initial_stage=FeatureStage.DEVELOPMENT,
        )
        dev = Developer(name="Dev", productivity_per_day=0.0)
        dev2 = Developer(name="Dev2")

        feature.assign(dev)

        with pytest.raises(PlanningError):
            SprintSimulator(
                employees=[dev, dev2],
                features=[feature],
                assignment_strategy=SimpleAssignmentStrategy(),
            )


class TestSimulatorFeatureCompletion:
    """Tests for feature completion during simulation."""

    def test_all_features_complete_early(self) -> None:
        """Simulation stops when all features are done."""
        feature = Feature(
            name="Quick Task",
            stage_capacities={FeatureStage.DEVELOPMENT: 0.5},
            initial_stage=FeatureStage.DEVELOPMENT,
        )

        dev1 = Developer(name="Dev1", productivity_per_day=16.0)
        dev2 = Developer(name="Dev2")  # External reviewer - NOT assigned

        feature.assign(dev1)
        # dev2 is NOT assigned - external reviewer

        simulator = SprintSimulator(
            employees=[dev1, dev2],
            features=[feature],
            assignment_strategy=SimpleAssignmentStrategy(),
        )

        simulator.run(max_days=10)

        # Should complete in less than 10 days
        assert feature.is_done
        assert len(simulator.history.history) < 80  # 10 days * 8 hours

    def test_max_days_limits_simulation(self) -> None:
        """Simulation stops at max days even with incomplete features."""
        feature = Feature(
            name="Huge Task",
            stage_capacities={FeatureStage.DEVELOPMENT: 1000.0},
            initial_stage=FeatureStage.DEVELOPMENT,
        )

        dev1 = Developer(name="Dev1")
        dev2 = Developer(name="Dev2")  # External reviewer

        feature.assign(dev1)
        # dev2 is NOT assigned - external reviewer

        simulator = SprintSimulator(
            employees=[dev1, dev2],
            features=[feature],
            assignment_strategy=SimpleAssignmentStrategy(),
        )

        simulator.run(max_days=2)

        # Should have exactly 2 days * 8 hours = 16 ticks
        assert len(simulator.history.history) == 16
        assert not feature.is_done


class TestSimulatorDefensiveCopy:
    """Tests for defensive copying of features."""

    def test_features_list_is_copied(self) -> None:
        """Modifying original features list doesn't affect simulator."""
        feature = Feature(
            name="Test",
            stage_capacities={FeatureStage.DEVELOPMENT: 1.0},
            initial_stage=FeatureStage.DEVELOPMENT,
        )

        dev1 = Developer(name="Dev1")
        dev2 = Developer(name="Dev2")

        feature.assign(dev1)

        features_list = [feature]
        simulator = SprintSimulator(
            employees=[dev1, dev2],
            features=features_list,
            assignment_strategy=SimpleAssignmentStrategy(),
        )

        # Modify original list
        features_list.clear()

        # Simulator should still have the feature
        assert len(simulator.features) == 1
