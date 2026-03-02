"""
Test fixtures for the sprint simulator.
"""

import pytest

from src.employee import Developer, QA, SystemAnalyst
from src.feature import Feature, FeatureStage
from src.strategy import SimpleAssignmentStrategy


@pytest.fixture
def developer() -> Developer:
    """Standard developer fixture."""
    return Developer(name="Dev", productivity_per_day=8.0)


@pytest.fixture
def developer_two() -> Developer:
    """Second developer for code review."""
    return Developer(name="Dev2", productivity_per_day=8.0)


@pytest.fixture
def qa_engineer() -> QA:
    """Standard QA engineer fixture."""
    return QA(name="QA", productivity_per_day=8.0)


@pytest.fixture
def qa_engineer_two() -> QA:
    """Second QA for testing."""
    return QA(name="QA2", productivity_per_day=8.0)


@pytest.fixture
def analyst() -> SystemAnalyst:
    """Standard analyst fixture."""
    return SystemAnalyst(name="Analyst", productivity_per_day=8.0)


@pytest.fixture
def simple_strategy() -> SimpleAssignmentStrategy:
    """Simple assignment strategy."""
    return SimpleAssignmentStrategy()


@pytest.fixture
def sample_feature() -> Feature:
    """Feature with all stages, no bugs for deterministic tests."""
    return Feature(
        name="Test Feature",
        stage_capacities={
            FeatureStage.ANALYTICS: 2.0,
            FeatureStage.DEVELOPMENT: 4.0,
            FeatureStage.TESTING: 2.0,
        },
        initial_stage=FeatureStage.ANALYTICS,
        bug_probability=0.0,  # No bugs for deterministic tests
    )


@pytest.fixture
def dev_only_feature() -> Feature:
    """Feature starting at development."""
    return Feature(
        name="Dev Only Feature",
        stage_capacities={
            FeatureStage.DEVELOPMENT: 5.0,
            FeatureStage.TESTING: 2.0,
        },
        initial_stage=FeatureStage.DEVELOPMENT,
    )


@pytest.fixture
def feature_no_bugs(developer: Developer, qa_engineer: QA) -> Feature:
    """Feature guaranteed to have no bugs."""
    feature = Feature(
        name="Clean Feature",
        stage_capacities={
            FeatureStage.DEVELOPMENT: 5.0,
            FeatureStage.TESTING: 2.0,
        },
        initial_stage=FeatureStage.DEVELOPMENT,
        bug_probability=0.0,
    )
    feature.assign(developer)
    feature.assign(qa_engineer)
    return feature


@pytest.fixture
def feature_with_bugs(developer: Developer, qa_engineer: QA) -> Feature:
    """Feature guaranteed to have bugs."""
    feature = Feature(
        name="Buggy Feature",
        stage_capacities={
            FeatureStage.DEVELOPMENT: 5.0,
            FeatureStage.TESTING: 2.0,
        },
        initial_stage=FeatureStage.DEVELOPMENT,
        bug_probability=1.0,
    )
    feature.assign(developer)
    feature.assign(qa_engineer)
    return feature
