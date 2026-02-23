import pytest
from src.feature import Feature, FeatureStage
from src.employee import Developer, SystemAnalyst, QA
from src.strategy import SimpleAssignmentStrategy
from src.simulator import SprintSimulator


@pytest.fixture
def sample_feature():
    """Returns a feature with all stages."""
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
def developer():
    """Returns a standard developer."""
    return Developer(name="Dev", productivity_per_day=8.0)


@pytest.fixture
def analyst():
    """Returns a standard analyst."""
    return SystemAnalyst(name="Analyst", productivity_per_day=8.0)


@pytest.fixture
def qa_engineer():
    """Returns a standard QA."""
    return QA(name="QA", productivity_per_day=8.0)


@pytest.fixture
def simple_strategy():
    """Returns a simple assignment strategy."""
    return SimpleAssignmentStrategy()
