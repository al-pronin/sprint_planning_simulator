"""
Global configuration for the sprint simulator.

This module contains all configurable constants used throughout the simulation.
Values can be adjusted to model different sprint scenarios.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationConfig:
    """
    Immutable configuration container for simulation parameters.

    Attributes:
        hours_per_day: Number of working hours in a single day.
        review_coefficient: Multiplier for calculating code review effort
            as a fraction of development effort (e.g., 0.2 = 20%).
    """

    hours_per_day: int = 8
    review_coefficient: float = 0.2


# Default configuration instance
DEFAULT_CONFIG = SimulationConfig()

# Backward-compatible module-level constants
HOURS_PER_DAY: int = DEFAULT_CONFIG.hours_per_day
REVIEW_COEFFICIENT: float = DEFAULT_CONFIG.review_coefficient
