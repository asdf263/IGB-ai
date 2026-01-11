import React, { useState, useContext } from 'react';
import { View, StyleSheet, ScrollView, FlatList } from 'react-native';
import { Card, Text, Button, Chip, SegmentedButtons, DataTable, ActivityIndicator, TextInput, IconButton } from 'react-native-paper';
import { AppContext } from '../context/AppContext';
import { generateSynthetic, listVectors } from '../services/vectorApi';

const SyntheticScreen = ({ navigation }) => {
  const { vectors } = useContext(AppContext);
  const [generating, setGenerating] = useState(false);
  const [syntheticVectors, setSyntheticVectors] = useState([]);
  const [method, setMethod] = useState('smote');
  const [count, setCount] = useState(10);
  const [compareMode, setCompareMode] = useState(false);
  const [selectedReal, setSelectedReal] = useState(null);
  const [selectedSynthetic, setSelectedSynthetic] = useState(null);

  const methods = [
    { value: 'smote', label: 'SMOTE' },
    { value: 'noise', label: 'Noise' },
    { value: 'jitter', label: 'Jitter' },
    { value: 'interpolate', label: 'Interpolate' },
    { value: 'adasyn', label: 'ADASYN' },
  ];

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const storedVectors = await listVectors();
      const sourceVectors = storedVectors.vectors?.map(v => v.vector) || [];

      if (sourceVectors.length === 0) {
        alert('No source vectors available. Please upload and extract features first.');
        setGenerating(false);
        return;
      }

      const result = await generateSynthetic(sourceVectors, count, method, true);

      if (result.success) {
        setSyntheticVectors(result.synthetic_vectors.map((vec, idx) => ({
          id: `synthetic_${idx}`,
          vector: vec,
          method: result.method,
          timestamp: new Date().toISOString(),
        })));
      } else {
        alert(result.error || 'Failed to generate synthetic vectors');
      }
    } catch (error) {
      alert(error.message || 'Generation failed');
    } finally {
      setGenerating(false);
    }
  };

  const computeStats = (vector) => {
    if (!vector || vector.length === 0) return { mean: 0, std: 0, min: 0, max: 0 };
    const mean = vector.reduce((a, b) => a + b, 0) / vector.length;
    const variance = vector.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / vector.length;
    return {
      mean: mean.toFixed(4),
      std: Math.sqrt(variance).toFixed(4),
      min: Math.min(...vector).toFixed(4),
      max: Math.max(...vector).toFixed(4),
    };
  };

  const computeSimilarity = (vec1, vec2) => {
    if (!vec1 || !vec2 || vec1.length !== vec2.length) return 0;
    
    let dotProduct = 0;
    let norm1 = 0;
    let norm2 = 0;
    
    for (let i = 0; i < vec1.length; i++) {
      dotProduct += vec1[i] * vec2[i];
      norm1 += vec1[i] * vec1[i];
      norm2 += vec2[i] * vec2[i];
    }
    
    const magnitude = Math.sqrt(norm1) * Math.sqrt(norm2);
    return magnitude === 0 ? 0 : (dotProduct / magnitude).toFixed(4);
  };

  const renderVectorCard = (item, isReal = false) => {
    const stats = computeStats(item.vector);
    const isSelected = isReal 
      ? selectedReal?.id === item.id 
      : selectedSynthetic?.id === item.id;

    return (
      <Card 
        style={[styles.vectorCard, isSelected && styles.selectedCard]}
        onPress={() => {
          if (compareMode) {
            if (isReal) {
              setSelectedReal(isSelected ? null : item);
            } else {
              setSelectedSynthetic(isSelected ? null : item);
            }
          }
        }}
      >
        <Card.Content>
          <View style={styles.vectorHeader}>
            <Text style={styles.vectorId}>{item.id}</Text>
            <Chip compact style={isReal ? styles.realChip : styles.syntheticChip}>
              {isReal ? 'Real' : 'Synthetic'}
            </Chip>
          </View>
          <View style={styles.statsRow}>
            <Text style={styles.statItem}>μ: {stats.mean}</Text>
            <Text style={styles.statItem}>σ: {stats.std}</Text>
            <Text style={styles.statItem}>↓: {stats.min}</Text>
            <Text style={styles.statItem}>↑: {stats.max}</Text>
          </View>
          {item.method && (
            <Text style={styles.methodText}>Method: {item.method}</Text>
          )}
        </Card.Content>
      </Card>
    );
  };

  const renderComparison = () => {
    if (!selectedReal || !selectedSynthetic) {
      return (
        <Card style={styles.comparisonCard}>
          <Card.Content>
            <Text style={styles.comparisonHint}>
              Select one real and one synthetic vector to compare
            </Text>
          </Card.Content>
        </Card>
      );
    }

    const similarity = computeSimilarity(selectedReal.vector, selectedSynthetic.vector);
    const realStats = computeStats(selectedReal.vector);
    const syntheticStats = computeStats(selectedSynthetic.vector);

    return (
      <Card style={styles.comparisonCard}>
        <Card.Title title="Comparison" />
        <Card.Content>
          <View style={styles.similarityRow}>
            <Text style={styles.similarityLabel}>Cosine Similarity:</Text>
            <Text style={styles.similarityValue}>{similarity}</Text>
          </View>
          
          <DataTable>
            <DataTable.Header>
              <DataTable.Title>Metric</DataTable.Title>
              <DataTable.Title numeric>Real</DataTable.Title>
              <DataTable.Title numeric>Synthetic</DataTable.Title>
              <DataTable.Title numeric>Diff</DataTable.Title>
            </DataTable.Header>
            
            <DataTable.Row>
              <DataTable.Cell>Mean</DataTable.Cell>
              <DataTable.Cell numeric>{realStats.mean}</DataTable.Cell>
              <DataTable.Cell numeric>{syntheticStats.mean}</DataTable.Cell>
              <DataTable.Cell numeric>
                {(parseFloat(syntheticStats.mean) - parseFloat(realStats.mean)).toFixed(4)}
              </DataTable.Cell>
            </DataTable.Row>
            
            <DataTable.Row>
              <DataTable.Cell>Std Dev</DataTable.Cell>
              <DataTable.Cell numeric>{realStats.std}</DataTable.Cell>
              <DataTable.Cell numeric>{syntheticStats.std}</DataTable.Cell>
              <DataTable.Cell numeric>
                {(parseFloat(syntheticStats.std) - parseFloat(realStats.std)).toFixed(4)}
              </DataTable.Cell>
            </DataTable.Row>
            
            <DataTable.Row>
              <DataTable.Cell>Min</DataTable.Cell>
              <DataTable.Cell numeric>{realStats.min}</DataTable.Cell>
              <DataTable.Cell numeric>{syntheticStats.min}</DataTable.Cell>
              <DataTable.Cell numeric>
                {(parseFloat(syntheticStats.min) - parseFloat(realStats.min)).toFixed(4)}
              </DataTable.Cell>
            </DataTable.Row>
            
            <DataTable.Row>
              <DataTable.Cell>Max</DataTable.Cell>
              <DataTable.Cell numeric>{realStats.max}</DataTable.Cell>
              <DataTable.Cell numeric>{syntheticStats.max}</DataTable.Cell>
              <DataTable.Cell numeric>
                {(parseFloat(syntheticStats.max) - parseFloat(realStats.max)).toFixed(4)}
              </DataTable.Cell>
            </DataTable.Row>
          </DataTable>
        </Card.Content>
      </Card>
    );
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Title title="Synthetic Data Generator" subtitle="Generate synthetic behavior vectors" />
        <Card.Content>
          <Text style={styles.label}>Generation Method</Text>
          <SegmentedButtons
            value={method}
            onValueChange={setMethod}
            buttons={methods}
            style={styles.segmented}
          />

          <Text style={styles.label}>Number of Vectors: {count}</Text>
          <View style={styles.sliderContainer}>
            <IconButton
              icon="minus"
              size={24}
              onPress={() => setCount(Math.max(1, count - 1))}
              disabled={count <= 1}
            />
            <TextInput
              mode="outlined"
              value={count.toString()}
              onChangeText={(text) => {
                const num = parseInt(text, 10);
                if (!isNaN(num) && num >= 1 && num <= 50) {
                  setCount(num);
                }
              }}
              keyboardType="numeric"
              style={styles.sliderInput}
              dense
            />
            <IconButton
              icon="plus"
              size={24}
              onPress={() => setCount(Math.min(50, count + 1))}
              disabled={count >= 50}
            />
          </View>

          <Button
            mode="contained"
            onPress={handleGenerate}
            loading={generating}
            disabled={generating}
            style={styles.generateButton}
            icon="creation"
          >
            Generate Synthetic Vectors
          </Button>
        </Card.Content>
      </Card>

      {syntheticVectors.length > 0 && (
        <>
          <Card style={styles.card}>
            <Card.Title 
              title="Generated Vectors" 
              subtitle={`${syntheticVectors.length} synthetic vectors`}
              right={() => (
                <Chip
                  selected={compareMode}
                  onPress={() => setCompareMode(!compareMode)}
                  style={styles.compareModeChip}
                >
                  Compare Mode
                </Chip>
              )}
            />
            <Card.Content>
              <FlatList
                data={syntheticVectors}
                renderItem={({ item }) => renderVectorCard(item, false)}
                keyExtractor={item => item.id}
                horizontal
                showsHorizontalScrollIndicator={false}
                style={styles.vectorList}
              />
            </Card.Content>
          </Card>

          {compareMode && (
            <>
              <Card style={styles.card}>
                <Card.Title title="Real Vectors" subtitle="Select one to compare" />
                <Card.Content>
                  <FlatList
                    data={vectors}
                    renderItem={({ item }) => renderVectorCard(item, true)}
                    keyExtractor={item => item.id}
                    horizontal
                    showsHorizontalScrollIndicator={false}
                    style={styles.vectorList}
                  />
                </Card.Content>
              </Card>

              {renderComparison()}
            </>
          )}
        </>
      )}

      {generating && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" />
          <Text style={styles.loadingText}>Generating synthetic vectors...</Text>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  card: {
    margin: 10,
    elevation: 2,
  },
  label: {
    fontSize: 14,
    fontWeight: 'bold',
    marginTop: 12,
    marginBottom: 8,
    color: '#333',
  },
  segmented: {
    marginBottom: 8,
  },
  sliderContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 8,
  },
  sliderInput: {
    width: 80,
    textAlign: 'center',
    marginHorizontal: 8,
  },
  generateButton: {
    marginTop: 16,
  },
  vectorList: {
    marginVertical: 8,
  },
  vectorCard: {
    width: 200,
    marginRight: 12,
    elevation: 2,
  },
  selectedCard: {
    borderWidth: 2,
    borderColor: '#6200ee',
  },
  vectorHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  vectorId: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#333',
  },
  realChip: {
    backgroundColor: '#4CAF50',
  },
  syntheticChip: {
    backgroundColor: '#2196F3',
  },
  statsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  statItem: {
    fontSize: 11,
    color: '#666',
    marginRight: 8,
    fontFamily: 'monospace',
  },
  methodText: {
    fontSize: 10,
    color: '#999',
    marginTop: 4,
  },
  compareModeChip: {
    marginRight: 8,
  },
  comparisonCard: {
    margin: 10,
    elevation: 3,
    backgroundColor: '#fff',
  },
  comparisonHint: {
    textAlign: 'center',
    color: '#666',
    fontStyle: 'italic',
  },
  similarityRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
    padding: 12,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
  },
  similarityLabel: {
    fontSize: 16,
    marginRight: 8,
  },
  similarityValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#6200ee',
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(255,255,255,0.9)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    color: '#666',
  },
});

export default SyntheticScreen;
