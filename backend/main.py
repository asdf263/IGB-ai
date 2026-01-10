"""
IGB AI - Behavior Vector Extraction API
FastAPI backend with feature extraction, synthetic generation, clustering, and visualization
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from services.feature_extractor import FeatureExtractor
from services.synthetic_generator import SyntheticGenerator
from services.clustering_service import ClusteringService
from services.visualization_service import VisualizationService
from services.vector_store_chroma import ChromaVectorStore
from services.cache_service import CacheService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

feature_extractor = None
synthetic_generator = None
clustering_service = None
visualization_service = None
vector_store = None
cache_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global feature_extractor, synthetic_generator, clustering_service
    global visualization_service, vector_store, cache_service
    
    logger.info("Initializing services...")
    feature_extractor = FeatureExtractor()
    synthetic_generator = SyntheticGenerator()
    clustering_service = ClusteringService()
    visualization_service = VisualizationService()
    vector_store = ChromaVectorStore(persist_directory="./data/chroma")
    cache_service = CacheService()
    
    logger.info(f"Services initialized. Feature count: {feature_extractor.get_feature_count()}")
    yield
    
    logger.info("Shutting down services...")


app = FastAPI(
    title="IGB AI - Behavior Vector API",
    description="Extract behavior vectors from chat logs",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    sender: str
    text: str
    timestamp: int | float | str


class ExtractRequest(BaseModel):
    messages: List[Message]
    store: bool = False


class SyntheticRequest(BaseModel):
    vectors: Optional[List[List[float]]] = None
    n_synthetic: int = 10
    method: str = "smote"
    store: bool = False


class ClusterRequest(BaseModel):
    vectors: Optional[List[List[float]]] = None
    cluster_method: str = "kmeans"
    reduce_method: str = "pca"
    n_clusters: int = 5


class SearchRequest(BaseModel):
    query_vector: List[float]
    top_k: int = 5
    threshold: float = 0.0


class HeatmapRequest(BaseModel):
    vector_id: Optional[str] = None
    features: Optional[Dict[str, float]] = None


class RadarRequest(BaseModel):
    messages: Optional[List[Message]] = None
    category_scores: Optional[Dict[str, float]] = None


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "IGB-AI Vector API",
        "version": "2.0.0",
        "feature_count": feature_extractor.get_feature_count() if feature_extractor else 0,
        "stored_vectors": vector_store.count() if vector_store else 0
    }


@app.post("/api/features/extract")
async def extract_features(request: ExtractRequest):
    """
    Extract behavior vector features from chat messages.
    """
    try:
        messages = [msg.model_dump() for msg in request.messages]
        
        if len(messages) == 0:
            raise HTTPException(status_code=400, detail="Messages list is empty")
        
        cache_key = cache_service.generate_key(messages) if cache_service else None
        if cache_key:
            cached = await cache_service.get(cache_key)
            if cached:
                return cached
        
        vector, labels = feature_extractor.extract(messages)
        categories = feature_extractor.extract_by_category(messages)
        
        vector_id = None
        if request.store:
            metadata = {
                "message_count": len(messages),
                "extracted_at": datetime.now().isoformat()
            }
            vector_id = vector_store.add(vector, metadata)
        
        response = {
            "success": True,
            "vector": vector,
            "feature_labels": labels,
            "feature_count": len(vector),
            "categories": {k: dict(v) for k, v in categories.items()},
            "category_summary": feature_extractor.get_category_summary(messages)
        }
        
        if vector_id:
            response["vector_id"] = vector_id
        
        if cache_key:
            await cache_service.set(cache_key, response, ttl=3600)
        
        return response
        
    except Exception as e:
        logger.error(f"Error extracting features: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Feature extraction failed: {str(e)}")


@app.post("/api/features/synthetic-generate")
async def generate_synthetic(request: SyntheticRequest):
    """
    Generate synthetic behavior vectors.
    """
    try:
        vectors = request.vectors
        
        if not vectors:
            stored = vector_store.get_all_vectors()
            if stored:
                vectors = stored
            else:
                raise HTTPException(status_code=400, detail="No vectors provided and none stored")
        
        synthetic_vectors = synthetic_generator.generate_synthetic_vectors(
            vectors, request.n_synthetic, request.method
        )
        
        validated_vectors = []
        for vec in synthetic_vectors:
            is_valid, clipped = synthetic_generator.validate_vector(vec)
            validated_vectors.append(clipped)
        
        stored_ids = []
        if request.store:
            for vec in validated_vectors:
                metadata = {
                    "synthetic": True,
                    "method": request.method,
                    "generated_at": datetime.now().isoformat()
                }
                vid = vector_store.add(vec, metadata)
                stored_ids.append(vid)
        
        response = {
            "success": True,
            "synthetic_vectors": validated_vectors,
            "count": len(validated_vectors),
            "method": request.method
        }
        
        if stored_ids:
            response["stored_ids"] = stored_ids
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating synthetic vectors: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Synthetic generation failed: {str(e)}")


@app.get("/api/vectors/list")
async def list_vectors():
    """List all stored vectors."""
    try:
        vectors = vector_store.list_all()
        stats = vector_store.get_stats()
        
        return {
            "success": True,
            "vectors": vectors,
            "count": len(vectors),
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error listing vectors: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list vectors: {str(e)}")


@app.get("/api/vectors/{vector_id}")
async def get_vector(vector_id: str):
    """Get a specific vector by ID."""
    try:
        vector_data = vector_store.get(vector_id)
        
        if not vector_data:
            raise HTTPException(status_code=404, detail="Vector not found")
        
        return {
            "success": True,
            "id": vector_id,
            "vector": vector_data["vector"],
            "metadata": vector_data.get("metadata", {}),
            "created_at": vector_data.get("created_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting vector: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get vector: {str(e)}")


@app.delete("/api/vectors/{vector_id}")
async def delete_vector(vector_id: str):
    """Delete a vector by ID."""
    try:
        success = vector_store.delete(vector_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Vector not found")
        
        return {
            "success": True,
            "message": f"Vector {vector_id} deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting vector: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete vector: {str(e)}")


@app.post("/api/vectors/cluster")
async def cluster_vectors(request: ClusterRequest):
    """Cluster stored vectors."""
    try:
        vectors = request.vectors
        
        if not vectors:
            vectors = vector_store.get_all_vectors()
        
        if not vectors:
            raise HTTPException(status_code=400, detail="No vectors to cluster")
        
        result = clustering_service.cluster_and_reduce(
            vectors,
            cluster_method=request.cluster_method,
            reduce_method=request.reduce_method,
            n_clusters=request.n_clusters
        )
        
        cluster_stats = clustering_service.get_cluster_stats(vectors, result["labels"])
        archetype_labels = clustering_service.assign_archetype_labels(cluster_stats)
        
        return {
            "success": True,
            "labels": result["labels"],
            "reduced": result["reduced"],
            "centroids": result["centroids"],
            "centroid_positions": result["centroid_positions"],
            "n_clusters": result["n_clusters"],
            "cluster_stats": {str(k): v for k, v in cluster_stats.items()},
            "archetype_labels": {str(k): v for k, v in archetype_labels.items()}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clustering vectors: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Clustering failed: {str(e)}")


@app.get("/api/visualization/graph")
async def get_visualization_graph():
    """Get graph structure for cluster visualization."""
    try:
        vectors = vector_store.get_all_vectors()
        
        if not vectors:
            return {
                "success": True,
                "nodes": [],
                "edges": [],
                "clusters": [],
                "bounds": {"min_x": 0, "max_x": 1, "min_y": 0, "max_y": 1}
            }
        
        result = clustering_service.cluster_and_reduce(vectors)
        
        all_entries = vector_store.list_all()
        metadata = [entry.get("metadata", {}) for entry in all_entries]
        
        graph = visualization_service.generate_cluster_graph(
            vectors,
            result["labels"],
            result["reduced"],
            metadata
        )
        
        return {
            "success": True,
            **graph
        }
        
    except Exception as e:
        logger.error(f"Error generating graph: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Graph generation failed: {str(e)}")


@app.post("/api/visualization/heatmap")
async def get_heatmap(request: HeatmapRequest):
    """Get heatmap data for feature visualization."""
    try:
        features = request.features
        
        if request.vector_id:
            vector_data = vector_store.get(request.vector_id)
            if not vector_data:
                raise HTTPException(status_code=404, detail="Vector not found")
            
            labels = feature_extractor.get_feature_names()
            features = dict(zip(labels, vector_data["vector"]))
        
        if not features:
            raise HTTPException(status_code=400, detail="No features provided")
        
        categories = ["temporal", "text", "linguistic", "semantic",
                     "sentiment", "behavioral", "graph", "composite"]
        
        heatmap = visualization_service.generate_feature_heatmap(features, categories)
        
        return {
            "success": True,
            **heatmap
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating heatmap: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Heatmap generation failed: {str(e)}")


@app.post("/api/visualization/radar")
async def get_radar(request: RadarRequest):
    """Get radar chart data for category scores."""
    try:
        category_scores = request.category_scores
        
        if request.messages:
            messages = [msg.model_dump() for msg in request.messages]
            category_scores = feature_extractor.get_category_summary(messages)
        
        if not category_scores:
            raise HTTPException(status_code=400, detail="No data provided")
        
        radar = visualization_service.generate_radar_chart_data(category_scores)
        
        return {
            "success": True,
            **radar
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating radar: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Radar generation failed: {str(e)}")


@app.post("/api/vectors/search")
async def search_vectors(request: SearchRequest):
    """Search for similar vectors."""
    try:
        results = vector_store.search_similar(
            request.query_vector, 
            request.top_k, 
            request.threshold
        )
        
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error searching vectors: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/api/features/labels")
async def get_feature_labels():
    """Get all feature labels."""
    try:
        labels = feature_extractor.get_feature_names()
        
        categories = {}
        for label in labels:
            category = label.split("_")[0]
            if category not in categories:
                categories[category] = []
            categories[category].append(label)
        
        return {
            "success": True,
            "labels": labels,
            "count": len(labels),
            "categories": categories
        }
        
    except Exception as e:
        logger.error(f"Error getting labels: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get labels: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
