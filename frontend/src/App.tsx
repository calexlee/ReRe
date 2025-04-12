import { useState, useEffect } from 'react'
import './App.css'

// Types
interface GameState {
  currentLoop: number;
  playerKnowledge: string[];
  worldState: Record<string, any>;
}

interface NPC {
  id: string;
  name: string;
  description: string;
  location: string;
}

const initialNPCs: NPC[] = [
  {
    id: 'elder',
    name: 'Elder Thalric',
    description: 'The village elder, wise but secretive',
    location: 'village_square'
  },
  {
    id: 'blacksmith',
    name: 'Gorrik the Blacksmith',
    description: 'A burly blacksmith with a mysterious past',
    location: 'forge'
  },
  {
    id: 'apothecary',
    name: 'Mistress Althea',
    description: 'The village apothecary, knowledgeable about herbs and potions',
    location: 'apothecary_shop'
  }
];

function App() {
  const [gameState, setGameState] = useState<GameState>({
    currentLoop: 1,
    playerKnowledge: [],
    worldState: {}
  });
  const [currentNPC, setCurrentNPC] = useState<NPC | null>(null);
  const [playerInput, setPlayerInput] = useState('');
  const [npcResponse, setNpcResponse] = useState('');

  useEffect(() => {
    // Fetch initial game state
    fetchGameState();
  }, []);

  const fetchGameState = async () => {
    try {
      const response = await fetch('http://localhost:8000/game/state');
      const data = await response.json();
      setGameState(data);
    } catch (error) {
      console.error('Error fetching game state:', error);
    }
  };

  const handleNPCInteraction = async (npcId: string) => {
    const npc = initialNPCs.find(n => n.id === npcId);
    if (!npc) return;

    setCurrentNPC(npc);
    setNpcResponse('...');
    
    try {
      const response = await fetch(`http://localhost:8000/npc/${npcId}/interact`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ player_input: playerInput }),
      });
      const data = await response.json();
      setNpcResponse(data.response);
    } catch (error) {
      console.error('Error interacting with NPC:', error);
      setNpcResponse('An error occurred while talking to the NPC.');
    }
  };

  const resetGame = async () => {
    try {
      const response = await fetch('http://localhost:8000/game/reset', {
        method: 'POST',
      });
      const data = await response.json();
      setGameState(prev => ({
        ...prev,
        currentLoop: data.new_loop
      }));
    } catch (error) {
      console.error('Error resetting game:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <header className="mb-8">
        <h1 className="text-4xl font-bold mb-2">TimeLoop Tales</h1>
        <p className="text-gray-400">Loop #{gameState.currentLoop}</p>
      </header>

      <div className="grid grid-cols-3 gap-8">
        {/* NPC List */}
        <div className="bg-gray-800 p-6 rounded-lg">
          <h2 className="text-2xl font-semibold mb-4">Village Residents</h2>
          <div className="space-y-4">
            {initialNPCs.map(npc => (
              <button
                key={npc.id}
                onClick={() => handleNPCInteraction(npc.id)}
                className="w-full p-4 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
              >
                <h3 className="font-semibold">{npc.name}</h3>
                <p className="text-sm text-gray-400">{npc.description}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Interaction Area */}
        <div className="col-span-2 bg-gray-800 p-6 rounded-lg">
          {currentNPC ? (
            <div>
              <h2 className="text-2xl font-semibold mb-4">Talking to {currentNPC.name}</h2>
              <div className="mb-4 p-4 bg-gray-700 rounded-lg min-h-[200px]">
                {npcResponse}
              </div>
              <div className="flex gap-4">
                <input
                  type="text"
                  value={playerInput}
                  onChange={(e) => setPlayerInput(e.target.value)}
                  placeholder="What would you like to say?"
                  className="flex-1 p-2 bg-gray-700 rounded-lg"
                />
                <button
                  onClick={() => handleNPCInteraction(currentNPC.id)}
                  className="px-4 py-2 bg-blue-600 rounded-lg hover:bg-blue-500 transition-colors"
                >
                  Send
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-400">
              Select an NPC to interact with
            </div>
          )}
        </div>
      </div>

      {/* Game Controls */}
      <div className="mt-8 flex justify-end">
        <button
          onClick={resetGame}
          className="px-4 py-2 bg-red-600 rounded-lg hover:bg-red-500 transition-colors"
        >
          Reset Loop
        </button>
      </div>
    </div>
  )
}

export default App