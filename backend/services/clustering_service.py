"""
Clustering Service Module
Provides UMAP, PCA, KMeans, and HDBSCAN clustering for behavior vectors
"""
import numpy as np
from typing import List, Dict, Any, Optional, Tuple


class ClusteringService:
    """Service for clustering and dimensionality reduction of behavior vectors."""
    
    def __init__(self):
        self.umap_model = None
        self.pca_model = None
        self.kmeans_model = None
        self.last_labels = None
        self.last_reduced = None
    
    def reduce_dimensions(self, 
                         vectors: List[List[float]], 
                         method: str = 'pca',
                         n_components: int = 2) -> List[List[float]]:
        """
        Reduce dimensionality of vectors.
        
        Args:
            vectors: List of feature vectors
            method: Reduction method ('pca', 'umap', 'tsne')
            n_components: Number of output dimensions
            
        Returns:
            List of reduced vectors
        """
        if not vectors:
            return []
        
        arr = np.array(vectors)
        
        if arr.shape[0] < 2:
            return [[0.0] * n_components]
        
        if method == 'pca':
            reduced = self._pca_reduce(arr, n_components)
        elif method == 'umap':
            reduced = self._umap_reduce(arr, n_components)
        elif method == 'tsne':
            reduced = self._tsne_reduce(arr, n_components)
        else:
            reduced = self._pca_reduce(arr, n_components)
        
        self.last_reduced = reduced
        return reduced.tolist()
    
    def _pca_reduce(self, vectors: np.ndarray, n_components: int) -> np.ndarray:
        """Reduce dimensions using PCA."""
        try:
            from sklearn.decomposition import PCA
            n_components = min(n_components, vectors.shape[0], vectors.shape[1])
            pca = PCA(n_components=n_components)
            reduced = pca.fit_transform(vectors)
            self.pca_model = pca
            return reduced
        except ImportError:
            return self._simple_pca(vectors, n_components)
    
    def _simple_pca(self, vectors: np.ndarray, n_components: int) -> np.ndarray:
        """Simple PCA implementation without sklearn."""
        centered = vectors - np.mean(vectors, axis=0)
        cov = np.cov(centered.T)
        
        if cov.ndim == 0:
            return vectors[:, :n_components] if vectors.shape[1] >= n_components else vectors
        
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        
        idx = np.argsort(eigenvalues)[::-1]
        eigenvectors = eigenvectors[:, idx]
        
        n_components = min(n_components, eigenvectors.shape[1])
        projection_matrix = eigenvectors[:, :n_components]
        
        return np.dot(centered, projection_matrix)
    
    def _umap_reduce(self, vectors: np.ndarray, n_components: int) -> np.ndarray:
        """Reduce dimensions using UMAP."""
        try:
            import umap
            n_neighbors = min(15, vectors.shape[0] - 1)
            n_neighbors = max(2, n_neighbors)
            
            reducer = umap.UMAP(
                n_components=n_components,
                n_neighbors=n_neighbors,
                min_dist=0.1,
                metric='cosine'
            )
            reduced = reducer.fit_transform(vectors)
            self.umap_model = reducer
            return reduced
        except ImportError:
            return self._pca_reduce(vectors, n_components)
    
    def _tsne_reduce(self, vectors: np.ndarray, n_components: int) -> np.ndarray:
        """Reduce dimensions using t-SNE."""
        try:
            from sklearn.manifold import TSNE
            perplexity = min(30, vectors.shape[0] - 1)
            perplexity = max(5, perplexity)
            
            tsne = TSNE(
                n_components=n_components,
                perplexity=perplexity,
                random_state=42
            )
            return tsne.fit_transform(vectors)
        except ImportError:
            return self._pca_reduce(vectors, n_components)
    
    def cluster(self, 
                vectors: List[List[float]], 
                method: str = 'kmeans',
                n_clusters: int = 5) -> List[int]:
        """
        Cluster vectors.
        
        Args:
            vectors: List of feature vectors
            method: Clustering method ('kmeans', 'hdbscan', 'agglomerative')
            n_clusters: Number of clusters (for kmeans)
            
        Returns:
            List of cluster labels
        """
        if not vectors:
            return []
        
        arr = np.array(vectors)
        
        if arr.shape[0] < 2:
            return [0]
        
        if method == 'kmeans':
            labels = self._kmeans_cluster(arr, n_clusters)
        elif method == 'hdbscan':
            labels = self._hdbscan_cluster(arr)
        elif method == 'agglomerative':
            labels = self._agglomerative_cluster(arr, n_clusters)
        else:
            labels = self._kmeans_cluster(arr, n_clusters)
        
        self.last_labels = labels
        return labels.tolist()
    
    def _kmeans_cluster(self, vectors: np.ndarray, n_clusters: int) -> np.ndarray:
        """Cluster using KMeans."""
        try:
            from sklearn.cluster import KMeans
            n_clusters = min(n_clusters, vectors.shape[0])
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(vectors)
            self.kmeans_model = kmeans
            return labels
        except ImportError:
            return self._simple_kmeans(vectors, n_clusters)
    
    def _simple_kmeans(self, vectors: np.ndarray, n_clusters: int, max_iter: int = 100) -> np.ndarray:
        """Simple KMeans implementation without sklearn."""
        n_samples = vectors.shape[0]
        n_clusters = min(n_clusters, n_samples)
        
        idx = np.random.choice(n_samples, n_clusters, replace=False)
        centroids = vectors[idx].copy()
        
        labels = np.zeros(n_samples, dtype=int)
        
        for _ in range(max_iter):
            distances = np.zeros((n_samples, n_clusters))
            for k in range(n_clusters):
                distances[:, k] = np.linalg.norm(vectors - centroids[k], axis=1)
            
            new_labels = np.argmin(distances, axis=1)
            
            if np.all(new_labels == labels):
                break
            
            labels = new_labels
            
            for k in range(n_clusters):
                mask = labels == k
                if np.sum(mask) > 0:
                    centroids[k] = np.mean(vectors[mask], axis=0)
        
        return labels
    
    def _hdbscan_cluster(self, vectors: np.ndarray) -> np.ndarray:
        """Cluster using HDBSCAN."""
        try:
            import hdbscan
            min_cluster_size = max(2, vectors.shape[0] // 10)
            clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size)
            labels = clusterer.fit_predict(vectors)
            return labels
        except ImportError:
            return self._kmeans_cluster(vectors, 5)
    
    def _agglomerative_cluster(self, vectors: np.ndarray, n_clusters: int) -> np.ndarray:
        """Cluster using Agglomerative Clustering."""
        try:
            from sklearn.cluster import AgglomerativeClustering
            n_clusters = min(n_clusters, vectors.shape[0])
            clustering = AgglomerativeClustering(n_clusters=n_clusters)
            labels = clustering.fit_predict(vectors)
            return labels
        except ImportError:
            return self._kmeans_cluster(vectors, n_clusters)
    
    def cluster_and_reduce(self,
                          vectors: List[List[float]],
                          cluster_method: str = 'kmeans',
                          reduce_method: str = 'pca',
                          n_clusters: int = 5,
                          n_components: int = 2) -> Dict[str, Any]:
        """
        Perform clustering and dimensionality reduction.
        
        Returns:
            Dictionary with 'labels', 'reduced', 'centroids'
        """
        if not vectors:
            return {'labels': [], 'reduced': [], 'centroids': []}
        
        labels = self.cluster(vectors, cluster_method, n_clusters)
        reduced = self.reduce_dimensions(vectors, reduce_method, n_components)
        
        arr = np.array(vectors)
        labels_arr = np.array(labels)
        unique_labels = np.unique(labels_arr)
        
        centroids = []
        for label in unique_labels:
            mask = labels_arr == label
            if np.sum(mask) > 0:
                centroid = np.mean(arr[mask], axis=0)
                centroids.append(centroid.tolist())
        
        reduced_arr = np.array(reduced)
        centroid_positions = []
        for label in unique_labels:
            mask = labels_arr == label
            if np.sum(mask) > 0:
                pos = np.mean(reduced_arr[mask], axis=0)
                centroid_positions.append(pos.tolist())
        
        return {
            'labels': labels,
            'reduced': reduced,
            'centroids': centroids,
            'centroid_positions': centroid_positions,
            'n_clusters': len(unique_labels)
        }
    
    def get_cluster_stats(self, 
                         vectors: List[List[float]], 
                         labels: List[int]) -> Dict[int, Dict[str, Any]]:
        """Get statistics for each cluster."""
        if not vectors or not labels:
            return {}
        
        arr = np.array(vectors)
        labels_arr = np.array(labels)
        
        stats = {}
        for label in np.unique(labels_arr):
            mask = labels_arr == label
            cluster_vectors = arr[mask]
            
            stats[int(label)] = {
                'size': int(np.sum(mask)),
                'mean': np.mean(cluster_vectors, axis=0).tolist(),
                'std': np.std(cluster_vectors, axis=0).tolist(),
                'centroid': np.mean(cluster_vectors, axis=0).tolist()
            }
        
        return stats
    
    def find_optimal_clusters(self, 
                             vectors: List[List[float]], 
                             max_clusters: int = 10) -> int:
        """Find optimal number of clusters using elbow method."""
        if not vectors or len(vectors) < 3:
            return min(2, len(vectors))
        
        arr = np.array(vectors)
        max_clusters = min(max_clusters, len(vectors) - 1)
        
        inertias = []
        for k in range(2, max_clusters + 1):
            labels = self._simple_kmeans(arr, k)
            
            inertia = 0
            for label in np.unique(labels):
                mask = labels == label
                if np.sum(mask) > 0:
                    centroid = np.mean(arr[mask], axis=0)
                    inertia += np.sum(np.linalg.norm(arr[mask] - centroid, axis=1) ** 2)
            inertias.append(inertia)
        
        if len(inertias) < 2:
            return 2
        
        diffs = np.diff(inertias)
        diffs2 = np.diff(diffs)
        
        if len(diffs2) > 0:
            elbow = np.argmax(diffs2) + 2
        else:
            elbow = 2
        
        return min(elbow, max_clusters)
    
    def assign_archetype_labels(self, 
                               cluster_stats: Dict[int, Dict[str, Any]]) -> Dict[int, str]:
        """Assign human-readable archetype labels to clusters."""
        archetypes = [
            'The Analyst',
            'The Optimist', 
            'The Minimalist',
            'The Storyteller',
            'The Rapid Responder',
            'The Thoughtful',
            'The Expressive',
            'The Reserved',
            'The Connector',
            'The Observer'
        ]
        
        labels = {}
        for i, cluster_id in enumerate(sorted(cluster_stats.keys())):
            labels[cluster_id] = archetypes[i % len(archetypes)]
        
        return labels
