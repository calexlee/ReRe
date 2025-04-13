from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class TimeState:
    current_hour: int
    is_dead: bool
    death_reason: Optional[str]
    discovered_murderer: bool

class TimeService:
    _instance = None
    TOTAL_HOURS = 24
    DEATH_EVENTS = {
        12: {"npc_id": "guard", "reason": "Captain Roderick caught you investigating the murder scene"},
        15: {"npc_id": "blacksmith", "reason": "Gorrik discovered you snooping in his forge"},
        18: {"npc_id": "innkeeper", "reason": "Mara found you in her secret room"},
        21: {"npc_id": "elder", "reason": "The Elder caught you trying to break the time loop"}
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TimeService, cls).__new__(cls)
            cls._instance.state = TimeState(
                current_hour=6,  # Start at 6 AM
                is_dead=False,
                death_reason=None,
                discovered_murderer=False
            )
        return cls._instance

    def get_current_time(self) -> TimeState:
        return self.state

    def advance_time(self, hours: int = 1) -> None:
        if self.state.is_dead:
            return

        self.state.current_hour += hours
        
        # Check for death events
        if self.state.current_hour in self.DEATH_EVENTS:
            death_event = self.DEATH_EVENTS[self.state.current_hour]
            from .npc_manager import NPCManager
            npc_manager = NPCManager()
            npc = npc_manager.get_npc(death_event["npc_id"])
            
            # Only trigger death if trust level is too low
            if npc and npc.state["trust_level"] < 50:
                self.state.is_dead = True
                self.state.death_reason = death_event["reason"]

        # Check for end of day
        if self.state.current_hour >= self.TOTAL_HOURS:
            if not self.state.discovered_murderer:
                self.state.is_dead = True
                self.state.death_reason = "The day ended without discovering the murderer"

    def reset(self) -> None:
        self.state = TimeState(
            current_hour=6,
            is_dead=False,
            death_reason=None,
            discovered_murderer=False
        )

    def mark_murderer_discovered(self) -> None:
        self.state.discovered_murderer = True

    def get_time_string(self) -> str:
        """Convert current hour to time string (e.g., '08:00')"""
        return f"{self.state.current_hour:02d}:00"

    def is_night(self) -> bool:
        """Check if it's night time (between 20:00 and 06:00)"""
        return self.state.current_hour >= 20 or self.state.current_hour < 6 