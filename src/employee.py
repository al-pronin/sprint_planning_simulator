from src.feature import Feature, FeatureStage


class Employee:

    day_work_hours = 7

    def __init__(self, name: str):
        self.name = name

    def work(self, feature: 'Feature') -> None:
        print(f'{self.name} works on {feature.name}')
        feature.capacity_mapping[feature.current_stage] -= 1
        print(f'Feature capacity: {feature.capacity_mapping[feature.current_stage]}')

    def idle(self) -> None:
        print(f'{self.name} idle')


class Developer(Employee):
    effective_stages = [FeatureStage.DEVELOPMENT]


class SystemAnalyst(Employee):
    effective_stages = [FeatureStage.ANALYTICS]
