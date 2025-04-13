from typing import Dict, List, Optional
from datetime import datetime
import json
import os

class NPC:
    def __init__(self, id: str, name: str, description: str, location: str, personality: Dict, initial_state: Dict):
        self.id = id
        self.name = name
        self.description = description
        self.location = location
        self.personality = personality
        self.state = initial_state.copy()

    def update_state(self, interaction_result: Dict):
        """Update NPC state based on interaction results"""
        if "mood_change" in interaction_result:
            self.state["mood"] = interaction_result["mood_change"]
        if "trust_change" in interaction_result:
            self.state["trust_level"] += interaction_result["trust_change"]
        if "new_secret" in interaction_result:
            self.state["known_secrets"].append(interaction_result["new_secret"])
        if "new_goal" in interaction_result:
            self.state["current_goal"] = interaction_result["new_goal"]
        if "memory" in interaction_result:
            self.state["memories"].append(interaction_result["memory"])

    def get_state(self) -> Dict:
        """Get current NPC state"""
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "state": self.state,
            "personality": self.personality
        }

class NPCManager:
    def __init__(self):
        self.npcs: Dict[str, NPC] = {}
        self.NPCs_WITH_MEMORY = ["elder"]  # NPCs who retain memories between loops
        self._load_npcs()

    def _load_npcs(self):
        """Load NPCs from JSON file"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            npc_file = os.path.join(current_dir, "npcs.json")
            
            with open(npc_file, 'r') as f:
                npc_data = json.load(f)
                
            for npc_id, npc_info in npc_data.items():
                self.npcs[npc_id] = NPC(
                    id=npc_id,
                    name=npc_info["name"],
                    description=npc_info["description"],
                    location=npc_info["location"],
                    personality=npc_info["personality"],
                    initial_state=npc_info["initial_state"]
                )
        except Exception as e:
            print(f"Error loading NPCs: {e}")
            # Initialize with empty NPCs if loading fails
            self.npcs = {}

    def get_npc(self, npc_id: str) -> Optional[NPC]:
        """Get an NPC by ID"""
        return self.npcs.get(npc_id)

    def get_npcs_at_location(self, location: str) -> List[NPC]:
        """Get all NPCs at a specific location"""
        return [npc for npc in self.npcs.values() if npc.location == location]

    def update_npc_location(self, npc_id: str, new_location: str):
        """Update an NPC's location"""
        if npc := self.get_npc(npc_id):
            npc.location = new_location

    def process_interaction(self, npc_id: str, action: str, game_state: Dict) -> Dict:
        """Process an interaction with an NPC"""
        npc = self.get_npc(npc_id)
        if not npc:
            return {"error": "NPC not found"}

        from .time_service import TimeService
        time_service = TimeService()
        current_time = time_service.get_current_time()

        # Different actions take different amounts of time
        time_cost = 1  # Default time cost
        response = ""

        if action == "greet":
            time_cost = 0.5
            response = self._generate_greeting(npc, current_time.current_hour)
        elif action == "ask_about_murder":
            time_cost = 2
            response = self._generate_murder_response(npc)
        elif action == "investigate":
            time_cost = 3
            response = self._generate_investigation_response(npc)
        else:
            response = "I don't understand what you want."

        # Update trust based on interaction
        trust_change = self._calculate_trust_change(action)
        npc.state["trust_level"] = max(0, min(100, npc.state["trust_level"] + trust_change))

        # Add memory of interaction
        memory = f"{current_time.current_hour}:00 - Player {action}"
        npc.state["memories"].append(memory)

        # Return the interaction result with state changes
        return {
            "state_changes": {
                "trust_change": trust_change,
                "memory": memory,
                "time_cost": time_cost,
                "npc_state": npc.get_state()
            }
        }

    def _generate_greeting(self, npc: NPC, current_hour: int) -> str:
        if current_hour < 12:
            return f"Good morning, traveler. {npc.personality['traits'][0]}"
        elif current_hour < 18:
            return f"Good afternoon. {npc.personality['traits'][0]}"
        else:
            return f"Good evening. {npc.personality['traits'][0]}"

    def _generate_murder_response(self, npc: NPC) -> str:
        if npc.state["trust_level"] < 30:
            return "I don't know anything about that. You should ask someone else."

        if npc.id == "elder":
            return "The murder... yes, it's part of the cycle. But I cannot tell you more yet."
        elif npc.id == "blacksmith":
            return "I saw something strange at the forge last night. A shadowy figure..."
        elif npc.id == "apothecary":
            return "I heard a commotion in one of the rooms, but when I checked, no one was there."
        return "I don't know anything about that."

    def _generate_investigation_response(self, npc: NPC) -> str:
        if npc.state["trust_level"] < 50:
            return "I can't let you look around here. It's not safe."

        if npc.id == "elder":
            return "You find a strange symbol carved into the wall. It looks familiar..."
        elif npc.id == "blacksmith":
            return "In the forge, you discover a hidden compartment with unusual weapons."
        elif npc.id == "apothecary":
            return "Behind a painting, you find a secret room with mysterious notes."
        return "You don't find anything of interest."

    def _calculate_trust_change(self, action: str) -> int:
        if action == "greet":
            return 5
        elif action == "ask_about_murder":
            return -10
        elif action == "investigate":
            return -20
        return 0

    def reset_states(self) -> None:
        """Reset NPC states for the next loop"""
        for npc_id, npc in self.npcs.items():
            if npc_id not in self.NPCs_WITH_MEMORY:
                # Reload initial state from JSON
                current_dir = os.path.dirname(os.path.abspath(__file__))
                npc_file = os.path.join(current_dir, "npcs.json")
                
                with open(npc_file, 'r') as f:
                    npc_data = json.load(f)
                    if npc_id in npc_data:
                        npc.state = npc_data[npc_id]["initial_state"].copy() 