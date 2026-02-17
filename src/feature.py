from enum import Enum
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.employee import Employee


class FeatureStage(Enum):
    NEW = 'new'
    ANALYTICS = 'analytics'
    DEVELOPMENT = 'development'
    TESTING = 'testing'


class Feature:

    assignees: list['Employee'] = []

    def __init__(
        self,
        name: str,
        capacity_mapping: dict['FeatureStage', int],
        current_stage: 'FeatureStage'
    ):
        self.name = name
        self.capacity_mapping = capacity_mapping
        self.current_stage = current_stage

    def assign(self, employee: 'Employee') -> None:
        self.assignees.append(employee)
