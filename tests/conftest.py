"""
Pytest configuration and shared fixtures.

This module provides common test fixtures used across the test suite.
"""

import pytest

from src.employee import Developer, QA, SystemAnalyst
from src.feature import Feature, FeatureStage
from src.strategy import SimpleAssignmentStrategy


@pytest.fixture
def sample_feature() -> Feature:
    """
    Returns a feature with all stages for comprehensive testing.

    The feature includes:
    - Analytics: 2.0h
    - Development: 4.0h
    - Code Review: 0.8h (auto-calculated as 20% of development)
    - Testing: 2.0h
    """
    return Feature(
        name="Test Feature",
        stage_capacities={
            FeatureStage.ANALYTICS: 2.0,
            FeatureStage.DEVELOPMENT: 4.0,
            FeatureStage.TESTING: 2.0,
        },
        initial_stage=FeatureStage.ANALYTICS,
    )


@pytest.fixture
def dev_only_feature() -> Feature:
    """
    Returns a feature starting at development (no analytics).
    """
    return Feature(
        name="Dev Only Feature",
        stage_capacities={
            FeatureStage.DEVELOPMENT: 5.0,
            FeatureStage.TESTING: 2.0,
        },
        initial_stage=FeatureStage.DEVELOPMENT,
    )


@pytest.fixture
def developer() -> Developer:
    """Returns a standard developer with default productivity."""
    return Developer(name="Dev", productivity_per_day=8.0)


@pytest.fixture
def developer_two() -> Developer:
    """Returns a second developer for code review testing."""
    return Developer(name="Dev2", productivity_per_day=8.0)


@pytest.fixture
def analyst() -> SystemAnalyst:
    """Returns a standard analyst with default productivity."""
    return SystemAnalyst(name="Analyst", productivity_per_day=8.0)


@pytest.fixture
def qa_engineer() -> QA:
    """Returns a standard QA with default productivity."""
    return QA(name="QA", productivity_per_day=8.0)


@pytest.fixture
def simple_strategy() -> SimpleAssignmentStrategy:
    """Returns a simple assignment strategy."""
    return SimpleAssignmentStrategy()


@pytest.fixture
def feature_with_assignees(
    sample_feature: Feature,
    developer: Developer,
    analyst: SystemAnalyst,
    qa_engineer: QA,
) -> Feature:
    """
    Returns a feature with all roles assigned.
    """
    sample_feature.assign(analyst)
    sample_feature.assign(developer)
    sample_feature.assign(qa_engineer)
    return sample_feature
