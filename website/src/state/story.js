import { create } from 'zustand';

export const useStoryStore = create((set) => ({
  currentAct: 1,             // 1..5
  actProgress: 0,            // 0..1 within current act
  audioEnabled: false,
  reducedMotion: false,

  setAct: (act) => set({ currentAct: act, actProgress: 0 }),
  setActProgress: (p) => set({ actProgress: p }),
  toggleAudio: () => set((s) => ({ audioEnabled: !s.audioEnabled })),
  setReducedMotion: (v) => set({ reducedMotion: v }),
}));
