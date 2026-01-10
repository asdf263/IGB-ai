import React, { useState, useEffect, useRef } from 'react';
import { View, StyleSheet, Dimensions, PanResponder, Animated } from 'react-native';
import { Card, Text, Chip, Button, ActivityIndicator, Portal, Modal } from 'react-native-paper';
import Svg, { Circle, Line, G, Text as SvgText } from 'react-native-svg';
import { getVisualizationGraph } from '../services/vectorApi';

const { width, height } = Dimensions.get('window');
const GRAPH_WIDTH = width - 40;
const GRAPH_HEIGHT = height * 0.6;

const ClusterGraphScreen = ({ navigation }) => {
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [scale, setScale] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });

  const pan = useRef(new Animated.ValueXY()).current;
  const lastOffset = useRef({ x: 0, y: 0 });

  useEffect(() => {
    loadGraphData();
  }, []);

  const loadGraphData = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getVisualizationGraph();
      if (result.success) {
        const normalizedData = normalizeCoordinates(result);
        setGraphData(normalizedData);
      } else {
        setError(result.error || 'Failed to load graph');
      }
    } catch (err) {
      setError(err.message || 'Failed to load graph');
    } finally {
      setLoading(false);
    }
  };

  const normalizeCoordinates = (data) => {
    if (!data.nodes || data.nodes.length === 0) return data;

    const { bounds } = data;
    const padding = 40;
    const availableWidth = GRAPH_WIDTH - padding * 2;
    const availableHeight = GRAPH_HEIGHT - padding * 2;

    const xRange = bounds.max_x - bounds.min_x || 1;
    const yRange = bounds.max_y - bounds.min_y || 1;

    const normalizedNodes = data.nodes.map(node => ({
      ...node,
      screenX: padding + ((node.x - bounds.min_x) / xRange) * availableWidth,
      screenY: padding + ((node.y - bounds.min_y) / yRange) * availableHeight,
    }));

    return { ...data, nodes: normalizedNodes };
  };

  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onMoveShouldSetPanResponder: () => true,
      onPanResponderGrant: () => {
        pan.setOffset({
          x: lastOffset.current.x,
          y: lastOffset.current.y,
        });
        pan.setValue({ x: 0, y: 0 });
      },
      onPanResponderMove: Animated.event(
        [null, { dx: pan.x, dy: pan.y }],
        { useNativeDriver: false }
      ),
      onPanResponderRelease: (_, gesture) => {
        lastOffset.current = {
          x: lastOffset.current.x + gesture.dx,
          y: lastOffset.current.y + gesture.dy,
        };
        pan.flattenOffset();
      },
    })
  ).current;

  const handleNodePress = (node) => {
    setSelectedNode(node);
    setShowModal(true);
  };

  const handleZoomIn = () => {
    setScale(prev => Math.min(prev * 1.2, 3));
  };

  const handleZoomOut = () => {
    setScale(prev => Math.max(prev / 1.2, 0.5));
  };

  const handleReset = () => {
    setScale(1);
    lastOffset.current = { x: 0, y: 0 };
    pan.setValue({ x: 0, y: 0 });
  };

  const renderGraph = () => {
    if (!graphData || !graphData.nodes) return null;

    const { nodes, edges } = graphData;

    return (
      <Animated.View
        style={[
          styles.graphContainer,
          {
            transform: [
              { translateX: pan.x },
              { translateY: pan.y },
              { scale },
            ],
          },
        ]}
        {...panResponder.panHandlers}
      >
        <Svg width={GRAPH_WIDTH} height={GRAPH_HEIGHT}>
          <G>
            {edges && edges.map((edge, index) => {
              const sourceNode = nodes.find(n => n.id === edge.source);
              const targetNode = nodes.find(n => n.id === edge.target);
              if (!sourceNode || !targetNode) return null;

              return (
                <Line
                  key={`edge-${index}`}
                  x1={sourceNode.screenX}
                  y1={sourceNode.screenY}
                  x2={targetNode.screenX}
                  y2={targetNode.screenY}
                  stroke={edge.same_cluster ? '#ccc' : '#eee'}
                  strokeWidth={edge.weight * 2}
                  opacity={0.5}
                />
              );
            })}

            {nodes.map((node, index) => (
              <G key={`node-${index}`}>
                <Circle
                  cx={node.screenX}
                  cy={node.screenY}
                  r={node.size || 10}
                  fill={node.color}
                  stroke="#fff"
                  strokeWidth={2}
                  onPress={() => handleNodePress(node)}
                />
                <SvgText
                  x={node.screenX}
                  y={node.screenY + node.size + 12}
                  fontSize={8}
                  fill="#666"
                  textAnchor="middle"
                >
                  {node.id.replace('node_', '')}
                </SvgText>
              </G>
            ))}
          </G>
        </Svg>
      </Animated.View>
    );
  };

  const renderLegend = () => {
    if (!graphData || !graphData.clusters) return null;

    return (
      <View style={styles.legend}>
        {graphData.clusters.map((cluster, index) => (
          <Chip
            key={index}
            style={[styles.legendChip, { backgroundColor: cluster.color }]}
            textStyle={styles.legendText}
          >
            Cluster {cluster.id} ({cluster.count})
          </Chip>
        ))}
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" />
        <Text style={styles.loadingText}>Loading cluster graph...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>{error}</Text>
        <Button mode="contained" onPress={loadGraphData} style={styles.retryButton}>
          Retry
        </Button>
        <Button mode="outlined" onPress={() => navigation.navigate('Upload')} style={styles.uploadButton}>
          Upload Data First
        </Button>
      </View>
    );
  }

  if (!graphData || graphData.nodes.length === 0) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.emptyText}>No vectors to visualize</Text>
        <Button mode="contained" onPress={() => navigation.navigate('Upload')}>
          Upload Chat Log
        </Button>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Card style={styles.graphCard}>
        <Card.Title 
          title="Cluster Visualization" 
          subtitle={`${graphData.nodes.length} vectors • ${graphData.clusters?.length || 0} clusters`}
        />
        <Card.Content>
          {renderGraph()}
        </Card.Content>
      </Card>

      <View style={styles.controls}>
        <Button mode="outlined" onPress={handleZoomIn} compact icon="magnify-plus">
          Zoom In
        </Button>
        <Button mode="outlined" onPress={handleZoomOut} compact icon="magnify-minus">
          Zoom Out
        </Button>
        <Button mode="outlined" onPress={handleReset} compact icon="refresh">
          Reset
        </Button>
      </View>

      {renderLegend()}

      <Portal>
        <Modal
          visible={showModal}
          onDismiss={() => setShowModal(false)}
          contentContainerStyle={styles.modal}
        >
          {selectedNode && (
            <View>
              <Text style={styles.modalTitle}>Node Details</Text>
              <Text style={styles.modalText}>ID: {selectedNode.id}</Text>
              <Text style={styles.modalText}>Cluster: {selectedNode.cluster}</Text>
              <Text style={styles.modalText}>Position: ({selectedNode.x?.toFixed(2)}, {selectedNode.y?.toFixed(2)})</Text>
              {selectedNode.vector_summary && (
                <>
                  <Text style={styles.modalSubtitle}>Vector Summary</Text>
                  <Text style={styles.modalText}>Mean: {selectedNode.vector_summary.mean?.toFixed(4)}</Text>
                  <Text style={styles.modalText}>Std: {selectedNode.vector_summary.std?.toFixed(4)}</Text>
                  <Text style={styles.modalText}>Range: [{selectedNode.vector_summary.min?.toFixed(4)}, {selectedNode.vector_summary.max?.toFixed(4)}]</Text>
                </>
              )}
              <Button mode="contained" onPress={() => setShowModal(false)} style={styles.modalButton}>
                Close
              </Button>
            </View>
          )}
        </Modal>
      </Portal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 16,
    color: '#666',
  },
  errorText: {
    color: '#F44336',
    marginBottom: 16,
    textAlign: 'center',
  },
  emptyText: {
    color: '#666',
    marginBottom: 16,
  },
  retryButton: {
    marginBottom: 8,
  },
  uploadButton: {
    marginTop: 8,
  },
  graphCard: {
    margin: 10,
    flex: 1,
  },
  graphContainer: {
    backgroundColor: '#fff',
    borderRadius: 8,
    overflow: 'hidden',
  },
  controls: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 10,
    backgroundColor: '#fff',
  },
  legend: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    padding: 10,
    backgroundColor: '#fff',
  },
  legendChip: {
    margin: 4,
  },
  legendText: {
    color: '#fff',
    fontSize: 12,
  },
  modal: {
    backgroundColor: '#fff',
    padding: 20,
    margin: 20,
    borderRadius: 8,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  modalSubtitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 12,
    marginBottom: 8,
  },
  modalText: {
    fontSize: 14,
    marginBottom: 4,
    color: '#333',
  },
  modalButton: {
    marginTop: 16,
  },
});

export default ClusterGraphScreen;
