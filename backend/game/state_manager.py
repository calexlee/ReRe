from typing import Dict, List, Set
from datetime import datetime, timedelta
import json

class GameState:
    def __init__(self):
        self.current_loop = 1
        self.player_knowledge: Set[str] = set()
        self.world_state: Dict = {
            "time": "08:00",
            "location": "village_square",
            "events": [],
            "inventory": [],
            "npc_states": {}
        }
        self.npc_memories: Dict[str, List[Dict]] = {}

    def add_player_knowledge(self, knowledge: str):
        """Add new knowledge to player's memory"""
        self.player_knowledge.add(knowledge)

    def advance_time(self, minutes: int):
        """Advance the game time"""
        current_time = datetime.strptime(self.world_state["time"], "%H:%M")
        new_time = current_time + timedelta(minutes=minutes)
        self.world_state["time"] = new_time.strftime("%H:%M")

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
            "world_state": self.world_state,
            "npc_memories": self.npc_memories
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'GameState':
        """Create game state from dictionary"""
        state = cls()
        state.current_loop = data["current_loop"]
        state.player_knowledge = set(data["player_knowledge"])
        state.world_state = data["world_state"]
        state.npc_memories = data["npc_memories"]
        return state 