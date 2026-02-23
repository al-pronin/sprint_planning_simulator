from src.simulator import SprintSimulator
from src.feature import FeatureStage

def test_simulator_records_history(sample_feature, analyst, simple_strategy):
    """Verifies that simulator correctly records history after each tick."""
    sample_feature.assign(analyst)
    
    sim = SprintSimulator(
        employees=[analyst],
        features=[sample_feature],
        assignment_strategy=simple_strategy,
    )
    
    # Run only for 1 day
    sim.run(max_days=1)
    
    # 8 hours in a day, so 8 ticks
    assert len(sim.history.history) == 8
    
    # Check first tick snapshot
    first_tick = sim.history.history[0]
    assert first_tick.tick.day == 1
    assert first_tick.tick.hour == 1
    
    # Analyst should have worked on the feature
    analyst_snap = first_tick.employees[0]
    assert analyst_snap.name == analyst.name
    assert analyst_snap.has_worked is True
    assert analyst_snap.current_task == sample_feature.name
    
    # Feature effort should have decreased (8/8 = 1.0 per hour)
    feature_snap = first_tick.features[0]
    assert feature_snap.name == sample_feature.name
    assert feature_snap.remaining_efforts[FeatureStage.ANALYTICS] == 1.0
