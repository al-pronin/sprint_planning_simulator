from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Tick:
    """
    Represents a simulation time unit (1 hour) ⏳

    Attributes:
        day: Simulation day number (starting from 1).
        hour: Hour of the working day (1..HOURS_PER_DAY).
    """

    day: int
    hour: int  # 1..8

    HOURS_PER_DAY: int = 8

    @property
    def label(self) -> str:
        """
        Human-readable label for logging.
        """
        return f"Day {self.day} — 🕐 Hour {self.hour}"
