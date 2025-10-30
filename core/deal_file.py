"""
Deal File Management

JSON memory per negotiation for persistent state management.
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path


class DealFile:
    """Deal file manager for persistent negotiation state."""
    
    def __init__(self, deal_id: str, initial_data: Dict[str, Any] = None):
        self.deal_id = deal_id
        self.logger = logging.getLogger(f"deal_file.{deal_id}")
        
        # File paths
        self.deal_files_dir = Path("deal_files")
        self.deal_files_dir.mkdir(exist_ok=True)
        self.file_path = self.deal_files_dir / f"{deal_id}.json"
        
        # Initialize deal data
        self.deal_data = {
            "deal_id": deal_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "status": "active",
            "participants": [],
            "messages": [],
            "negotiation_history": [],
            "agreements": [],
            "metadata": {}
        }
        
        # Merge with initial data if provided
        if initial_data:
            self.deal_data.update(initial_data)
        
        # Load existing file if it exists
        if self.file_path.exists():
            self._load_from_file()
        else:
            self._save_to_file()
        
        self.logger.info(f"DealFile initialized for deal {deal_id}")
    
    def add_participant(self, participant_id: str, role: str, metadata: Dict[str, Any] = None) -> bool:
        """Add participant to deal."""
        try:
            participant = {
                "id": participant_id,
                "role": role,
                "joined_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            # Check if participant already exists
            existing_participants = [p for p in self.deal_data["participants"] if p["id"] == participant_id]
            if existing_participants:
                self.logger.warning(f"Participant {participant_id} already exists")
                return False
            
            self.deal_data["participants"].append(participant)
            self._update_timestamp()
            self._save_to_file()
            
            self.logger.info(f"Added participant {participant_id} with role {role}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add participant: {e}")
            return False
    
    def remove_participant(self, participant_id: str) -> bool:
        """Remove participant from deal."""
        try:
            original_count = len(self.deal_data["participants"])
            self.deal_data["participants"] = [
                p for p in self.deal_data["participants"] if p["id"] != participant_id
            ]
            
            if len(self.deal_data["participants"]) < original_count:
                self._update_timestamp()
                self._save_to_file()
                self.logger.info(f"Removed participant {participant_id}")
                return True
            else:
                self.logger.warning(f"Participant {participant_id} not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to remove participant: {e}")
            return False
    
    def add_message(self, message: Dict[str, Any]) -> bool:
        """Add message to deal history."""
        try:
            message_with_timestamp = {
                **message,
                "timestamp": datetime.utcnow().isoformat(),
                "message_id": f"msg_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
            }
            
            self.deal_data["messages"].append(message_with_timestamp)
            self._update_timestamp()
            self._save_to_file()
            
            self.logger.debug(f"Added message to deal {self.deal_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add message: {e}")
            return False
    
    def add_negotiation_round(self, round_data: Dict[str, Any]) -> bool:
        """Add negotiation round to history."""
        try:
            round_with_timestamp = {
                **round_data,
                "timestamp": datetime.utcnow().isoformat(),
                "round_id": f"round_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
            }
            
            self.deal_data["negotiation_history"].append(round_with_timestamp)
            self._update_timestamp()
            self._save_to_file()
            
            self.logger.info(f"Added negotiation round to deal {self.deal_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add negotiation round: {e}")
            return False
    
    def add_agreement(self, agreement: Dict[str, Any]) -> bool:
        """Add agreement to deal."""
        try:
            agreement_with_timestamp = {
                **agreement,
                "timestamp": datetime.utcnow().isoformat(),
                "agreement_id": f"agreement_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
            }
            
            self.deal_data["agreements"].append(agreement_with_timestamp)
            self._update_timestamp()
            self._save_to_file()
            
            self.logger.info(f"Added agreement to deal {self.deal_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add agreement: {e}")
            return False
    
    def update_status(self, status: str, reason: str = None) -> bool:
        """Update deal status."""
        try:
            self.deal_data["status"] = status
            if reason:
                self.deal_data["status_reason"] = reason
            
            self._update_timestamp()
            self._save_to_file()
            
            self.logger.info(f"Updated deal status to {status}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update status: {e}")
            return False
    
    def update_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Update deal metadata."""
        try:
            self.deal_data["metadata"].update(metadata)
            self._update_timestamp()
            self._save_to_file()
            
            self.logger.debug(f"Updated metadata for deal {self.deal_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update metadata: {e}")
            return False
    
    def get_deal_data(self) -> Dict[str, Any]:
        """Get complete deal data."""
        return self.deal_data.copy()
    
    def get_participants(self) -> List[Dict[str, Any]]:
        """Get deal participants."""
        return self.deal_data["participants"].copy()
    
    def get_messages(self, message_type: str = None) -> List[Dict[str, Any]]:
        """Get deal messages, optionally filtered by type."""
        messages = self.deal_data["messages"]
        if message_type:
            return [msg for msg in messages if msg.get("type") == message_type]
        return messages.copy()
    
    def get_negotiation_history(self) -> List[Dict[str, Any]]:
        """Get negotiation history."""
        return self.deal_data["negotiation_history"].copy()
    
    def get_agreements(self) -> List[Dict[str, Any]]:
        """Get deal agreements."""
        return self.deal_data["agreements"].copy()
    
    def get_status(self) -> str:
        """Get current deal status."""
        return self.deal_data["status"]
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get deal metadata."""
        return self.deal_data["metadata"].copy()
    
    def save_final_state(self, final_state: Dict[str, Any]) -> bool:
        """Save final state and close deal file."""
        try:
            self.deal_data["final_state"] = final_state
            self.deal_data["status"] = "closed"
            self.deal_data["closed_at"] = datetime.utcnow().isoformat()
            
            self._update_timestamp()
            self._save_to_file()
            
            self.logger.info(f"Saved final state for deal {self.deal_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save final state: {e}")
            return False
    
    def archive(self) -> bool:
        """Archive deal file."""
        try:
            archive_dir = self.deal_files_dir / "archived"
            archive_dir.mkdir(exist_ok=True)
            
            archive_path = archive_dir / f"{self.deal_id}.json"
            self.file_path.rename(archive_path)
            
            self.logger.info(f"Archived deal file {self.deal_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to archive deal file: {e}")
            return False
    
    def delete(self) -> bool:
        """Delete deal file."""
        try:
            if self.file_path.exists():
                self.file_path.unlink()
                self.logger.info(f"Deleted deal file {self.deal_id}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete deal file: {e}")
            return False
    
    def _load_from_file(self) -> bool:
        """Load deal data from file."""
        try:
            if self.file_path.exists():
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.deal_data = json.load(f)
                self.logger.debug(f"Loaded deal data from file")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to load deal data: {e}")
            return False
    
    def _save_to_file(self) -> bool:
        """Save deal data to file."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.deal_data, f, indent=2, ensure_ascii=False)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save deal data: {e}")
            return False
    
    def _update_timestamp(self):
        """Update last modified timestamp."""
        self.deal_data["updated_at"] = datetime.utcnow().isoformat()
    
    def get_file_size(self) -> int:
        """Get deal file size in bytes."""
        try:
            if self.file_path.exists():
                return self.file_path.stat().st_size
            return 0
        except Exception:
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get deal statistics."""
        return {
            "deal_id": self.deal_id,
            "participants_count": len(self.deal_data["participants"]),
            "messages_count": len(self.deal_data["messages"]),
            "negotiation_rounds": len(self.deal_data["negotiation_history"]),
            "agreements_count": len(self.deal_data["agreements"]),
            "file_size_bytes": self.get_file_size(),
            "created_at": self.deal_data["created_at"],
            "updated_at": self.deal_data["updated_at"],
            "status": self.deal_data["status"]
        }

