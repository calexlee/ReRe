export interface NPC {
  id: string;
  name: string;
  description: string;
  personality: string;
  goals: string[];
  fears: string[];
  secrets: string[];
  defaultLocation: string;
  initialMood: string;
  initialTrustLevel: number;
}

export interface NPCState {
  mood: string;
  trustLevel: number;
  location: string;
  memories: string[];
}

export interface NPCData {
  npcs: NPC[];
} 