from dataclasses import dataclass


@dataclass(frozen=True)
class Tick:
    """
    Represents a simulation time unit (half-day) ⏳
    """
    day: int
    slot: int  # 0 = morning, 1 = afternoon

    @property
    def label(self) -> str:
        part = "🌅 Morning" if self.slot == 0 else "🌇 Afternoon"
        return f"Day {self.day} — {part}"
