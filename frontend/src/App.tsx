import { useState, useEffect, useRef } from 'react'
import './App.css'
import { GameState, NPC, InteractionResult } from './types/game'

const initialGameState: GameState = {
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
};

function App() {
  const [gameState, setGameState] = useState<GameState>(initialGameState);
  const [currentNPC, setCurrentNPC] = useState<NPC | null>(null);
  const [playerInput, setPlayerInput] = useState('');
  const [npcResponse, setNpcResponse] = useState('');
  const [locations, setLocations] = useState<string[]>([]);
  const [currentLocation, setCurrentLocation] = useState('village_square');
  const [locationNPCs, setLocationNPCs] = useState<NPC[]>([]);
  const [chatHistory, setChatHistory] = useState<{ speaker: string; message: string }[]>([]);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when chat history changes
  useEffect(() => {
    if (chatContainerRef.current) {
      const container = chatContainerRef.current;
      const shouldScroll = container.scrollHeight - container.scrollTop <= container.clientHeight + 100;
      if (shouldScroll) {
        container.scrollTop = container.scrollHeight;
      }
    }
  }, [chatHistory, npcResponse]);

  useEffect(() => {
    fetchGameState();
    fetchLocations();
    fetchLocationNPCs(currentLocation);
  }, [currentLocation]);

  const fetchGameState = async () => {
    try {
      const response = await fetch('http://localhost:8000/game/state');
      const data = await response.json();
      // Ensure all required fields are present
      const state: GameState = {
        currentLoop: data.currentLoop || 1,
        playerKnowledge: data.playerKnowledge || [],
        worldState: {
          time: data.worldState?.time || "08:00",
          location: data.worldState?.location || "village_square",
          events: data.worldState?.events || [],
          inventory: data.worldState?.inventory || [],
          npcStates: data.worldState?.npcStates || {}
        },
        npcMemories: data.npcMemories || {}
      };
      setGameState(state);
    } catch (error) {
      console.error('Error fetching game state:', error);
      // Fallback to initial state if fetch fails
      setGameState(initialGameState);
    }
  };

  const fetchLocations = async () => {
    try {
      const response = await fetch('http://localhost:8000/game/locations');
      const data = await response.json();
      setLocations(data.locations);
    } catch (error) {
      console.error('Error fetching locations:', error);
      setLocations(['village_square', 'forge', 'apothecary_shop']);
    }
  };

  const fetchLocationNPCs = async (location: string) => {
    try {
      const response = await fetch(`http://localhost:8000/game/location/${location}/npcs`);
      const data = await response.json();
      setLocationNPCs(data.npcs);
    } catch (error) {
      console.error('Error fetching location NPCs:', error);
      setLocationNPCs([]);
    }
  };

  const handleNPCInteraction = async (npcId: string) => {
    const npc = locationNPCs.find(n => n.id === npcId);
    if (!npc) return;

    setCurrentNPC(npc);
    setNpcResponse('...');
    
    // Add player message to chat history
    if (playerInput.trim()) {
      setChatHistory(prev => [...prev, { speaker: 'You', message: playerInput }]);
    }
    
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
      
      // Add NPC response to chat history
      setChatHistory(prev => [...prev, { speaker: npc.name, message: data.response }]);
      
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
    <div className="h-screen flex flex-col bg-gray-900 text-white overflow-hidden">
      {/* Top Bar */}
      <div className="flex-none bg-gray-800/50 backdrop-blur-sm p-3 border-b border-gray-700">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold">ReRe</h1>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-400">Loop #{gameState.currentLoop}</span>
            <span className="text-sm text-gray-400">Time: {gameState.worldState.time}</span>
            <button
              onClick={resetGame}
              className="px-2 py-1 bg-red-600/50 hover:bg-red-600 rounded-lg transition-colors text-xs"
            >
              Reset Loop
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        <div className="max-w-7xl mx-auto w-full p-3">
          <div className="grid grid-cols-12 h-[calc(100vh-4rem)] gap-3">
            {/* Left Sidebar - Minimap and NPCs */}
            <div className="col-span-3 flex flex-col gap-3 h-full">
              {/* Minimap */}
              <div className="flex-none bg-gray-800/50 backdrop-blur-sm rounded-lg p-3 border border-gray-700">
                <h2 className="text-xs font-semibold mb-2 text-gray-400">Locations</h2>
                <div className="grid grid-cols-2 gap-1">
                  {locations.map(location => (
                    <button
                      key={location}
                      onClick={() => changeLocation(location)}
                      className={`p-1.5 rounded-lg text-xs transition-all ${
                        currentLocation === location
                          ? 'bg-blue-600/50 border border-blue-500'
                          : 'bg-gray-700/50 hover:bg-gray-700 border border-gray-600'
                      }`}
                    >
                      {location.replace('_', ' ')}
                    </button>
                  ))}
                </div>
              </div>

              {/* NPC List */}
              <div className="flex-1 bg-gray-800/50 backdrop-blur-sm rounded-lg p-3 border border-gray-700 overflow-y-auto">
                <h2 className="text-xs font-semibold mb-1 text-gray-400">Current Location</h2>
                <p className="text-sm mb-2">{currentLocation.replace('_', ' ')}</p>
                <div className="space-y-1.5">
                  {locationNPCs.map(npc => (
                    <button
                      key={npc.id}
                      onClick={() => handleNPCInteraction(npc.id)}
                      className={`w-full p-2 rounded-lg transition-all ${
                        currentNPC?.id === npc.id
                          ? 'bg-blue-600/50 border border-blue-500'
                          : 'bg-gray-700/50 hover:bg-gray-700 border border-gray-600'
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <h3 className="text-sm font-medium">{npc.name}</h3>
                        <div className="flex gap-1">
                          <span className="text-[10px] text-blue-400">{npc.state?.mood || 'neutral'}</span>
                          <span className="text-[10px] text-green-400">{npc.state?.trustLevel || 0}</span>
                        </div>
                      </div>
                      <p className="text-xs text-gray-400 mt-0.5">{npc.description}</p>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Main Chat Area */}
            <div className="col-span-9 h-full">
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-700 h-full flex flex-col">
                {/* Chat Header */}
                <div className="flex-none p-3 border-b border-gray-700">
                  <h2 className="text-lg font-semibold">
                    {currentNPC ? `Talking to ${currentNPC.name}` : 'Select an NPC to interact'}
                  </h2>
                </div>

                {/* Chat Messages */}
                <div 
                  ref={chatContainerRef}
                  className="flex-1 min-h-0 overflow-y-auto p-3 space-y-2 scroll-smooth"
                  style={{ scrollBehavior: 'smooth' }}
                >
                  {chatHistory.map((chat, index) => (
                    <div
                      key={index}
                      className={`flex ${chat.speaker === 'You' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[85%] p-2 rounded-lg ${
                          chat.speaker === 'You'
                            ? 'bg-blue-600/50 border border-blue-500'
                            : 'bg-gray-700/50 border border-gray-600'
                        }`}
                      >
                        <div className="text-xs font-medium mb-0.5">{chat.speaker}</div>
                        <div className="text-sm text-gray-200">{chat.message}</div>
                      </div>
                    </div>
                  ))}
                  {npcResponse === '...' && (
                    <div className="flex justify-start">
                      <div className="bg-gray-700/50 border border-gray-600 p-2 rounded-lg">
                        <div className="text-xs font-medium mb-0.5">{currentNPC?.name}</div>
                        <div className="text-sm text-gray-200">...</div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Input Area */}
                <div className="flex-none p-3 border-t border-gray-700 bg-gray-800/50">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={playerInput}
                      onChange={(e) => setPlayerInput(e.target.value)}
                      placeholder="What would you like to say?"
                      className="flex-1 p-2 bg-gray-700/50 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 text-sm"
                      onKeyPress={(e) => e.key === 'Enter' && currentNPC && handleNPCInteraction(currentNPC.id)}
                    />
                    <button
                      onClick={() => currentNPC && handleNPCInteraction(currentNPC.id)}
                      className="px-3 py-2 bg-blue-600/50 hover:bg-blue-600 border border-blue-500 rounded-lg transition-colors text-sm"
                      disabled={!currentNPC}
                    >
                      Send
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App