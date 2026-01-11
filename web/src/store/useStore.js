import { create } from 'zustand'

const useStore = create((set, get) => ({
  currentVector: null,
  featureLabels: [],
  categories: null,
  vectors: [],
  clusterData: null,
  isLoading: false,
  error: null,
  
  // User-based features
  userFeatures: null,
  currentMessages: null,
  compatibility: null,

  setCurrentVector: (vector) => set({ currentVector: vector }),
  setFeatureLabels: (labels) => set({ featureLabels: labels }),
  setCategories: (categories) => set({ categories }),
  setClusterData: (data) => set({ clusterData: data }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  
  // User features actions
  setUserFeatures: (features) => set({ userFeatures: features }),
  setCurrentMessages: (messages) => set({ currentMessages: messages }),
  setCompatibility: (compatibility) => set({ compatibility }),

  addVector: (vectorData) => set((state) => ({
    vectors: [...state.vectors.filter(v => v.id !== vectorData.id), vectorData]
  })),

  clearVectors: () => set({ vectors: [], currentVector: null, featureLabels: [] }),
  clearUserData: () => set({ userFeatures: null, currentMessages: null, compatibility: null }),
}))

export default useStore
