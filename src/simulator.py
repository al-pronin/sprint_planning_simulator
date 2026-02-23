from __future__ import annotations

from typing import List

from src.employee import Employee
from src.feature import Feature, FeatureStage
from src.timebox import Tick
from src.strategy import AssignmentStrategy
from src.review_engine import ReviewEngine


class SprintSimulator:
    """
    Core simulation engine 🧠
    """

    HOURS_PER_DAY: int = 8

    def __init__(
        self,
        employees: List[Employee],
        features: List[Feature],
        assignment_strategy: AssignmentStrategy,
        review_engine: ReviewEngine,
    ) -> None:
        self.employees = employees
        self.features = features
        self.assignment_strategy = assignment_strategy
        self.review_engine = review_engine

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def run(self, max_days: int) -> None:
        print("🚀 Sprint simulation started\n")

        for day in range(1, max_days + 1):
            for hour in range(1, self.HOURS_PER_DAY + 1):
                tick = Tick(day=day, hour=hour)
                print(f"\n🕒 {tick.label}")
                self._process_tick()

                if not self.features:
                    print("\n🏁 All features completed early!")
                    return

        print("\n⏹ Max days reached. Simulation stopped.")

    # ------------------------------------------------------------------ #
    # Internal mechanics
    # ------------------------------------------------------------------ #

    def _process_tick(self) -> None:
        for employee in self.employees:
            employee.reset_tick()

        for employee in self.employees:
            feature = self.assignment_strategy.choose_feature(
                employee,
                self.features,
            )

            if feature:
                employee.work(feature)
            else:
                employee.idle()

        self._advance_features()

    def _advance_features(self) -> None:
        completed: List[Feature] = []

        for feature in self.features:
            # If REVIEW just finished — delegate decision
            if (
                feature.current_stage == FeatureStage.REVIEW
                and feature._remaining[FeatureStage.REVIEW] <= 0
            ):
                self.review_engine.process_review(feature)

            if feature.try_advance():
                completed.append(feature)

        for feature in completed:
            self.features.remove(feature)