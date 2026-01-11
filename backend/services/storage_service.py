"""
Local Storage Service for User Analysis Data
Saves and retrieves user analysis data to/from local JSON files.
Each upload creates a new analysis file with a unique ID.
"""
import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class StorageService:
    """Handles local storage of user analysis data."""
    
    def __init__(self, storage_dir: str = "./data/analyses"):
        self.storage_dir = storage_dir
        self._ensure_storage_dir()
    
    def _ensure_storage_dir(self):
        """Create storage directory if it doesn't exist."""
        os.makedirs(self.storage_dir, exist_ok=True)
        logger.info(f"Storage directory: {os.path.abspath(self.storage_dir)}")
    
    def _generate_analysis_id(self) -> str:
        """Generate a unique analysis ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_uuid = str(uuid.uuid4())[:8]
        return f"analysis_{timestamp}_{short_uuid}"
    
    def save_analysis(
        self,
        messages: List[Dict[str, Any]],
        user_features: Dict[str, Any],
        compatibility: Optional[Dict[str, Any]] = None,
        conversation_features: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Save a complete analysis to a local JSON file.
        
        Args:
            messages: Original chat messages
            user_features: Extracted user features for each participant
            compatibility: Compatibility analysis results (optional)
            conversation_features: Overall conversation features (optional)
            metadata: Additional metadata (optional)
        
        Returns:
            Dict with analysis_id and file_path
        """
        analysis_id = self._generate_analysis_id()
        
        # Extract participant names
        participants = list(set(msg.get('sender', 'Unknown') for msg in messages))
        
        # Build analysis data structure
        analysis_data = {
            "analysis_id": analysis_id,
            "created_at": datetime.now().isoformat(),
            "participants": participants,
            "message_count": len(messages),
            "messages": messages,
            "user_features": user_features,
            "compatibility": compatibility,
            "conversation_features": conversation_features,
            "metadata": metadata or {}
        }
        
        # Save to file
        file_path = os.path.join(self.storage_dir, f"{analysis_id}.json")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Saved analysis: {analysis_id}")
            
            return {
                "analysis_id": analysis_id,
                "file_path": file_path,
                "created_at": analysis_data["created_at"],
                "participants": participants,
                "message_count": len(messages)
            }
        except Exception as e:
            logger.error(f"Failed to save analysis: {e}")
            raise
    
    def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific analysis by ID.
        
        Args:
            analysis_id: The unique analysis identifier
        
        Returns:
            Analysis data or None if not found
        """
        file_path = os.path.join(self.storage_dir, f"{analysis_id}.json")
        
        if not os.path.exists(file_path):
            logger.warning(f"Analysis not found: {analysis_id}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load analysis {analysis_id}: {e}")
            return None
    
    def list_analyses(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all saved analyses with summary info.
        
        Args:
            limit: Maximum number of analyses to return
            offset: Number of analyses to skip
        
        Returns:
            List of analysis summaries
        """
        analyses = []
        
        try:
            files = [f for f in os.listdir(self.storage_dir) if f.endswith('.json')]
            # Sort by modification time (newest first)
            files.sort(key=lambda x: os.path.getmtime(os.path.join(self.storage_dir, x)), reverse=True)
            
            for filename in files[offset:offset + limit]:
                file_path = os.path.join(self.storage_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    analyses.append({
                        "analysis_id": data.get("analysis_id", filename.replace('.json', '')),
                        "created_at": data.get("created_at"),
                        "participants": data.get("participants", []),
                        "message_count": data.get("message_count", 0),
                        "has_compatibility": data.get("compatibility") is not None
                    })
                except Exception as e:
                    logger.warning(f"Failed to read {filename}: {e}")
                    continue
            
            return analyses
        except Exception as e:
            logger.error(f"Failed to list analyses: {e}")
            return []
    
    def delete_analysis(self, analysis_id: str) -> bool:
        """
        Delete a specific analysis.
        
        Args:
            analysis_id: The unique analysis identifier
        
        Returns:
            True if deleted, False if not found
        """
        file_path = os.path.join(self.storage_dir, f"{analysis_id}.json")
        
        if not os.path.exists(file_path):
            return False
        
        try:
            os.remove(file_path)
            logger.info(f"Deleted analysis: {analysis_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete analysis {analysis_id}: {e}")
            return False
    
    def get_user_history(self, username: str) -> List[Dict[str, Any]]:
        """
        Get all analyses involving a specific user.
        
        Args:
            username: The username to search for
        
        Returns:
            List of analyses involving this user
        """
        user_analyses = []
        
        try:
            files = [f for f in os.listdir(self.storage_dir) if f.endswith('.json')]
            
            for filename in files:
                file_path = os.path.join(self.storage_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if username in data.get("participants", []):
                        user_analyses.append({
                            "analysis_id": data.get("analysis_id"),
                            "created_at": data.get("created_at"),
                            "participants": data.get("participants", []),
                            "message_count": data.get("message_count", 0),
                            "user_features": data.get("user_features", {}).get(username)
                        })
                except Exception:
                    continue
            
            # Sort by creation time (newest first)
            user_analyses.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return user_analyses
        except Exception as e:
            logger.error(f"Failed to get user history for {username}: {e}")
            return []
    
    def count_analyses(self) -> int:
        """Get total number of saved analyses."""
        try:
            return len([f for f in os.listdir(self.storage_dir) if f.endswith('.json')])
        except Exception:
            return 0
