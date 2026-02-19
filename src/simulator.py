from __future__ import annotations
from typing import List
from src.employee import Employee
from src.feature import Feature
from src.timebox import Tick
from src.strategy import AssignmentStrategy


class SprintSimulator:
    """
    Core simulation engine 🧠
    Tick-based (half-day granularity).
    """

    SLOTS_PER_DAY = 2

    def __init__(
        self,
        employees: List[Employee],
        features: List[Feature],
        assignment_strategy: AssignmentStrategy,
    ) -> None:
        self.employees = employees
        self.features = features
        self.assignment_strategy = assignment_strategy

    def run(self, max_days: int) -> None:
        print("🚀 Sprint simulation started\n")

        for day in range(1, max_days + 1):
            for slot in range(self.SLOTS_PER_DAY):
                tick = Tick(day=day, slot=slot)
                print(f"\n🕒 {tick.label}")
                self._process_tick()

                if not self.features:
                    print("\n🏁 All features completed early!")
                    return

        print("\n⏹ Max days reached. Simulation stopped.")

    def _process_tick(self) -> None:
        for employee in self.employees:
            employee.reset_tick()

        for employee in self.employees:
            feature = self.assignment_strategy.choose_feature(
                employee, self.features
            )
            if feature:
                employee.work(feature)
            else:
                employee.idle()

        self._advance_features()

    def _advance_features(self) -> None:
        completed: List[Feature] = []

        for feature in self.features:
            if feature.try_advance():
                completed.append(feature)

        for feature in completed:
            self.features.remove(feature)
