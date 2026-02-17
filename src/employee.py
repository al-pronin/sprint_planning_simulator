from src.feature import Feature, FeatureStage


class Employee:

    day_work_hours = 7

    def __init__(self, name: str):
        self.name = name

    def work(self, feature: 'Feature') -> bool | None:
        print(f'{self.name} works on {feature.name}')
        feature.capacity_mapping[feature.current_stage] -= 1
        if feature.capacity_mapping[feature.current_stage] == 0:
            finished_stage = feature.capacity_mapping.pop(feature.current_stage)
            print(f'Finished stage {feature.current_stage.name}')

            remain_stages = list(feature.capacity_mapping.keys())
            if len(remain_stages) == 0:
                print(f'Feature `{feature.name}` is done!')
                return True

            feature.current_stage = list(feature.capacity_mapping.keys())[0]

    def idle(self) -> None:
        print(f'{self.name} idle')


class Developer(Employee):
    effective_stages = [FeatureStage.DEVELOPMENT]


class SystemAnalyst(Employee):
    effective_stages = [FeatureStage.ANALYTICS]
