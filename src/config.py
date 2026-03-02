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
        bug_probability: Probability that bugs are found after testing (0.0 to 1.0).
        bug_fix_coefficient: Multiplier for calculating bug fix effort
            as a fraction of development effort (e.g., 0.1 = 10%).
    """

    hours_per_day: int = 8
    review_coefficient: float = 0.2
    bug_probability: float = 0.3
    bug_fix_coefficient: float = 0.1


# Default configuration instance
DEFAULT_CONFIG = SimulationConfig()

# Backward-compatible module-level constants
HOURS_PER_DAY: int = DEFAULT_CONFIG.hours_per_day
REVIEW_COEFFICIENT: float = DEFAULT_CONFIG.review_coefficient
BUG_PROBABILITY: float = DEFAULT_CONFIG.bug_probability
BUG_FIX_COEFFICIENT: float = DEFAULT_CONFIG.bug_fix_coefficient
