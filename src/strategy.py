from __future__ import annotations
from typing import List, Protocol
from src.employee import Employee
from src.feature import Feature


class AssignmentStrategy(Protocol):
    """
    Strategy interface for assigning work 🎯
    """

    def choose_feature(
        self,
        employee: Employee,
        features: List[Feature],
    ) -> Feature | None:
        ...


class SimpleAssignmentStrategy:
    """
    Greedy strategy:
    - First available feature
    - In given order
    """

    def choose_feature(
        self,
        employee: Employee,
        features: List[Feature],
    ) -> Feature | None:

        for feature in features:
            if feature.can_be_worked_by(employee):
                return feature

        return None
