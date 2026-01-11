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
from pathlib import Path

# Load environment variables from .env file in backend directory
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
    logging.info(f"Loaded environment variables from {env_path}")
except ImportError:
    logging.warning("python-dotenv not installed, environment variables must be set manually")
except Exception as e:
    logging.warning(f"Could not load .env file: {e}")

from services.feature_extractor import FeatureExtractor
from services.synthetic_generator import SyntheticGenerator
from services.clustering_service import ClusteringService
from services.visualization_service import VisualizationService
from services.vector_store_chroma import ChromaVectorStore
from services.cache_service import CacheService
from services.user_feature_extractor import UserFeatureExtractor
from services.compatibility_service import CompatibilityService
from services.storage_service import StorageService
from services.personality_service import PersonalityService
from services.ecosystem_service import EcosystemService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

feature_extractor = None
synthetic_generator = None
clustering_service = None
visualization_service = None
vector_store = None
cache_service = None
user_feature_extractor = None
compatibility_service = None
storage_service = None
personality_service = None
ecosystem_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global feature_extractor, synthetic_generator, clustering_service
    global visualization_service, vector_store, cache_service
    global user_feature_extractor, compatibility_service, storage_service
    global personality_service, ecosystem_service
    
    logger.info("Initializing services...")
    feature_extractor = FeatureExtractor()
    synthetic_generator = SyntheticGenerator()
    clustering_service = ClusteringService()
    visualization_service = VisualizationService()
    vector_store = ChromaVectorStore(persist_directory="./data/chroma")
    cache_service = CacheService()
    user_feature_extractor = UserFeatureExtractor()
    compatibility_service = CompatibilityService()
    storage_service = StorageService(storage_dir="./data/analyses")
    personality_service = PersonalityService()
    ecosystem_service = EcosystemService(storage_dir="./data/ecosystem")
    
    logger.info(f"Services initialized. Feature count: {feature_extractor.get_feature_count()}")
    logger.info(f"User feature count: {user_feature_extractor.get_feature_count()}")
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


class UserFeaturesRequest(BaseModel):
    messages: List[Message]
    target_user: Optional[str] = None
    store: bool = False


class CompatibilityRequest(BaseModel):
    messages: List[Message]
    user1: Optional[str] = None
    user2: Optional[str] = None


class SaveAnalysisRequest(BaseModel):
    messages: List[Message]
    user_features: Optional[Dict[str, Any]] = None
    compatibility: Optional[Dict[str, Any]] = None
    conversation_features: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class SynthesizePersonalityRequest(BaseModel):
    user_name: str
    user_features: Dict[str, Any]
    sample_messages: Optional[List[str]] = None


class AddPersonaRequest(BaseModel):
    persona_id: str
    user_name: str
    personality: Dict[str, Any]
    vector: List[float]
    source_analysis_id: Optional[str] = None


class ChatWithPersonaRequest(BaseModel):
    persona_id: str
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = None


class EcosystemCompatibilityRequest(BaseModel):
    persona_id_1: str
    persona_id_2: str


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


@app.post("/api/users/features")
async def extract_user_features(request: UserFeaturesRequest):
    """
    Extract behavior features for individual users in a conversation.
    Analyzes how each user reacts to and interacts with the other person.
    """
    try:
        messages = [msg.model_dump() for msg in request.messages]
        
        if len(messages) == 0:
            raise HTTPException(status_code=400, detail="Messages list is empty")
        
        # Get all participants
        participants = user_feature_extractor.get_participants(messages)
        
        if request.target_user:
            if request.target_user not in participants:
                raise HTTPException(
                    status_code=400, 
                    detail=f"User '{request.target_user}' not found in conversation. Available: {participants}"
                )
            # Extract for specific user
            vector, labels = user_feature_extractor.extract_for_user(messages, request.target_user)
            categories = user_feature_extractor._group_by_category(labels, vector)
            summary = user_feature_extractor.get_user_summary(messages, request.target_user)
            
            user_msgs = [m for m in messages if m.get('sender') == request.target_user]
            
            response = {
                "success": True,
                "user": request.target_user,
                "vector": vector,
                "feature_labels": labels,
                "feature_count": len(vector),
                "categories": categories,
                "category_summary": summary,
                "message_count": len(user_msgs)
            }
        else:
            # Extract for all users
            all_users = user_feature_extractor.extract_all_users(messages)
            
            response = {
                "success": True,
                "participants": participants,
                "users": all_users,
                "total_messages": len(messages)
            }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting user features: {str(e)}")
        raise HTTPException(status_code=500, detail=f"User feature extraction failed: {str(e)}")


