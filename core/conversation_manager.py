"""Conversation history management with SQLite."""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from config.settings import DATABASE_PATH


class ConversationManager:
    """Manages conversation history with optional persistence."""
    
    def __init__(self, save_enabled: bool = False):
        """
        Initialize conversation manager.
        
        Args:
            save_enabled: Whether to save conversations to database
        """
        self.save_enabled = save_enabled
        self.memory: List[Dict] = []  # In-memory conversation
        self.db_path = DATABASE_PATH
        
        if self.save_enabled:
            self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_message TEXT NOT NULL,
                assistant_message TEXT NOT NULL,
                humor INTEGER,
                honesty INTEGER,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def set_save_enabled(self, enabled: bool):
        """Toggle conversation saving."""
        self.save_enabled = enabled
        if enabled:
            self._init_database()
    
    def add_exchange(self, user_message: str, assistant_message: str, 
                    humor: Optional[int] = None, honesty: Optional[int] = None,
                    metadata: Optional[Dict] = None):
        """
        Add a conversation exchange.
        
        Args:
            user_message: User's message
            assistant_message: Assistant's response
            humor: Humor setting used
            honesty: Honesty setting used
            metadata: Additional metadata
        """
        exchange = {
            'role': 'user',
            'parts': [user_message],
            'timestamp': datetime.now().isoformat()
        }
        self.memory.append(exchange)
        
        exchange = {
            'role': 'model',
            'parts': [assistant_message],
            'timestamp': datetime.now().isoformat()
        }
        self.memory.append(exchange)
        
        if self.save_enabled:
            self._save_to_database(user_message, assistant_message, humor, honesty, metadata)
    
    def _save_to_database(self, user_message: str, assistant_message: str,
                         humor: Optional[int], honesty: Optional[int],
                         metadata: Optional[Dict]):
        """Save exchange to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute('''
            INSERT INTO conversations 
            (timestamp, user_message, assistant_message, humor, honesty, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            user_message,
            assistant_message,
            humor,
            honesty,
            metadata_json
        ))
        
        conn.commit()
        conn.close()
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get conversation history.
        
        Args:
            limit: Maximum number of exchanges to return
            
        Returns:
            List of conversation exchanges
        """
        if limit:
            return self.memory[-limit:]
        return self.memory.copy()
    
    def get_history_for_api(self) -> List[Dict]:
        """
        Get history formatted for Gemini API.
        
        Returns:
            List of messages in API format
        """
        api_history = []
        for msg in self.memory:
            if 'parts' in msg:
                api_history.append({
                    'role': msg['role'],
                    'parts': msg['parts']
                })
        return api_history
    
    def clear_history(self):
        """Clear conversation history."""
        self.memory = []
        
        if self.save_enabled:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM conversations')
            conn.commit()
            conn.close()
    
    def load_from_database(self, limit: Optional[int] = None):
        """Load conversation history from database."""
        if not self.save_enabled:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT user_message, assistant_message FROM conversations ORDER BY timestamp DESC'
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        # Rebuild memory from database
        self.memory = []
        for user_msg, assistant_msg in reversed(rows):
            self.memory.append({
                'role': 'user',
                'parts': [user_msg],
                'timestamp': datetime.now().isoformat()
            })
            self.memory.append({
                'role': 'model',
                'parts': [assistant_msg],
                'timestamp': datetime.now().isoformat()
            })





