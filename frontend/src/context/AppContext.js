import React, { createContext, useState, useCallback } from 'react';

export const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [currentVector, setCurrentVector] = useState(null);
  const [featureLabels, setFeatureLabels] = useState([]);
  const [vectors, setVectors] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const addVector = useCallback((vectorData) => {
    setVectors(prev => {
      const exists = prev.find(v => v.id === vectorData.id);
      if (exists) {
        return prev.map(v => v.id === vectorData.id ? vectorData : v);
      }
      return [...prev, vectorData];
    });
  }, []);

  const removeVector = useCallback((vectorId) => {
    setVectors(prev => prev.filter(v => v.id !== vectorId));
  }, []);

  const clearVectors = useCallback(() => {
    setVectors([]);
    setCurrentVector(null);
    setFeatureLabels([]);
  }, []);

  const getVectorById = useCallback((vectorId) => {
    return vectors.find(v => v.id === vectorId);
  }, [vectors]);

  const value = {
    currentVector,
    setCurrentVector,
    featureLabels,
    setFeatureLabels,
    vectors,
    setVectors,
    addVector,
    removeVector,
    clearVectors,
    getVectorById,
    isLoading,
    setIsLoading,
    error,
    setError,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};

export default AppContext;
