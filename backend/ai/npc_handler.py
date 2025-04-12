import os
from openai import OpenAI
from typing import Dict, List, Optional
from dotenv import load_dotenv
import httpx
from game.npc_manager import NPCManager, NPC

load_dotenv()

class NPCHandler:
    def __init__(self):
        # Create a custom HTTP client without proxies
        http_client = httpx.Client()
        # Initialize OpenAI client with the custom HTTP client
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            http_client=http_client
        )
        # Simple in-memory storage for NPC memories
        self.npc_memories: Dict[str, List[Dict]] = {}
        # Initialize NPC manager to get NPC information
        self.npc_manager = NPCManager()

    def get_npc_response(self, npc_id: str, player_input: str, context: Dict) -> str:
        """
        Generate an NPC response using OpenAI, considering their memory and context
        
        Args:
            npc_id: Unique identifier for the NPC
            player_input: Player's message to the NPC
            context: Current game context including previous interactions
            
        Returns:
            str: Generated response from the NPC
        """
        # Get NPC information
        npc = self.npc_manager.get_npc(npc_id)
        if not npc:
            return "I'm sorry, I don't know who I am."
            
        # Get relevant memories from in-memory storage
        memories = self._get_relevant_memories(npc_id, player_input)
        
        # Construct the prompt with context and memories
        prompt = self._construct_prompt(npc, player_input, context, memories)
        
        # Generate response using OpenAI
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using GPT-3.5-turbo for cost efficiency
            messages=[
                {"role": "system", "content": f"""You are {npc.name}, a character in a time loop game.
You are currently in the {npc.location.replace('_', ' ')}.
Your personality traits are: {', '.join(npc.personality['traits'])}.
Your goals are: {', '.join(npc.personality['goals'])}.
Your fears are: {', '.join(npc.personality['fears'])}.
You know these secrets: {', '.join(npc.personality['secrets'])}."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        # Store the interaction in memory
        self._store_memory(npc_id, player_input, response.choices[0].message.content, context)
        
        return response.choices[0].message.content

    def _get_relevant_memories(self, npc_id: str, query: str) -> List[str]:
        """
        Get relevant memories from in-memory storage
        
        Args:
            npc_id: NPC identifier
            query: Current interaction to find relevant memories for
            
        Returns:
            List of relevant memory texts
        """
        if npc_id not in self.npc_memories:
            return []
        
        # For MVP, just return the last 3 memories
        memories = self.npc_memories[npc_id][-3:]
        return [memory["content"] for memory in memories]

    def _store_memory(self, npc_id: str, player_input: str, npc_response: str, context: Dict):
        """Store an interaction in memory"""
        if npc_id not in self.npc_memories:
            self.npc_memories[npc_id] = []
            
        self.npc_memories[npc_id].append({
            "player_input": player_input,
            "content": npc_response,
            "timestamp": context.get('time', 'unknown')
        })

    def _construct_prompt(self, npc: NPC, player_input: str, context: Dict, memories: List[str]) -> str:
        """
        Construct the prompt for the AI model
        
        Args:
            npc: The NPC object
            player_input: Player's message
            context: Current game context
            memories: Relevant memories from previous interactions
            
        Returns:
            str: Constructed prompt
        """
        memory_context = "\n".join([f"- {memory}" for memory in memories])
        
        return f"""
        Context:
        - Current loop: {context.get('current_loop', 1)}
        - Time of day: {context.get('time', 'morning')}
        - Your location: {npc.location.replace('_', ' ')}
        - Player's location: {context.get('location', 'unknown').replace('_', ' ')}
        
        Previous interactions:
        {memory_context}
        
        Player says: "{player_input}"
        
        Respond naturally, considering your character's personality and the context above.
        """ 