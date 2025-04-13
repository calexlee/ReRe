from typing import Dict, List, Set
from datetime import datetime, timedelta
import json

class GameState:
    def __init__(self):
        self.current_loop = 1
        self.player_knowledge: Set[str] = set()
        self.discovered_clues: Set[str] = set()
        self.world_state: Dict = {
            "time": "06:00",  # Start at 6 AM
            "location": "village_square",
            "events": [],
            "inventory": [],
            "npc_states": {}
        }
        self.npc_memories: Dict[str, List[Dict]] = {}
        self.is_game_over = False
        self.victory = False

        # Define the clues needed to solve the mystery
        self.CLUES = {
            "murder_weapon": "The murder weapon was a blacksmith's hammer",
            "last_seen": "The victim was last seen at the inn",
            "guard_report": "The guard's report mentions a suspicious figure",
            "elder_knowledge": "The Elder knows more than he lets on",
            "time_loop": "The time loop is connected to the murder"
        }

    def add_player_knowledge(self, knowledge: str):
        """Add new knowledge to player's memory"""
        self.player_knowledge.add(knowledge)

    def discover_clue(self, clue_id: str) -> bool:
        """Discover a new clue and check for victory condition"""
        if clue_id in self.CLUES and clue_id not in self.discovered_clues:
            self.discovered_clues.add(clue_id)
            self.add_player_knowledge(self.CLUES[clue_id])

            # Check for victory condition
            if len(self.discovered_clues) == len(self.CLUES):
                self.victory = True
                self.is_game_over = True
                from .time_service import TimeService
                time_service = TimeService()
                time_service.mark_murderer_discovered()

            return True
        return False

    def handle_death(self, death_reason: str):
        """Handle player death and prepare for next loop"""
        self.add_player_knowledge(f"Died in loop {self.current_loop}: {death_reason}")
        
        # Check if player has discovered enough clues
        if len(self.discovered_clues) >= 3:
            self.add_player_knowledge("You're getting closer to solving the mystery...")

        # Reset for next loop
        self._prepare_next_loop()

    def _prepare_next_loop(self):
        """Prepare the game state for the next loop"""
        self.current_loop += 1
        self.is_game_over = False
        self.victory = False

        # Reset time and location
        self.world_state["time"] = "06:00"
        self.world_state["location"] = "village_square"
        self.world_state["events"] = []

        # Reset NPC states (except for those with memory retention)
        from .npc_manager import NPCManager
        npc_manager = NPCManager()
        npc_manager.reset_states()

        # Reset time service
        from .time_service import TimeService
        time_service = TimeService()
        time_service.reset()

    def add_event(self, event: Dict):
        """Add a new event to the world state"""
        self.world_state["events"].append(event)

    def update_npc_state(self, npc_id: str, state: Dict):
        """Update an NPC's state"""
        self.world_state["npc_states"][npc_id] = state

    def add_npc_memory(self, npc_id: str, memory: Dict):
        """Add a memory for a specific NPC"""
        if npc_id not in self.npc_memories:
            self.npc_memories[npc_id] = []
        self.npc_memories[npc_id].append(memory)

    def get_npc_memories(self, npc_id: str) -> List[Dict]:
        """Get all memories for a specific NPC"""
        return self.npc_memories.get(npc_id, [])

    def to_dict(self) -> Dict:
        """Convert game state to dictionary for storage"""
        return {
            "current_loop": self.current_loop,
            "player_knowledge": list(self.player_knowledge),
            "discovered_clues": list(self.discovered_clues),
            "world_state": self.world_state,
            "npc_memories": self.npc_memories,
            "is_game_over": self.is_game_over,
            "victory": self.victory
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'GameState':
        """Create game state from dictionary"""
        state = cls()
        state.current_loop = data["current_loop"]
        state.player_knowledge = set(data["player_knowledge"])
        state.discovered_clues = set(data["discovered_clues"])
        state.world_state = data["world_state"]
        state.npc_memories = data["npc_memories"]
        state.is_game_over = data["is_game_over"]
        state.victory = data["victory"]
        return state

    def advance_time(self, minutes: int = 5) -> None:
        """Advance the game time by the specified number of minutes"""
        from .time_service import TimeService
        time_service = TimeService()
        
        # Convert minutes to hours (rounding up)
        hours = (minutes + 59) // 60
        time_service.advance_time(hours)
        
        # Update world state time
        self.world_state["time"] = time_service.get_time_string()
        
        # Check if player died during time advancement
        if time_service.get_current_time().is_dead:
            self.handle_death(time_service.get_current_time().death_reason) 