# src/employee.py
from typing import List, Optional
from src.feature import Feature, FeatureStage


class Employee:
    day_work_hours = 7  # может пригодиться для моделирования встреч
    effective_stages: List[FeatureStage] = []

    def __init__(self, name: str, productivity: float = 1.0):
        self.name = name
        self.productivity = productivity  # сколько единиц работы делает за день

    def work_on_feature(self, feature: Feature) -> None:
        """Работать над указанной фичей."""
        print(f"{self.name} doing {feature.current_stage.name} of `{feature.name}`")
        feature.work(self)

    def idle(self) -> None:
        print(f"{self.name} idle")


class Developer(Employee):
    effective_stages = [FeatureStage.DEVELOPMENT]


class SystemAnalyst(Employee):
    effective_stages = [FeatureStage.ANALYTICS]


class QA(Employee):
    effective_stages = [FeatureStage.TESTING]