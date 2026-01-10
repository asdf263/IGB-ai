"""
IGB AI - Behavior Vector Extraction API
Flask backend with feature extraction, synthetic generation, clustering, and visualization
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from dotenv import load_dotenv
import json
from datetime import datetime

from services.feature_extractor import FeatureExtractor
from services.synthetic_generator import SyntheticGenerator
from services.clustering_service import ClusteringService
from services.visualization_service import VisualizationService
from services.vector_store import VectorStore

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

feature_extractor = FeatureExtractor()
synthetic_generator = SyntheticGenerator()
clustering_service = ClusteringService()
visualization_service = VisualizationService()
vector_store = VectorStore(storage_path='data/vectors.json')

os.makedirs('data', exist_ok=True)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'IGB-AI Vector API',
        'feature_count': feature_extractor.get_feature_count(),
        'stored_vectors': vector_store.count()
    }), 200


@app.route('/api/features/extract', methods=['POST'])
def extract_features():
    """
    Extract behavior vector features from chat messages.
    
    Input:
    {
        "messages": [
            {"sender": "user", "text": "Hello", "timestamp": 1715234000},
            {"sender": "bot", "text": "Hi there!", "timestamp": 1715234012}
        ]
    }
    
    Output:
    {
        "vector": [...],
        "feature_labels": [...],
        "feature_count": 200,
        "categories": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'messages' not in data:
            return jsonify({'error': 'No messages provided'}), 400
        
        messages = data['messages']
        
        if not isinstance(messages, list):
            return jsonify({'error': 'Messages must be a list'}), 400
        
        if len(messages) == 0:
            return jsonify({'error': 'Messages list is empty'}), 400
        
        vector, labels = feature_extractor.extract(messages)
        categories = feature_extractor.extract_by_category(messages)
        
        store_result = data.get('store', False)
        vector_id = None
        if store_result:
            metadata = {
                'message_count': len(messages),
                'extracted_at': datetime.now().isoformat()
            }
            vector_id = vector_store.add(vector, metadata)
        
        response = {
            'success': True,
            'vector': vector,
            'feature_labels': labels,
            'feature_count': len(vector),
            'categories': {k: dict(v) for k, v in categories.items()},
            'category_summary': feature_extractor.get_category_summary(messages)
        }
        
        if vector_id:
            response['vector_id'] = vector_id
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error extracting features: {str(e)}")
        return jsonify({'error': f'Feature extraction failed: {str(e)}'}), 500


@app.route('/api/features/synthetic-generate', methods=['POST'])
def generate_synthetic():
    """
    Generate synthetic behavior vectors.
    
    Input:
    {
        "vectors": [[...], [...]], // Original vectors
        "n_synthetic": 10,
        "method": "smote" // smote, noise, jitter, interpolate, adasyn
    }
    
    Output:
    {
        "synthetic_vectors": [[...], [...], ...]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        vectors = data.get('vectors', [])
        
        if not vectors:
            stored = vector_store.get_all_vectors()
            if stored:
                vectors = stored
            else:
                return jsonify({'error': 'No vectors provided and none stored'}), 400
        
        n_synthetic = data.get('n_synthetic', 10)
        method = data.get('method', 'smote')
        
        synthetic_vectors = synthetic_generator.generate_synthetic_vectors(
            vectors, n_synthetic, method
        )
        
        validated_vectors = []
        for vec in synthetic_vectors:
            is_valid, clipped = synthetic_generator.validate_vector(vec)
            validated_vectors.append(clipped)
        
        store_result = data.get('store', False)
        stored_ids = []
        if store_result:
            for i, vec in enumerate(validated_vectors):
                metadata = {
                    'synthetic': True,
                    'method': method,
                    'generated_at': datetime.now().isoformat()
                }
                vid = vector_store.add(vec, metadata)
                stored_ids.append(vid)
        
        response = {
            'success': True,
            'synthetic_vectors': validated_vectors,
            'count': len(validated_vectors),
            'method': method
        }
        
        if stored_ids:
            response['stored_ids'] = stored_ids
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error generating synthetic vectors: {str(e)}")
        return jsonify({'error': f'Synthetic generation failed: {str(e)}'}), 500


@app.route('/api/vectors/list', methods=['GET'])
def list_vectors():
    """
    List all stored vectors.
    
    Output:
    {
        "vectors": [
            {"id": "...", "vector": [...], "metadata": {...}},
            ...
        ],
        "count": 10
    }
    """
    try:
        vectors = vector_store.list_all()
        stats = vector_store.get_stats()
        
        return jsonify({
            'success': True,
            'vectors': vectors,
            'count': len(vectors),
            'stats': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing vectors: {str(e)}")
        return jsonify({'error': f'Failed to list vectors: {str(e)}'}), 500


@app.route('/api/vectors/<vector_id>', methods=['GET'])
def get_vector(vector_id):
    """Get a specific vector by ID."""
    try:
        vector_data = vector_store.get(vector_id)
        
        if not vector_data:
            return jsonify({'error': 'Vector not found'}), 404
        
        return jsonify({
            'success': True,
            'id': vector_id,
            'vector': vector_data['vector'],
            'metadata': vector_data['metadata'],
            'created_at': vector_data['created_at']
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting vector: {str(e)}")
        return jsonify({'error': f'Failed to get vector: {str(e)}'}), 500


@app.route('/api/vectors/<vector_id>', methods=['DELETE'])
def delete_vector(vector_id):
    """Delete a vector by ID."""
    try:
        success = vector_store.delete(vector_id)
        
        if not success:
            return jsonify({'error': 'Vector not found'}), 404
        
        return jsonify({
            'success': True,
            'message': f'Vector {vector_id} deleted'
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting vector: {str(e)}")
        return jsonify({'error': f'Failed to delete vector: {str(e)}'}), 500


@app.route('/api/vectors/cluster', methods=['POST'])
def cluster_vectors():
    """
    Cluster stored vectors.
    
    Input:
    {
        "vectors": [[...], [...]], // Optional, uses stored if not provided
        "cluster_method": "kmeans", // kmeans, hdbscan, agglomerative
        "reduce_method": "pca", // pca, umap, tsne
        "n_clusters": 5
    }
    
    Output:
    {
        "labels": [0, 1, 0, 2, ...],
        "reduced": [[x, y], ...],
        "centroids": [[...], ...],
        "cluster_stats": {...}
    }
    """
    try:
        data = request.get_json() or {}
        
        vectors = data.get('vectors', [])
        
        if not vectors:
            vectors = vector_store.get_all_vectors()
        
        if not vectors:
            return jsonify({'error': 'No vectors to cluster'}), 400
        
        cluster_method = data.get('cluster_method', 'kmeans')
        reduce_method = data.get('reduce_method', 'pca')
        n_clusters = data.get('n_clusters', 5)
        
        result = clustering_service.cluster_and_reduce(
            vectors,
            cluster_method=cluster_method,
            reduce_method=reduce_method,
            n_clusters=n_clusters
        )
        
        cluster_stats = clustering_service.get_cluster_stats(vectors, result['labels'])
        archetype_labels = clustering_service.assign_archetype_labels(cluster_stats)
        
        return jsonify({
            'success': True,
            'labels': result['labels'],
            'reduced': result['reduced'],
            'centroids': result['centroids'],
            'centroid_positions': result['centroid_positions'],
            'n_clusters': result['n_clusters'],
            'cluster_stats': {str(k): v for k, v in cluster_stats.items()},
            'archetype_labels': {str(k): v for k, v in archetype_labels.items()}
        }), 200
        
    except Exception as e:
        logger.error(f"Error clustering vectors: {str(e)}")
        return jsonify({'error': f'Clustering failed: {str(e)}'}), 500


@app.route('/api/visualization/graph', methods=['GET'])
def get_visualization_graph():
    """
    Get graph structure for cluster visualization.
    
    Output:
    {
        "nodes": [{"id": "...", "x": 0, "y": 0, "cluster": 0, ...}, ...],
        "edges": [{"source": "...", "target": "...", "weight": 0.8}, ...],
        "clusters": [{"id": 0, "count": 5, "color": "#FF6B6B"}, ...],
        "bounds": {"min_x": 0, "max_x": 100, ...}
    }
    """
    try:
        vectors = vector_store.get_all_vectors()
        
        if not vectors:
            return jsonify({
                'success': True,
                'nodes': [],
                'edges': [],
                'clusters': [],
                'bounds': {'min_x': 0, 'max_x': 1, 'min_y': 0, 'max_y': 1}
            }), 200
        
        result = clustering_service.cluster_and_reduce(vectors)
        
        all_entries = vector_store.list_all()
        metadata = [entry.get('metadata', {}) for entry in all_entries]
        
        graph = visualization_service.generate_cluster_graph(
            vectors,
            result['labels'],
            result['reduced'],
            metadata
        )
        
        return jsonify({
            'success': True,
            **graph
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating graph: {str(e)}")
        return jsonify({'error': f'Graph generation failed: {str(e)}'}), 500


@app.route('/api/visualization/heatmap', methods=['POST'])
def get_heatmap():
    """Get heatmap data for feature visualization."""
    try:
        data = request.get_json() or {}
        
        vector_id = data.get('vector_id')
        features = data.get('features')
        
        if vector_id:
            vector_data = vector_store.get(vector_id)
            if not vector_data:
                return jsonify({'error': 'Vector not found'}), 404
            
            labels = feature_extractor.get_feature_names()
            features = dict(zip(labels, vector_data['vector']))
        
        if not features:
            return jsonify({'error': 'No features provided'}), 400
        
        categories = ['temporal', 'text', 'linguistic', 'semantic', 
                     'sentiment', 'behavioral', 'graph', 'composite']
        
        heatmap = visualization_service.generate_feature_heatmap(features, categories)
        
        return jsonify({
            'success': True,
            **heatmap
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating heatmap: {str(e)}")
        return jsonify({'error': f'Heatmap generation failed: {str(e)}'}), 500


@app.route('/api/visualization/radar', methods=['POST'])
def get_radar():
    """Get radar chart data for category scores."""
    try:
        data = request.get_json() or {}
        
        messages = data.get('messages')
        category_scores = data.get('category_scores')
        
        if messages:
            category_scores = feature_extractor.get_category_summary(messages)
        
        if not category_scores:
            return jsonify({'error': 'No data provided'}), 400
        
        radar = visualization_service.generate_radar_chart_data(category_scores)
        
        return jsonify({
            'success': True,
            **radar
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating radar: {str(e)}")
        return jsonify({'error': f'Radar generation failed: {str(e)}'}), 500


@app.route('/api/vectors/search', methods=['POST'])
def search_vectors():
    """Search for similar vectors."""
    try:
        data = request.get_json()
        
        if not data or 'query_vector' not in data:
            return jsonify({'error': 'No query vector provided'}), 400
        
        query_vector = data['query_vector']
        top_k = data.get('top_k', 5)
        threshold = data.get('threshold', 0.0)
        
        results = vector_store.search_similar(query_vector, top_k, threshold)
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching vectors: {str(e)}")
        return jsonify({'error': f'Search failed: {str(e)}'}), 500


@app.route('/api/features/labels', methods=['GET'])
def get_feature_labels():
    """Get all feature labels."""
    try:
        labels = feature_extractor.get_feature_names()
        
        categories = {}
        for label in labels:
            category = label.split('_')[0]
            if category not in categories:
                categories[category] = []
            categories[category].append(label)
        
        return jsonify({
            'success': True,
            'labels': labels,
            'count': len(labels),
            'categories': categories
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting labels: {str(e)}")
        return jsonify({'error': f'Failed to get labels: {str(e)}'}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
