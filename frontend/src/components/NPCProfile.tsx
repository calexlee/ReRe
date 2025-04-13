import React from 'react';
import { NPC, NPCState } from '../types/npc';
import { NPCService } from '../services/npcService';

interface NPCProfileProps {
  npcId: string;
}

export const NPCProfile: React.FC<NPCProfileProps> = ({ npcId }) => {
  const npcService = NPCService.getInstance();
  const npc = npcService.getNPC(npcId);
  const npcState = npcService.getNPCState(npcId);

  if (!npc || !npcState) {
    return <div>NPC not found</div>;
  }

  return (
    <div className="npc-profile">
      <h2>{npc.name}</h2>
      <div className="npc-description">
        <p>{npc.description}</p>
      </div>
      <div className="npc-details">
        <div className="npc-personality">
          <h3>Personality</h3>
          <p>{npc.personality}</p>
        </div>
        <div className="npc-goals">
          <h3>Goals</h3>
          <ul>
            {npc.goals.map((goal, index) => (
              <li key={index}>{goal}</li>
            ))}
          </ul>
        </div>
        <div className="npc-fears">
          <h3>Fears</h3>
          <ul>
            {npc.fears.map((fear, index) => (
              <li key={index}>{fear}</li>
            ))}
          </ul>
        </div>
        <div className="npc-state">
          <h3>Current State</h3>
          <p>Mood: {npcState.mood}</p>
          <p>Trust Level: {npcState.trustLevel}</p>
          <p>Location: {npcState.location}</p>
        </div>
        <div className="npc-memories">
          <h3>Memories</h3>
          <ul>
            {npcState.memories.map((memory, index) => (
              <li key={index}>{memory}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}; 