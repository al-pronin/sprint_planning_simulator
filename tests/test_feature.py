from src.feature import FeatureStage

def test_feature_work(sample_feature):
    """Checks that effort is correctly deducted."""
    initial_effort = sample_feature.get_remaining_efforts()[FeatureStage.ANALYTICS]
    sample_feature.work(0.5)
    remaining = sample_feature.get_remaining_efforts()[FeatureStage.ANALYTICS]
    assert remaining == initial_effort - 0.5


def test_feature_advancement(sample_feature):
    """Checks that feature moves to next stage when finished."""
    # Finish analytics
    sample_feature.work(2.0)
    is_done = sample_feature.try_advance()
    
    assert not is_done
    assert sample_feature.current_stage == FeatureStage.DEVELOPMENT


def test_feature_completion(sample_feature):
    """Checks that feature is completed after all stages."""
    # Analytics
    sample_feature.work(2.0)
    sample_feature.try_advance()
    
    # Development
    sample_feature.work(4.0)
    sample_feature.try_advance()
    
    # Testing
    sample_feature.work(2.0)
    is_done = sample_feature.try_advance()
    
    assert is_done
    assert sample_feature.is_done
