from __future__ import annotations
from typing import List
from src.employee import Employee
from src.feature import Feature
from src.timebox import Tick
from src.strategy import AssignmentStrategy
from src.config import HOURS_PER_DAY
from src.history import SprintHistory


class SprintSimulator:
    """
    Core simulation engine 🧠

    Time granularity:
        - 1 tick = 1 working hour
        - 8 hours per working day (default, see config)

    Responsibilities:
        - Iterate over time
        - Assign work via strategy
        - Advance feature lifecycle
        - Record simulation history
    """

    def __init__(
        self,
        employees: List[Employee],
        features: List[Feature],
        assignment_strategy: AssignmentStrategy,
    ) -> None:
        """
        Args:
            employees: Team members participating in the sprint.
            features: Active features in progress.
            assignment_strategy: Strategy used to assign work.
        """
        self.employees = employees
        self.features = features
        self.assignment_strategy = assignment_strategy
        self.history = SprintHistory()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def run(self, max_days: int) -> None:
        """
        Runs the sprint simulation.

        Args:
            max_days: Maximum number of working days to simulate.
        """
        print("🚀 Sprint simulation started\n")

        for day in range(1, max_days + 1):
            for hour in range(1, HOURS_PER_DAY + 1):
                tick = Tick(day=day, hour=hour)
                print(f"\n🕒 {tick.label}")
                self._process_tick(tick)

                if not self.features:
                    print("\n🏁 All features completed early!")
                    return

        print("\n⏹ Max days reached. Simulation stopped.")

    # ------------------------------------------------------------------ #
    # Internal mechanics
    # ------------------------------------------------------------------ #

    def _process_tick(self, tick: Tick) -> None:
        """
        Processes a single hour of work.
        """
        # Reset state
        for employee in self.employees:
            employee.reset_tick()

        # Assign and perform work
        for employee in self.employees:
            feature = self.assignment_strategy.choose_feature(
                employee,
                self.features,
            )

            if feature:
                employee.work(feature)
            else:
                employee.idle()

        # Record history for this tick
        self.history.record(tick, self.features, self.employees)

        # Try advancing features after work is done
        self._advance_features()

    def _advance_features(self) -> None:
        """
        Advances features to next stages if their current stage is complete.
        """
        completed: List[Feature] = []

        for feature in self.features:
            if feature.try_advance():
                completed.append(feature)

        for feature in completed:
            self.features.remove(feature)
