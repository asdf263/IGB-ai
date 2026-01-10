import { create } from 'zustand'

const useStore = create((set, get) => ({
  currentVector: null,
  featureLabels: [],
  categories: null,
  vectors: [],
  clusterData: null,
  isLoading: false,
  error: null,

  setCurrentVector: (vector) => set({ currentVector: vector }),
  setFeatureLabels: (labels) => set({ featureLabels: labels }),
  setCategories: (categories) => set({ categories }),
  setClusterData: (data) => set({ clusterData: data }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),

  addVector: (vectorData) => set((state) => ({
    vectors: [...state.vectors.filter(v => v.id !== vectorData.id), vectorData]
  })),

  clearVectors: () => set({ vectors: [], currentVector: null, featureLabels: [] }),
}))

export default useStore
