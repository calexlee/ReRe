import os
from openai import OpenAI
from typing import Dict, List, Optional
import pinecone
from dotenv import load_dotenv

load_dotenv()

class NPCHandler:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.pinecone_index = None
        self.setup_pinecone()
        
    def setup_pinecone(self):
        """Initialize Pinecone for vector storage of NPC memories"""
        pinecone.init(
            api_key=os.getenv("PINECONE_API_KEY"),
            environment=os.getenv("PINECONE_ENVIRONMENT")
        )
        index_name = "npc-memories"
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                index_name,
                dimension=1536,  # OpenAI embedding dimension
                metric="cosine"
            )
        self.pinecone_index = pinecone.Index(index_name)

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
        # Retrieve relevant memories from vector store
        memories = self._get_relevant_memories(npc_id, player_input)
        
        # Construct the prompt with context and memories
        prompt = self._construct_prompt(npc_id, player_input, context, memories)
        
        # Generate response using OpenAI
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"You are {npc_id}, a character in a time loop game."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        return response.choices[0].message.content

    def _get_relevant_memories(self, npc_id: str, query: str) -> List[str]:
        """
        Retrieve relevant memories from the vector store
        
        Args:
            npc_id: NPC identifier
            query: Current interaction to find relevant memories for
            
        Returns:
            List of relevant memory texts
        """
        # Generate embedding for the query
        query_embedding = self.client.embeddings.create(
            input=query,
            model="text-embedding-ada-002"
        ).data[0].embedding
        
        # Query Pinecone for relevant memories
        results = self.pinecone_index.query(
            vector=query_embedding,
            top_k=3,
            filter={"npc_id": npc_id}
        )
        
        return [match.metadata["text"] for match in results.matches]

    def _construct_prompt(self, npc_id: str, player_input: str, context: Dict, memories: List[str]) -> str:
        """
        Construct the prompt for the AI model
        
        Args:
            npc_id: NPC identifier
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
        - Location: {context.get('location', 'unknown')}
        
        Relevant memories:
        {memory_context}
        
        Player says: "{player_input}"
        
        Respond naturally, considering your character's personality and the context above.
        """ 