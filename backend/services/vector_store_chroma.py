"""
ChromaDB Vector Store Module
Persistent vector storage using ChromaDB
"""
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import json


class ChromaVectorStore:
    """ChromaDB-based vector storage with persistence."""
    
    def __init__(self, persist_directory: str = "./data/chroma", collection_name: str = "behavior_vectors"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self._init_chroma()
    
    def _init_chroma(self):
        """Initialize ChromaDB client and collection."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        except ImportError:
            print("ChromaDB not installed, using in-memory fallback")
            self._use_fallback()
    
    def _use_fallback(self):
        """Use in-memory storage as fallback."""
        self.vectors = {}
        self.client = None
        self.collection = None
    
    def add(self, 
            vector: List[float], 
            metadata: Optional[Dict[str, Any]] = None,
            vector_id: Optional[str] = None) -> str:
        """Add a vector to the store."""
        if vector_id is None:
            vector_id = self._generate_id(vector)
        
        metadata = metadata or {}
        metadata["created_at"] = datetime.now().isoformat()
        
        if self.collection is not None:
            serializable_metadata = {}
            for k, v in metadata.items():
                if isinstance(v, (str, int, float, bool)):
                    serializable_metadata[k] = v
                else:
                    serializable_metadata[k] = json.dumps(v)
            
            self.collection.add(
                ids=[vector_id],
                embeddings=[vector],
                metadatas=[serializable_metadata]
            )
        else:
            self.vectors[vector_id] = {
                "vector": vector,
                "metadata": metadata,
                "created_at": metadata["created_at"]
            }
        
        return vector_id
    
    def get(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """Get a vector by ID."""
        if self.collection is not None:
            try:
                result = self.collection.get(
                    ids=[vector_id],
                    include=["embeddings", "metadatas"]
                )
                if result["ids"]:
                    return {
                        "vector": result["embeddings"][0],
                        "metadata": result["metadatas"][0] if result["metadatas"] else {},
                        "created_at": result["metadatas"][0].get("created_at") if result["metadatas"] else None
                    }
            except Exception:
                pass
            return None
        else:
            return self.vectors.get(vector_id)
    
    def get_vector(self, vector_id: str) -> Optional[List[float]]:
        """Get just the vector values by ID."""
        entry = self.get(vector_id)
        return entry["vector"] if entry else None
    
    def delete(self, vector_id: str) -> bool:
        """Delete a vector by ID."""
        if self.collection is not None:
            try:
                self.collection.delete(ids=[vector_id])
                return True
            except Exception:
                return False
        else:
            if vector_id in self.vectors:
                del self.vectors[vector_id]
                return True
            return False
    
    def list_all(self) -> List[Dict[str, Any]]:
        """List all stored vectors with metadata."""
        if self.collection is not None:
            try:
                result = self.collection.get(include=["embeddings", "metadatas"])
                entries = []
                for i, vid in enumerate(result["ids"]):
                    entries.append({
                        "id": vid,
                        "vector": result["embeddings"][i] if result["embeddings"] else [],
                        "metadata": result["metadatas"][i] if result["metadatas"] else {},
                        "created_at": result["metadatas"][i].get("created_at") if result["metadatas"] else None
                    })
                return entries
            except Exception:
                return []
        else:
            return [
                {"id": vid, **data}
                for vid, data in self.vectors.items()
            ]
    
    def get_all_vectors(self) -> List[List[float]]:
        """Get all vectors as a list."""
        if self.collection is not None:
            try:
                result = self.collection.get(include=["embeddings"])
                return result["embeddings"] if result["embeddings"] else []
            except Exception:
                return []
        else:
            return [data["vector"] for data in self.vectors.values()]
    
    def search_similar(self, 
                      query_vector: List[float], 
                      top_k: int = 5,
                      threshold: float = 0.0) -> List[Dict[str, Any]]:
        """Search for similar vectors using ChromaDB's native search."""
        if self.collection is not None:
            try:
                results = self.collection.query(
                    query_embeddings=[query_vector],
                    n_results=top_k,
                    include=["embeddings", "metadatas", "distances"]
                )
                
                similar = []
                for i, vid in enumerate(results["ids"][0]):
                    similarity = 1 - results["distances"][0][i]
                    if similarity >= threshold:
                        similar.append({
                            "id": vid,
                            "similarity": float(similarity),
                            "vector": results["embeddings"][0][i] if results["embeddings"] else [],
                            "metadata": results["metadatas"][0][i] if results["metadatas"] else {}
                        })
                return similar
            except Exception as e:
                print(f"Search error: {e}")
                return []
        else:
            query_arr = np.array(query_vector)
            results = []
            
            for vector_id, data in self.vectors.items():
                stored_arr = np.array(data["vector"])
                similarity = self._cosine_similarity(query_arr, stored_arr)
                
                if similarity >= threshold:
                    results.append({
                        "id": vector_id,
                        "similarity": float(similarity),
                        "vector": data["vector"],
                        "metadata": data["metadata"]
                    })
            
            results.sort(key=lambda x: x["similarity"], reverse=True)
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
    
    def count(self) -> int:
        """Get number of stored vectors."""
        if self.collection is not None:
            return self.collection.count()
        else:
            return len(self.vectors)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        vectors = self.get_all_vectors()
        if not vectors:
            return {
                "count": 0,
                "avg_dimension": 0,
                "storage_type": "chromadb" if self.collection else "memory"
            }
        
        dimensions = [len(v) for v in vectors]
        
        return {
            "count": len(vectors),
            "avg_dimension": float(np.mean(dimensions)),
            "min_dimension": min(dimensions),
            "max_dimension": max(dimensions),
            "storage_type": "chromadb" if self.collection else "memory"
        }
    
    def clear(self):
        """Clear all vectors."""
        if self.collection is not None:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        else:
            self.vectors = {}
