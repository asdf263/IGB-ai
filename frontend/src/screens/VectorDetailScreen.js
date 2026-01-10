import React, { useState, useMemo } from 'react';
import { View, StyleSheet, ScrollView, FlatList } from 'react-native';
import { Card, Text, Searchbar, Chip, DataTable, Button } from 'react-native-paper';

const VectorDetailScreen = ({ route, navigation }) => {
  const { vector, labels } = route.params || {};
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('index');
  const [sortOrder, setSortOrder] = useState('asc');
  const [filterCategory, setFilterCategory] = useState(null);

  const categories = useMemo(() => {
    if (!labels) return [];
    const cats = new Set();
    labels.forEach(label => {
      const category = label.split('_')[0];
      cats.add(category);
    });
    return Array.from(cats);
  }, [labels]);

  const featureData = useMemo(() => {
    if (!vector || !labels) return [];

    let data = vector.map((value, index) => ({
      index,
      label: labels[index],
      value,
      category: labels[index].split('_')[0],
      displayName: labels[index].split('_').slice(1).join(' '),
    }));

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      data = data.filter(item => 
        item.label.toLowerCase().includes(query) ||
        item.displayName.toLowerCase().includes(query)
      );
    }

    if (filterCategory) {
      data = data.filter(item => item.category === filterCategory);
    }

    data.sort((a, b) => {
      let comparison = 0;
      if (sortBy === 'index') {
        comparison = a.index - b.index;
      } else if (sortBy === 'value') {
        comparison = a.value - b.value;
      } else if (sortBy === 'name') {
        comparison = a.label.localeCompare(b.label);
      } else if (sortBy === 'absValue') {
        comparison = Math.abs(a.value) - Math.abs(b.value);
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });

    return data;
  }, [vector, labels, searchQuery, sortBy, sortOrder, filterCategory]);

  const formatValue = (value) => {
    if (Math.abs(value) < 0.0001 && value !== 0) {
      return value.toExponential(2);
    }
    return value.toFixed(6);
  };

  const getValueStyle = (value) => {
    if (value > 0.7) return styles.highValue;
    if (value > 0.3) return styles.mediumValue;
    if (value < 0) return styles.negativeValue;
    return styles.normalValue;
  };

  const toggleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  const renderItem = ({ item }) => (
    <DataTable.Row key={item.index}>
      <DataTable.Cell style={styles.indexCell}>
        <Text style={styles.indexText}>{item.index}</Text>
      </DataTable.Cell>
      <DataTable.Cell style={styles.nameCell}>
        <View>
          <Text style={styles.featureName} numberOfLines={1}>
            {item.displayName}
          </Text>
          <Text style={styles.categoryLabel}>{item.category}</Text>
        </View>
      </DataTable.Cell>
      <DataTable.Cell numeric style={styles.valueCell}>
        <Text style={[styles.valueText, getValueStyle(item.value)]}>
          {formatValue(item.value)}
        </Text>
      </DataTable.Cell>
    </DataTable.Row>
  );

  if (!vector || !labels) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>No vector data available</Text>
        <Button mode="contained" onPress={() => navigation.navigate('Upload')}>
          Upload Chat Log
        </Button>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Card style={styles.headerCard}>
        <Card.Content>
          <Searchbar
            placeholder="Search features..."
            onChangeText={setSearchQuery}
            value={searchQuery}
            style={styles.searchbar}
          />
          
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterRow}>
            <Chip
              selected={filterCategory === null}
              onPress={() => setFilterCategory(null)}
              style={styles.filterChip}
            >
              All ({labels.length})
            </Chip>
            {categories.map(cat => (
              <Chip
                key={cat}
                selected={filterCategory === cat}
                onPress={() => setFilterCategory(filterCategory === cat ? null : cat)}
                style={styles.filterChip}
              >
                {cat}
              </Chip>
            ))}
          </ScrollView>

          <View style={styles.sortRow}>
            <Text style={styles.sortLabel}>Sort by:</Text>
            <Chip
              selected={sortBy === 'index'}
              onPress={() => toggleSort('index')}
              compact
              style={styles.sortChip}
            >
              Index {sortBy === 'index' && (sortOrder === 'asc' ? '↑' : '↓')}
            </Chip>
            <Chip
              selected={sortBy === 'value'}
              onPress={() => toggleSort('value')}
              compact
              style={styles.sortChip}
            >
              Value {sortBy === 'value' && (sortOrder === 'asc' ? '↑' : '↓')}
            </Chip>
            <Chip
              selected={sortBy === 'absValue'}
              onPress={() => toggleSort('absValue')}
              compact
              style={styles.sortChip}
            >
              |Value| {sortBy === 'absValue' && (sortOrder === 'asc' ? '↑' : '↓')}
            </Chip>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.tableCard}>
        <DataTable>
          <DataTable.Header>
            <DataTable.Title style={styles.indexCell}>#</DataTable.Title>
            <DataTable.Title style={styles.nameCell}>Feature</DataTable.Title>
            <DataTable.Title numeric style={styles.valueCell}>Value</DataTable.Title>
          </DataTable.Header>

          <FlatList
            data={featureData}
            renderItem={renderItem}
            keyExtractor={item => item.index.toString()}
            style={styles.list}
            initialNumToRender={20}
            maxToRenderPerBatch={20}
            windowSize={10}
          />
        </DataTable>
      </Card>

      <View style={styles.statsBar}>
        <Text style={styles.statsText}>
          Showing {featureData.length} of {labels.length} features
        </Text>
      </View>
    </View>
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
    marginBottom: 5,
  },
  searchbar: {
    marginBottom: 12,
  },
  filterRow: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  filterChip: {
    marginRight: 8,
  },
  sortRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  sortLabel: {
    marginRight: 8,
    color: '#666',
  },
  sortChip: {
    marginRight: 8,
  },
  tableCard: {
    flex: 1,
    margin: 10,
    marginTop: 5,
  },
  list: {
    maxHeight: '100%',
  },
  indexCell: {
    flex: 0.5,
  },
  nameCell: {
    flex: 2,
  },
  valueCell: {
    flex: 1,
  },
  indexText: {
    fontSize: 12,
    color: '#999',
  },
  featureName: {
    fontSize: 13,
    textTransform: 'capitalize',
  },
  categoryLabel: {
    fontSize: 10,
    color: '#999',
    textTransform: 'uppercase',
  },
  valueText: {
    fontFamily: 'monospace',
    fontSize: 12,
  },
  highValue: {
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  mediumValue: {
    color: '#FF9800',
  },
  negativeValue: {
    color: '#F44336',
  },
  normalValue: {
    color: '#333',
  },
  statsBar: {
    padding: 10,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  statsText: {
    textAlign: 'center',
    color: '#666',
    fontSize: 12,
  },
});

export default VectorDetailScreen;
