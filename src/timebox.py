"""
Time management module for the sprint simulator.

This module defines the time-related concepts used in simulation,
including the fundamental time unit (Tick) and time utilities.
"""

from dataclasses import dataclass

from src.config import HOURS_PER_DAY


@dataclass(frozen=True, slots=True)
class Tick:
    """
    Represents a simulation time unit (1 working hour).

    A tick is the fundamental time unit in the sprint simulation.
    Each tick represents one hour of work in a working day.

    Attributes:
        day: Simulation day number (starting from 1).
        hour: Hour of the working day (1 to HOURS_PER_DAY).

    Example:
        >>> tick = Tick(day=1, hour=3)
        >>> tick.label
        'Day 1 — 🕐 Hour 3'
    """

    day: int
    hour: int  # 1..HOURS_PER_DAY

    def __post_init__(self) -> None:
        """Validate tick values after initialization."""
        if self.day < 1:
            raise ValueError(f"Day must be >= 1, got {self.day}")
        if not 1 <= self.hour <= HOURS_PER_DAY:
            raise ValueError(
                f"Hour must be between 1 and {HOURS_PER_DAY}, got {self.hour}"
            )

    @property
    def label(self) -> str:
        """Human-readable label for logging and display."""
        return f"Day {self.day} — 🕐 Hour {self.hour}"

    @property
    def total_hours(self) -> int:
        """Total number of hours elapsed since simulation start."""
        return (self.day - 1) * HOURS_PER_DAY + self.hour

    @property
    def name(self) -> str:
        """Alias for label for compatibility."""
        return self.label
