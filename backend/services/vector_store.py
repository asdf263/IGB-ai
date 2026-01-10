"""
Vector Store Module
In-memory storage for behavior vectors with persistence support
"""
import numpy as np
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import hashlib


class VectorStore:
    """In-memory vector storage with persistence capabilities."""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.vectors: Dict[str, Dict[str, Any]] = {}
        self.storage_path = storage_path or 'vector_store.json'
        self._load_from_disk()
    
    def add(self, 
            vector: List[float], 
            metadata: Optional[Dict[str, Any]] = None,
            vector_id: Optional[str] = None) -> str:
        """
        Add a vector to the store.
        
        Args:
            vector: Feature vector
            metadata: Optional metadata
            vector_id: Optional custom ID
            
        Returns:
            Vector ID
        """
        if vector_id is None:
            vector_id = self._generate_id(vector)
        
        self.vectors[vector_id] = {
            'vector': vector,
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self._save_to_disk()
        return vector_id
    
    def get(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """Get a vector by ID."""
        return self.vectors.get(vector_id)
    
    def get_vector(self, vector_id: str) -> Optional[List[float]]:
        """Get just the vector values by ID."""
        entry = self.vectors.get(vector_id)
        return entry['vector'] if entry else None
    
    def update(self, 
               vector_id: str, 
               vector: Optional[List[float]] = None,
               metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update a vector entry."""
        if vector_id not in self.vectors:
            return False
        
        if vector is not None:
            self.vectors[vector_id]['vector'] = vector
        
        if metadata is not None:
            self.vectors[vector_id]['metadata'].update(metadata)
        
        self.vectors[vector_id]['updated_at'] = datetime.now().isoformat()
        self._save_to_disk()
        return True
    
    def delete(self, vector_id: str) -> bool:
        """Delete a vector by ID."""
        if vector_id in self.vectors:
            del self.vectors[vector_id]
            self._save_to_disk()
            return True
        return False
    
    def list_all(self) -> List[Dict[str, Any]]:
        """List all stored vectors with metadata."""
        result = []
        for vector_id, data in self.vectors.items():
            result.append({
                'id': vector_id,
                'vector': data['vector'],
                'metadata': data['metadata'],
                'created_at': data['created_at'],
                'updated_at': data.get('updated_at', data['created_at'])
            })
        return result
    
    def list_ids(self) -> List[str]:
        """List all vector IDs."""
        return list(self.vectors.keys())
    
    def get_all_vectors(self) -> List[List[float]]:
        """Get all vectors as a list."""
        return [data['vector'] for data in self.vectors.values()]
    
    def search_similar(self, 
                      query_vector: List[float], 
                      top_k: int = 5,
                      threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query vector
            top_k: Number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of similar vectors with scores
        """
        if not self.vectors:
            return []
        
        query_arr = np.array(query_vector)
        results = []
        
        for vector_id, data in self.vectors.items():
            stored_arr = np.array(data['vector'])
            similarity = self._cosine_similarity(query_arr, stored_arr)
            
            if similarity >= threshold:
                results.append({
                    'id': vector_id,
                    'similarity': float(similarity),
                    'vector': data['vector'],
                    'metadata': data['metadata']
                })
        
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
    
    def _generate_id(self, vector: List[float]) -> str:
        """Generate unique ID for vector."""
        timestamp = datetime.now().isoformat()
        vector_hash = hashlib.md5(str(vector).encode()).hexdigest()[:8]
        return f"vec_{vector_hash}_{timestamp.replace(':', '-').replace('.', '-')}"
    
    def _save_to_disk(self):
        """Save vectors to disk."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.vectors, f, indent=2)
        except Exception as e:
            print(f"Error saving vector store: {e}")
    
    def _load_from_disk(self):
        """Load vectors from disk."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    self.vectors = json.load(f)
            except Exception as e:
                print(f"Error loading vector store: {e}")
                self.vectors = {}
    
    def clear(self):
        """Clear all vectors."""
        self.vectors = {}
        self._save_to_disk()
    
    def count(self) -> int:
        """Get number of stored vectors."""
        return len(self.vectors)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        if not self.vectors:
            return {
                'count': 0,
                'avg_dimension': 0,
                'total_size_bytes': 0
            }
        
        vectors = self.get_all_vectors()
        dimensions = [len(v) for v in vectors]
        
        return {
            'count': len(self.vectors),
            'avg_dimension': float(np.mean(dimensions)),
            'min_dimension': min(dimensions),
            'max_dimension': max(dimensions),
            'total_size_bytes': len(json.dumps(self.vectors).encode())
        }
    
    def export(self, format: str = 'json') -> str:
        """Export vectors to string."""
        if format == 'json':
            return json.dumps(self.list_all(), indent=2)
        elif format == 'csv':
            lines = []
            for entry in self.list_all():
                vector_str = ','.join(map(str, entry['vector']))
                lines.append(f"{entry['id']},{vector_str}")
            return '\n'.join(lines)
        return json.dumps(self.list_all())
    
    def import_vectors(self, data: List[Dict[str, Any]]):
        """Import vectors from list."""
        for entry in data:
            vector_id = entry.get('id')
            vector = entry.get('vector', [])
            metadata = entry.get('metadata', {})
            self.add(vector, metadata, vector_id)
