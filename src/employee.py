from src.feature import Feature, FeatureStage


class Employee:

    day_work_hours = 7
    effective_stages: list[FeatureStage]

    def __init__(self, name: str):
        self.name = name

    def work(self, feature: 'Feature') -> bool | None:

        print(f'{self.name} doing {feature.current_stage.name} of `{feature.name}`')
        feature.capacity_mapping[feature.current_stage] -= 1


    def idle(self) -> None:
        print(f'{self.name} idle')


class Developer(Employee):
    effective_stages = [FeatureStage.DEVELOPMENT]


class SystemAnalyst(Employee):
    effective_stages = [FeatureStage.ANALYTICS]


class QA(Employee):
    effective_stages = [FeatureStage.TESTING]