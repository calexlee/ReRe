import { useState, useEffect } from 'react'
import './App.css'
import { GameState, NPC, InteractionResult } from './types/game'

function App() {
  const [gameState, setGameState] = useState<GameState>({
    currentLoop: 1,
    playerKnowledge: [],
    worldState: {
      time: "08:00",
      location: "village_square",
      events: [],
      inventory: [],
      npcStates: {}
    },
    npcMemories: {}
  });
  const [currentNPC, setCurrentNPC] = useState<NPC | null>(null);
  const [playerInput, setPlayerInput] = useState('');
  const [npcResponse, setNpcResponse] = useState('');
  const [locations, setLocations] = useState<string[]>([]);
  const [currentLocation, setCurrentLocation] = useState('village_square');
  const [locationNPCs, setLocationNPCs] = useState<NPC[]>([]);

  useEffect(() => {
    // Fetch initial game state
    fetchGameState();
    fetchLocations();
    fetchLocationNPCs(currentLocation);
  }, [currentLocation]);

  const fetchGameState = async () => {
    try {
      const response = await fetch('http://localhost:8000/game/state');
      const data = await response.json();
      setGameState(data);
    } catch (error) {
      console.error('Error fetching game state:', error);
    }
  };

  const fetchLocations = async () => {
    try {
      const response = await fetch('http://localhost:8000/game/locations');
      const data = await response.json();
      setLocations(data.locations);
    } catch (error) {
      console.error('Error fetching locations:', error);
    }
  };

  const fetchLocationNPCs = async (location: string) => {
    try {
      const response = await fetch(`http://localhost:8000/game/location/${location}/npcs`);
      const data = await response.json();
      setLocationNPCs(data.npcs);
    } catch (error) {
      console.error('Error fetching location NPCs:', error);
    }
  };

  const handleNPCInteraction = async (npcId: string) => {
    const npc = locationNPCs.find(n => n.id === npcId);
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
      const data: InteractionResult = await response.json();
      setNpcResponse(data.response);
      setPlayerInput('');
      
      // Update game state after interaction
      fetchGameState();
      fetchLocationNPCs(currentLocation);
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
      setCurrentNPC(null);
      setNpcResponse('');
      setPlayerInput('');
    } catch (error) {
      console.error('Error resetting game:', error);
    }
  };

  const changeLocation = (location: string) => {
    setCurrentLocation(location);
    setCurrentNPC(null);
    setNpcResponse('');
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <header className="mb-8">
        <h1 className="text-4xl font-bold mb-2">TimeLoop Tales</h1>
        <div className="flex justify-between items-center">
          <p className="text-gray-400">Loop #{gameState.currentLoop}</p>
          <p className="text-gray-400">Time: {gameState.worldState.time}</p>
        </div>
      </header>

      <div className="grid grid-cols-4 gap-8">
        {/* Locations */}
        <div className="bg-gray-800 p-6 rounded-lg">
          <h2 className="text-2xl font-semibold mb-4">Locations</h2>
          <div className="space-y-2">
            {locations.map(location => (
              <button
                key={location}
                onClick={() => changeLocation(location)}
                className={`w-full p-3 rounded-lg transition-colors ${
                  currentLocation === location
                    ? 'bg-blue-600 hover:bg-blue-500'
                    : 'bg-gray-700 hover:bg-gray-600'
                }`}
              >
                {location.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        {/* NPC List */}
        <div className="bg-gray-800 p-6 rounded-lg">
          <h2 className="text-2xl font-semibold mb-4">Current Location: {currentLocation.replace('_', ' ')}</h2>
          <div className="space-y-4">
            {locationNPCs.map(npc => (
              <button
                key={npc.id}
                onClick={() => handleNPCInteraction(npc.id)}
                className="w-full p-4 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
              >
                <h3 className="font-semibold">{npc.name}</h3>
                <p className="text-sm text-gray-400">{npc.description}</p>
                <div className="mt-2 text-sm">
                  <span className="text-blue-400">Mood: {npc.state.mood}</span>
                  <span className="ml-4 text-green-400">Trust: {npc.state.trustLevel}</span>
                </div>
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
                  onKeyPress={(e) => e.key === 'Enter' && handleNPCInteraction(currentNPC.id)}
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
      <div className="mt-8 flex justify-between">
        <div className="bg-gray-800 p-4 rounded-lg">
          <h3 className="font-semibold mb-2">Player Knowledge</h3>
          <ul className="space-y-1">
            {gameState.playerKnowledge.map((knowledge, index) => (
              <li key={index} className="text-sm text-gray-400">{knowledge}</li>
            ))}
          </ul>
        </div>
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