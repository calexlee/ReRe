from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv
from game.state_manager import GameState
from game.npc_manager import NPCManager
from ai.npc_handler import NPCHandler
from pydantic import BaseModel

# Load environment variables
load_dotenv()

app = FastAPI(
    title="ReRe API",
    description="Backend API for the ReRe game",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize game components
game_state = GameState()
npc_manager = NPCManager()
npc_handler = NPCHandler()

class InteractionRequest(BaseModel):
    player_input: str

@app.get("/")
async def root():
    return {"message": "Welcome to ReRe API"}

@app.get("/game/state")
async def get_game_state():
    """Get the current game state"""
    # Ensure the game state has all required fields
    state = game_state.to_dict()
    if "worldState" not in state:
        state["worldState"] = {
            "time": "08:00",
            "location": "village_square",
            "events": [],
            "inventory": [],
            "npcStates": {}
        }
    if "npcMemories" not in state:
        state["npcMemories"] = {}
    return state

@app.post("/game/reset")
async def reset_game():
    """Reset the game state while preserving player knowledge"""
    preserved_knowledge = game_state.player_knowledge.copy()
    game_state.__init__()
    game_state.player_knowledge = preserved_knowledge
    game_state.current_loop += 1
    return {"message": "Game reset", "new_loop": game_state.current_loop}

@app.get("/game/locations")
async def get_locations():
    """Get all available locations in the game"""
    return {
        "locations": [
            "village_square",
            "forge",
            "apothecary_shop",
            "tavern",
            "temple",
            "market"
        ]
    }

@app.get("/game/location/{location_id}/npcs")
async def get_npcs_at_location(location_id: str):
    """Get all NPCs at a specific location"""
    npcs = npc_manager.get_npcs_at_location(location_id)
    return {
        "location": location_id,
        "npcs": [npc.get_state() for npc in npcs]
    }

@app.get("/npc/{npc_id}")
async def get_npc(npc_id: str):
    """Get information about a specific NPC"""
    npc = npc_manager.get_npc(npc_id)
    if not npc:
        raise HTTPException(status_code=404, detail="NPC not found")
    return npc.get_state()

@app.post("/npc/{npc_id}/interact")
async def interact_with_npc(npc_id: str, request: InteractionRequest = Body(...)):
    """Handle player interaction with an NPC"""
    # Process the interaction through the NPC manager
    interaction_result = npc_manager.process_interaction(npc_id, request.player_input, game_state.to_dict())
    
    if "error" in interaction_result:
        raise HTTPException(status_code=404, detail=interaction_result["error"])

    # Get AI-generated response
    ai_response = npc_handler.get_npc_response(
        npc_id=npc_id,
        player_input=request.player_input,
        context={
            "current_loop": game_state.current_loop,
            "time": game_state.world_state.get("time", "08:00"),
            "location": game_state.world_state.get("location", "village_square")
        }
    )

    # Update game state with interaction results
    game_state.advance_time(interaction_result["state_changes"]["time_cost"] * 60)  # Convert hours to minutes
    game_state.add_event({
        "type": "npc_interaction",
        "npc_id": npc_id,
        "player_input": request.player_input,
        "npc_response": ai_response,
        "timestamp": game_state.world_state.get("time", "08:00")
    })

    # Update NPC state in game state
    game_state.update_npc_state(npc_id, interaction_result["state_changes"]["npc_state"])

    return {
        "response": ai_response,
        "state_changes": interaction_result["state_changes"],
        "time_advanced": True,
        "current_time": game_state.world_state.get("time", "08:00")
    }

@app.post("/game/player/knowledge")
async def add_player_knowledge(knowledge: str):
    """Add new knowledge to player's memory"""
    game_state.add_player_knowledge(knowledge)
    return {"message": "Knowledge added", "knowledge": knowledge}

@app.get("/game/player/knowledge")
async def get_player_knowledge():
    """Get all player knowledge"""
    return {"knowledge": list(game_state.player_knowledge)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 