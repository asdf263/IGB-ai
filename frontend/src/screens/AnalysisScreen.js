import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, Dimensions } from 'react-native';
import { Card, Text, Chip, List, Divider, Button } from 'react-native-paper';

const { width } = Dimensions.get('window');

const AnalysisScreen = ({ route, navigation }) => {
  const { vector, labels, categories } = route.params || {};
  const [expandedCategories, setExpandedCategories] = useState({});
  const [viewMode, setViewMode] = useState('categories');

  const categoryColors = {
    temporal: '#FF6B6B',
    text: '#4ECDC4',
    linguistic: '#45B7D1',
    semantic: '#96CEB4',
    sentiment: '#FFEAA7',
    behavioral: '#DDA0DD',
    graph: '#98D8C8',
    composite: '#F7DC6F',
  };

  const toggleCategory = (category) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  const formatValue = (value) => {
    if (typeof value === 'number') {
      if (Math.abs(value) < 0.001 && value !== 0) {
        return value.toExponential(2);
      }
      return value.toFixed(4);
    }
    return String(value);
  };

  const getValueColor = (value) => {
    if (typeof value !== 'number') return '#333';
    if (value > 0.7) return '#4CAF50';
    if (value > 0.3) return '#FF9800';
    if (value < 0) return '#F44336';
    return '#666';
  };

  const renderFeatureBar = (value, maxValue = 1) => {
    const normalizedValue = Math.min(Math.abs(value) / maxValue, 1);
    const barColor = value >= 0 ? '#4ECDC4' : '#FF6B6B';
    
    return (
      <View style={styles.barContainer}>
        <View 
          style={[
            styles.bar, 
            { width: `${normalizedValue * 100}%`, backgroundColor: barColor }
          ]} 
        />
      </View>
    );
  };

  const renderCategorySection = (categoryName, features) => {
    const isExpanded = expandedCategories[categoryName];
    const featureEntries = Object.entries(features);
    const avgValue = featureEntries.reduce((sum, [, v]) => sum + (typeof v === 'number' ? v : 0), 0) / featureEntries.length;

    return (
      <Card key={categoryName} style={[styles.categoryCard, { borderLeftColor: categoryColors[categoryName] || '#999' }]}>
        <List.Accordion
          title={categoryName.charAt(0).toUpperCase() + categoryName.slice(1)}
          description={`${featureEntries.length} features • avg: ${formatValue(avgValue)}`}
          expanded={isExpanded}
          onPress={() => toggleCategory(categoryName)}
          left={props => (
            <View style={[styles.categoryDot, { backgroundColor: categoryColors[categoryName] || '#999' }]} />
          )}
        >
          {featureEntries.map(([featureName, value]) => (
            <View key={featureName} style={styles.featureRow}>
              <View style={styles.featureInfo}>
                <Text style={styles.featureName}>
                  {featureName.replace(/_/g, ' ')}
                </Text>
                <Text style={[styles.featureValue, { color: getValueColor(value) }]}>
                  {formatValue(value)}
                </Text>
              </View>
              {renderFeatureBar(value)}
            </View>
          ))}
        </List.Accordion>
      </Card>
    );
  };

  const renderSummaryView = () => {
    if (!categories) return null;

    const summaryData = Object.entries(categories).map(([cat, features]) => {
      const values = Object.values(features).filter(v => typeof v === 'number');
      return {
        category: cat,
        count: Object.keys(features).length,
        mean: values.reduce((a, b) => a + b, 0) / values.length,
        max: Math.max(...values),
        min: Math.min(...values),
      };
    });

    return (
      <Card style={styles.card}>
        <Card.Title title="Category Summary" />
        <Card.Content>
          {summaryData.map(({ category, count, mean, max, min }) => (
            <View key={category} style={styles.summaryRow}>
              <View style={styles.summaryHeader}>
                <View style={[styles.categoryDot, { backgroundColor: categoryColors[category] || '#999' }]} />
                <Text style={styles.summaryCategory}>{category}</Text>
                <Chip compact style={styles.countChip}>{count}</Chip>
              </View>
              <View style={styles.summaryStats}>
                <Text style={styles.statLabel}>Mean: <Text style={styles.statValue}>{formatValue(mean)}</Text></Text>
                <Text style={styles.statLabel}>Max: <Text style={styles.statValue}>{formatValue(max)}</Text></Text>
                <Text style={styles.statLabel}>Min: <Text style={styles.statValue}>{formatValue(min)}</Text></Text>
              </View>
              {renderFeatureBar(mean)}
              <Divider style={styles.divider} />
            </View>
          ))}
        </Card.Content>
      </Card>
    );
  };

  if (!vector || !labels) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>No analysis data available</Text>
        <Button mode="contained" onPress={() => navigation.navigate('Upload')}>
          Upload Chat Log
        </Button>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.headerCard}>
        <Card.Content>
          <Text style={styles.headerTitle}>Behavior Vector Analysis</Text>
          <Text style={styles.headerSubtitle}>{vector.length} features extracted</Text>
          <View style={styles.modeSelector}>
            <Chip
              selected={viewMode === 'summary'}
              onPress={() => setViewMode('summary')}
              style={styles.modeChip}
            >
              Summary
            </Chip>
            <Chip
              selected={viewMode === 'categories'}
              onPress={() => setViewMode('categories')}
              style={styles.modeChip}
            >
              By Category
            </Chip>
          </View>
        </Card.Content>
      </Card>

      {viewMode === 'summary' && renderSummaryView()}

      {viewMode === 'categories' && categories && (
        Object.entries(categories).map(([categoryName, features]) => 
          renderCategorySection(categoryName, features)
        )
      )}

      <View style={styles.actionButtons}>
        <Button
          mode="outlined"
          onPress={() => navigation.navigate('VectorDetail', { vector, labels })}
          style={styles.actionButton}
          icon="format-list-bulleted"
        >
          View All Features
        </Button>
        <Button
          mode="outlined"
          onPress={() => navigation.navigate('ClusterGraph')}
          style={styles.actionButton}
          icon="graph"
        >
          View Clusters
        </Button>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  emptyText: {
    fontSize: 16,
    color: '#666',
    marginBottom: 20,
  },
  headerCard: {
    margin: 10,
    backgroundColor: '#E07A5F',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  headerSubtitle: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.8)',
    marginTop: 4,
  },
  modeSelector: {
    flexDirection: 'row',
    marginTop: 16,
  },
  modeChip: {
    marginRight: 8,
    backgroundColor: 'rgba(255,255,255,0.2)',
  },
  card: {
    margin: 10,
    elevation: 2,
  },
  categoryCard: {
    margin: 10,
    marginBottom: 5,
    elevation: 2,
    borderLeftWidth: 4,
  },
  categoryDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  featureRow: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#fafafa',
  },
  featureInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  featureName: {
    fontSize: 12,
    color: '#666',
    flex: 1,
    textTransform: 'capitalize',
  },
  featureValue: {
    fontSize: 12,
    fontWeight: 'bold',
    fontFamily: 'monospace',
  },
  barContainer: {
    height: 4,
    backgroundColor: '#e0e0e0',
    borderRadius: 2,
    overflow: 'hidden',
  },
  bar: {
    height: '100%',
    borderRadius: 2,
  },
  summaryRow: {
    marginBottom: 12,
  },
  summaryHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  summaryCategory: {
    fontSize: 16,
    fontWeight: 'bold',
    textTransform: 'capitalize',
    flex: 1,
  },
  countChip: {
    height: 24,
  },
  summaryStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
  },
  statValue: {
    fontWeight: 'bold',
    color: '#333',
  },
  divider: {
    marginTop: 12,
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 16,
    marginBottom: 20,
  },
  actionButton: {
    flex: 1,
    marginHorizontal: 4,
  },
});

export default AnalysisScreen;
