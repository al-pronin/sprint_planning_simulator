"""
Core simulation engine module.

This module provides the main SprintSimulator class that orchestrates
the sprint simulation, managing time, work assignment, and history.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.config import HOURS_PER_DAY
from src.history import SprintHistory
from src.validator import SprintValidator

if TYPE_CHECKING:
    from src.employee import Employee
    from src.feature import Feature
    from src.strategy import AssignmentStrategy
    from src.timebox import Tick


class SprintSimulator:
    """
    Core simulation engine for sprint planning.

    The simulator advances time tick-by-tick (hour-by-hour), assigns work
    to employees via the configured strategy, and records the complete
    history of the sprint for analysis and reporting.

    Time granularity:
        - 1 tick = 1 working hour
        - 8 hours per working day (configurable via HOURS_PER_DAY)

    Responsibilities:
        - Validate sprint configuration before running
        - Iterate through simulation time
        - Assign work to employees via strategy
        - Advance feature lifecycle stages
        - Record complete simulation history

    Example:
        >>> simulator = SprintSimulator(
        ...     employees=[dev1, dev2, qa],
        ...     features=[feature1, feature2],
        ...     assignment_strategy=SimpleAssignmentStrategy(),
        ... )
        >>> simulator.run(max_days=10)
        >>> simulator.history.history  # Access recorded snapshots
    """

    def __init__(
        self,
        employees: list[Employee],
        features: list[Feature],
        assignment_strategy: AssignmentStrategy,
        validate: bool = True,
    ) -> None:
        """
        Initialize the sprint simulator.

        Args:
            employees: Team members participating in the sprint.
            features: Active features to be developed.
            assignment_strategy: Strategy for matching employees to work.
            validate: Whether to validate configuration on init.

        Raises:
            PlanningError: If validation fails and validate=True.
        """
        self.employees = employees
        self.features = features.copy()  # Defensive copy
        self.assignment_strategy = assignment_strategy
        self.history = SprintHistory()
        self._validator = SprintValidator()

        if validate:
            self._validator.validate(features, employees)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def run(self, max_days: int) -> None:
        """
        Run the sprint simulation.

        Simulates the sprint day-by-day, hour-by-hour until either:
        - All features are complete
        - Maximum days are reached

        Args:
            max_days: Maximum number of working days to simulate.
        """
        print("🚀 Sprint simulation started\n")
        print(f"📋 Configuration:")
        print(f"   - Team size: {len(self.employees)}")
        print(f"   - Features: {len(self.features)}")
        print(f"   - Max days: {max_days}")
        print()

        # Print warnings
        warnings = self._validator.get_validation_warnings(
            self.features, self.employees
        )
        for warning in warnings:
            print(f"⚠️ Warning: {warning}")

        for day in range(1, max_days + 1):
            for hour in range(1, HOURS_PER_DAY + 1):
                from src.timebox import Tick
                tick = Tick(day=day, hour=hour)
                print(f"\n🕒 {tick.label}")
                self._process_tick(tick)

                if not self.features:
                    print("\n🏁 All features completed early!")
                    return

        print("\n⏹ Max days reached. Simulation stopped.")
        self._print_summary()

    # ------------------------------------------------------------------ #
    # Internal mechanics
    # ------------------------------------------------------------------ #

    def _process_tick(self, tick: Tick) -> None:
        """
        Process a single hour of work.

        This is the core simulation loop:
        1. Reset employee tick state
        2. Assign and perform work for each employee
        3. Record history snapshot
        4. Try to advance features to next stages

        Args:
            tick: Current time point.
        """
        # Reset state for this tick
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
        Advance features to next stages if current stage is complete.

        Removes fully completed features from the active list.
        """
        completed: list[Feature] = []

        for feature in self.features:
            if feature.try_advance():
                completed.append(feature)

        for feature in completed:
            self.features.remove(feature)

    def _print_summary(self) -> None:
        """
        Print a summary of the simulation results.
        """
        print("\n📊 Simulation Summary:")
        print(f"   - Total ticks recorded: {len(self.history.history)}")

        # Count completed vs incomplete features
        last_snapshot = self.history.history[-1] if self.history.history else None
        if last_snapshot:
            completed = sum(1 for f in last_snapshot.features if f.is_done)
            print(f"   - Features completed: {completed}/{len(last_snapshot.features)}")
