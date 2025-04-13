import { NPC, NPCState, NPCData } from '../types/npc';
import npcData from '../data/npcs.json';

class NPCService {
  private static instance: NPCService;
  private npcStates: Map<string, NPCState> = new Map();

  private constructor() {
    this.initializeNPCStates();
  }

  public static getInstance(): NPCService {
    if (!NPCService.instance) {
      NPCService.instance = new NPCService();
    }
    return NPCService.instance;
  }

  private initializeNPCStates(): void {
    const data = npcData as NPCData;
    data.npcs.forEach(npc => {
      this.npcStates.set(npc.id, {
        mood: npc.initialMood,
        trustLevel: npc.initialTrustLevel,
        location: npc.defaultLocation,
        memories: []
      });
    });
  }

  public getNPC(npcId: string): NPC | undefined {
    const data = npcData as NPCData;
    return data.npcs.find(npc => npc.id === npcId);
  }

  public getNPCState(npcId: string): NPCState | undefined {
    return this.npcStates.get(npcId);
  }

  public updateNPCState(npcId: string, updates: Partial<NPCState>): void {
    const currentState = this.npcStates.get(npcId);
    if (currentState) {
      this.npcStates.set(npcId, {
        ...currentState,
        ...updates
      });
    }
  }

  public addMemory(npcId: string, memory: string): void {
    const currentState = this.npcStates.get(npcId);
    if (currentState) {
      this.npcStates.set(npcId, {
        ...currentState,
        memories: [...currentState.memories, memory]
      });
    }
  }
}

export default NPCService; 