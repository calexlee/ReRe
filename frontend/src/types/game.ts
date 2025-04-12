export interface GameState {
  currentLoop: number;
  playerKnowledge: string[];
  worldState: {
    time: string;
    location: string;
    events: GameEvent[];
    inventory: string[];
    npcStates: Record<string, NPCState>;
  };
  npcMemories: Record<string, NPCMemory[]>;
}

export interface GameEvent {
  type: string;
  npcId?: string;
  playerInput?: string;
  timestamp: string;
}

export interface NPC {
  id: string;
  name: string;
  description: string;
  location: string;
  personality: {
    traits: string[];
    goals: string[];
    fears: string[];
    secrets: string[];
  };
  state: NPCState;
}

export interface NPCState {
  mood: string;
  trustLevel: number;
  knownSecrets: string[];
  currentGoal: string | null;
}

export interface NPCMemory {
  timestamp: string;
  content: string;
  importance: number;
}

export interface InteractionResult {
  response: string;
  stateChanges: {
    moodChange: string;
    trustChange: number;
    newSecret: string | null;
    newGoal: string | null;
  };
  timeAdvanced: boolean;
} 