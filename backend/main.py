from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="TimeLoop Tales API",
    description="Backend API for the TimeLoop Tales game",
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

# Game state models
class GameState:
    def __init__(self):
        self.current_loop = 1
        self.npc_memories = {}
        self.player_knowledge = set()
        self.world_state = {}

# Global game state (in production, this would be in a database)
game_state = GameState()

@app.get("/")
async def root():
    return {"message": "Welcome to TimeLoop Tales API"}

@app.get("/game/state")
async def get_game_state():
    """Get the current game state"""
    return {
        "current_loop": game_state.current_loop,
        "player_knowledge": list(game_state.player_knowledge),
        "world_state": game_state.world_state
    }

@app.post("/game/reset")
async def reset_game():
    """Reset the game state while preserving player knowledge"""
    game_state.current_loop += 1
    # Preserve player knowledge but reset other states
    preserved_knowledge = game_state.player_knowledge.copy()
    game_state.__init__()
    game_state.player_knowledge = preserved_knowledge
    return {"message": "Game reset", "new_loop": game_state.current_loop}

@app.get("/npc/{npc_id}/memory")
async def get_npc_memory(npc_id: str):
    """Get an NPC's memory of previous loops"""
    if npc_id not in game_state.npc_memories:
        raise HTTPException(status_code=404, detail="NPC not found")
    return game_state.npc_memories[npc_id]

@app.post("/npc/{npc_id}/interact")
async def interact_with_npc(npc_id: str, player_input: str):
    """Handle player interaction with an NPC"""
    # TODO: Implement AI-driven NPC response
    # This will be expanded to use OpenAI for dynamic responses
    return {
        "response": f"NPC {npc_id} received: {player_input}",
        "memory_updated": False
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 