@app.post("/api/users/compatibility")
async def calculate_compatibility(request: CompatibilityRequest):
    """
    Calculate compatibility score between two users based on their conversation behavior.
    Uses Gemini LLM for intelligent analysis when available, falls back to algorithmic scoring.
    """
    try:
        messages = [msg.model_dump() for msg in request.messages]
        
        if len(messages) == 0:
            raise HTTPException(status_code=400, detail="Messages list is empty")
        
        participants = user_feature_extractor.get_participants(messages)
        
        if len(participants) < 2:
            raise HTTPException(
                status_code=400, 
                detail="Need at least 2 participants for compatibility analysis"
            )
        
        # Determine which users to compare
        user1 = request.user1 or participants[0]
        user2 = request.user2 or (participants[1] if len(participants) > 1 else participants[0])
        
        if user1 not in participants:
            raise HTTPException(status_code=400, detail=f"User '{user1}' not found")
        if user2 not in participants:
            raise HTTPException(status_code=400, detail=f"User '{user2}' not found")
        
        # Extract features for both users
        vec1, labels1 = user_feature_extractor.extract_for_user(messages, user1)
        vec2, labels2 = user_feature_extractor.extract_for_user(messages, user2)
        
        user1_features = {
            'vector': vec1,
            'labels': labels1,
            'categories': user_feature_extractor._group_by_category(labels1, vec1)
        }
        
        user2_features = {
            'vector': vec2,
            'labels': labels2,
            'categories': user_feature_extractor._group_by_category(labels2, vec2)
        }
        
        # Calculate compatibility
        compatibility = await compatibility_service.calculate_compatibility(
            user1_features, user2_features, user1, user2
        )
        
        return {
            "success": True,
            "compatibility": compatibility,
            "user1_summary": user_feature_extractor.get_user_summary(messages, user1),
            "user2_summary": user_feature_extractor.get_user_summary(messages, user2)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating compatibility: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Compatibility calculation failed: {str(e)}")


@app.get("/api/users/labels")
async def get_user_feature_labels():
    """Get all user feature labels including reaction features."""
    try:
        labels = user_feature_extractor.get_feature_names()
        
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
        logger.error(f"Error getting user labels: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get user labels: {str(e)}")


@app.post("/api/analyses/save")
async def save_analysis(request: SaveAnalysisRequest):
    """
    Save a complete analysis to local storage.
    Each upload creates a new analysis file with a unique ID.
    """
    try:
        messages = [msg.model_dump() for msg in request.messages]
        
        if len(messages) == 0:
            raise HTTPException(status_code=400, detail="Messages list is empty")
        
        # If user_features not provided, extract them
        user_features = request.user_features
        if not user_features:
            all_users = user_feature_extractor.extract_all_users(messages)
            user_features = all_users.get("users", {})
        
        # If conversation_features not provided, extract them
        conversation_features = request.conversation_features
        if not conversation_features:
            vector, labels = feature_extractor.extract(messages)
            categories = feature_extractor.extract_by_category(messages)
            conversation_features = {
                "vector": vector,
                "labels": labels,
                "categories": {k: dict(v) for k, v in categories.items()}
            }
        
        # Save to storage
        result = storage_service.save_analysis(
            messages=messages,
            user_features=user_features,
            compatibility=request.compatibility,
            conversation_features=conversation_features,
            metadata=request.metadata
        )
        
        return {
            "success": True,
            **result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save analysis: {str(e)}")


@app.get("/api/analyses")
async def list_analyses(limit: int = 50, offset: int = 0):
    """List all saved analyses with summary info."""
    try:
        analyses = storage_service.list_analyses(limit=limit, offset=offset)
        total = storage_service.count_analyses()
        
        return {
            "success": True,
            "analyses": analyses,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error listing analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list analyses: {str(e)}")


@app.get("/api/analyses/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Retrieve a specific analysis by ID."""
    try:
        analysis = storage_service.get_analysis(analysis_id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Analysis '{analysis_id}' not found")
        
        return {
            "success": True,
            "analysis": analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get analysis: {str(e)}")


@app.delete("/api/analyses/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete a specific analysis."""
    try:
        deleted = storage_service.delete_analysis(analysis_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Analysis '{analysis_id}' not found")
        
        return {
            "success": True,
            "message": f"Analysis '{analysis_id}' deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete analysis: {str(e)}")


@app.get("/api/analyses/user/{username}")
async def get_user_history(username: str):
    """Get all analyses involving a specific user."""
    try:
        analyses = storage_service.get_user_history(username)
        
        return {
            "success": True,
            "username": username,
            "analyses": analyses,
            "count": len(analyses)
        }
        
    except Exception as e:
        logger.error(f"Error getting user history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get user history: {str(e)}")


# ============== Personality Synthesis Endpoints ==============

@app.post("/api/personality/synthesize")
async def synthesize_personality(request: SynthesizePersonalityRequest):
    """
    Synthesize an AI personality from user features.
    Generates a custom LLM prompt that shapes voice, tone, style, pacing, and quirks.
    """
    try:
        personality = personality_service.synthesize_personality(
            user_name=request.user_name,
            user_features=request.user_features,
            sample_messages=request.sample_messages
        )
        
        return {
            "success": True,
            "personality": personality
        }
        
    except Exception as e:
        logger.error(f"Error synthesizing personality: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Personality synthesis failed: {str(e)}")


@app.post("/api/personality/chat")
async def chat_with_persona(request: ChatWithPersonaRequest):
    """
    Chat with an AI persona. Users can preview interpersonal dynamics
    by talking to another person's AI persona before meeting them.
    """
    try:
        # Get persona from ecosystem
        persona = ecosystem_service.get_persona(request.persona_id)
        
        if not persona:
            raise HTTPException(status_code=404, detail=f"Persona '{request.persona_id}' not found")
        
        personality = persona.get('personality', {})
        
        # Generate response
        response = await personality_service.chat_as_persona(
            personality=personality,
            user_message=request.message,
            conversation_history=request.conversation_history
        )
        
        # Increment interaction count
        ecosystem_service.increment_interaction(request.persona_id)
        
        return {
            "success": True,
            "response": response,
            "persona_name": persona.get('user_name'),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in persona chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


# ============== Ecosystem Endpoints ==============

@app.post("/api/ecosystem/personas")
async def add_persona_to_ecosystem(request: AddPersonaRequest):
    """Add a persona to the personality ecosystem."""
    try:
        persona = ecosystem_service.add_persona(
            persona_id=request.persona_id,
            user_name=request.user_name,
            personality=request.personality,
            vector=request.vector,
            source_analysis_id=request.source_analysis_id
        )
        
        return {
            "success": True,
            "persona": {
                "persona_id": persona['persona_id'],
                "user_name": persona['user_name'],
                "added_at": persona['added_at'],
            }
        }
        
    except Exception as e:
        logger.error(f"Error adding persona: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add persona: {str(e)}")


@app.get("/api/ecosystem/personas")
async def list_ecosystem_personas():
    """List all personas in the ecosystem."""
    try:
        personas = ecosystem_service.list_personas()
        stats = ecosystem_service.get_ecosystem_stats()
        
        return {
            "success": True,
            "personas": personas,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error listing personas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list personas: {str(e)}")


@app.get("/api/ecosystem/personas/{persona_id}")
async def get_ecosystem_persona(persona_id: str):
    """Get a specific persona from the ecosystem."""
    try:
        persona = ecosystem_service.get_persona(persona_id)
        
        if not persona:
            raise HTTPException(status_code=404, detail=f"Persona '{persona_id}' not found")
        
        return {
            "success": True,
            "persona": persona
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting persona: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get persona: {str(e)}")


@app.delete("/api/ecosystem/personas/{persona_id}")
async def remove_ecosystem_persona(persona_id: str):
    """Remove a persona from the ecosystem."""
    try:
        removed = ecosystem_service.remove_persona(persona_id)
        
        if not removed:
            raise HTTPException(status_code=404, detail=f"Persona '{persona_id}' not found")
        
        return {
            "success": True,
            "message": f"Persona '{persona_id}' removed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing persona: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to remove persona: {str(e)}")


@app.post("/api/ecosystem/compatibility")
async def compute_ecosystem_compatibility(request: EcosystemCompatibilityRequest):
    """
    Compute detailed compatibility between two personas in the ecosystem.
    Scores across: emotional alignment, conversation rhythm, topic affinity,
    social energy match, linguistic similarity, and trait complementarity.
    """
    try:
        compatibility = ecosystem_service.compute_compatibility(
            request.persona_id_1,
            request.persona_id_2
        )
        
        return {
            "success": True,
            "compatibility": compatibility
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error computing compatibility: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Compatibility computation failed: {str(e)}")


@app.get("/api/ecosystem/matches/{persona_id}")
async def find_best_matches(persona_id: str, top_k: int = 5):
    """Find the best matching personas for a given persona."""
    try:
        matches = ecosystem_service.find_best_matches(persona_id, top_k)
        
        return {
            "success": True,
            "persona_id": persona_id,
            "matches": matches
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error finding matches: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to find matches: {str(e)}")


@app.get("/api/ecosystem/stats")
async def get_ecosystem_stats():
    """Get statistics about the personality ecosystem."""
    try:
        stats = ecosystem_service.get_ecosystem_stats()
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting ecosystem stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@app.post("/api/ecosystem/from-analysis/{analysis_id}")
async def create_personas_from_analysis(analysis_id: str):
    """
    Create personas from a saved analysis and add them to the ecosystem.
    This allows users to quickly populate the ecosystem from past analyses.
    """
    try:
        # Get the analysis
        analysis = storage_service.get_analysis(analysis_id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Analysis '{analysis_id}' not found")
        
        created_personas = []
        
        # Create persona for each participant
        for user_name, user_data in analysis.get('user_features', {}).items():
            # Extract sample messages for this user
            sample_messages = [
                msg.get('content', '')
                for msg in analysis.get('messages', [])
                if msg.get('sender') == user_name
            ][:10]
            
            # Synthesize personality
            personality = personality_service.synthesize_personality(
                user_name=user_name,
                user_features={'categories': user_data.get('categories', {})},
                sample_messages=sample_messages
            )
            
            # Generate persona ID
            persona_id = f"{user_name.lower().replace(' ', '_')}_{analysis_id[:8]}"
            
            # Get vector
            vector = user_data.get('vector', [0.5] * 100)
            
            # Add to ecosystem
            persona = ecosystem_service.add_persona(
                persona_id=persona_id,
                user_name=user_name,
                personality=personality,
                vector=vector,
                source_analysis_id=analysis_id
            )
            
            created_personas.append({
                'persona_id': persona['persona_id'],
                'user_name': persona['user_name'],
            })
        
        return {
            "success": True,
            "created_personas": created_personas,
            "count": len(created_personas)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating personas from analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create personas: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        reload_excludes=[
            "*/__pycache__/*",
            "*/.venv/*",
            "*/data/*",
            "*/.*",
            "*.pyc",
            "*.pyo",
            "*.db",
            "*.sqlite3",
            "*/node_modules/*",
            "*/.git/*",
        ]
    )
