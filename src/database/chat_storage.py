"""
Database models for SwarmBot chat history storage
Stores all chat interactions, MCP tool calls, and raw data
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ChatDatabase:
    """Manages the chat history database with raw data storage"""
    
    def __init__(self, db_path: str = "swarmbot_chats.db"):
        """Initialize the database connection and create tables if needed"""
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database and create tables"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            self._create_tables()
            logger.info(f"Chat database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _create_tables(self):
        """Create all necessary tables for chat storage"""
        cursor = self.conn.cursor()
        
        # Chat sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                llm_provider TEXT,
                metadata JSON
            )
        """)
        
        # Chat messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                message_id TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                raw_data JSON,
                FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
            )
        """)
        
        # Tool calls table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tool_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL,
                tool_name TEXT NOT NULL,
                tool_server TEXT,
                request_data JSON,
                response_data JSON,
                duration_ms INTEGER,
                status TEXT,
                error_message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES chat_messages(message_id)
            )
        """)
        
        # MCP raw logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mcp_raw_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                direction TEXT NOT NULL,
                protocol TEXT,
                server_name TEXT,
                method TEXT,
                raw_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON chat_messages(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tools_message ON tool_calls(message_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_session ON mcp_raw_logs(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON mcp_raw_logs(timestamp)")
        
        self.conn.commit()
    
    def create_session(self, session_id: str, llm_provider: str = None, metadata: Dict = None) -> int:
        """Create a new chat session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO chat_sessions (session_id, llm_provider, metadata)
            VALUES (?, ?, ?)
        """, (session_id, llm_provider, json.dumps(metadata or {})))
        self.conn.commit()
        return cursor.lastrowid
    
    def end_session(self, session_id: str):
        """Mark a session as ended"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE chat_sessions 
            SET ended_at = CURRENT_TIMESTAMP 
            WHERE session_id = ?
        """, (session_id,))
        self.conn.commit()
    
    def add_message(self, session_id: str, message_id: str, role: str, content: str, raw_data: Dict = None):
        """Add a chat message to the database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO chat_messages (session_id, message_id, role, content, raw_data)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, message_id, role, content, json.dumps(raw_data or {})))
        self.conn.commit()
    
    def add_tool_call(self, message_id: str, tool_name: str, tool_server: str = None,
                      request_data: Dict = None, response_data: Dict = None,
                      duration_ms: int = None, status: str = "success", error_message: str = None):
        """Add a tool call record"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO tool_calls (
                message_id, tool_name, tool_server, request_data, response_data,
                duration_ms, status, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            message_id, tool_name, tool_server,
            json.dumps(request_data or {}), json.dumps(response_data or {}),
            duration_ms, status, error_message
        ))
        self.conn.commit()
    
    def add_mcp_log(self, session_id: str, direction: str, protocol: str = None,
                    server_name: str = None, method: str = None, raw_data: str = None):
        """Add a raw MCP protocol log entry"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO mcp_raw_logs (
                session_id, direction, protocol, server_name, method, raw_data
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, direction, protocol, server_name, method, raw_data))
        self.conn.commit()
    
    def get_session_messages(self, session_id: str) -> List[Dict]:
        """Get all messages for a session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM chat_messages 
            WHERE session_id = ? 
            ORDER BY timestamp
        """, (session_id,))
        
        messages = []
        for row in cursor.fetchall():
            msg = dict(row)
            if msg.get('raw_data'):
                msg['raw_data'] = json.loads(msg['raw_data'])
            messages.append(msg)
        
        return messages
    
    def get_message_tools(self, message_id: str) -> List[Dict]:
        """Get all tool calls for a message"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM tool_calls 
            WHERE message_id = ? 
            ORDER BY timestamp
        """, (message_id,))
        
        tools = []
        for row in cursor.fetchall():
            tool = dict(row)
            if tool.get('request_data'):
                tool['request_data'] = json.loads(tool['request_data'])
            if tool.get('response_data'):
                tool['response_data'] = json.loads(tool['response_data'])
            tools.append(tool)
        
        return tools
    
    def get_session_mcp_logs(self, session_id: str, limit: int = 1000) -> List[Dict]:
        """Get MCP protocol logs for a session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM mcp_raw_logs 
            WHERE session_id = ? 
            ORDER BY timestamp DESC
            LIMIT ?
        """, (session_id, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def search_messages(self, query: str, limit: int = 100) -> List[Dict]:
        """Search messages by content"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT m.*, s.llm_provider 
            FROM chat_messages m
            JOIN chat_sessions s ON m.session_id = s.session_id
            WHERE m.content LIKE ?
            ORDER BY m.timestamp DESC
            LIMIT ?
        """, (f"%{query}%", limit))
        
        results = []
        for row in cursor.fetchall():
            msg = dict(row)
            if msg.get('raw_data'):
                msg['raw_data'] = json.loads(msg['raw_data'])
            results.append(msg)
        
        return results
    
    def get_sessions(self, limit: int = 50) -> List[Dict]:
        """Get recent chat sessions"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT s.*, 
                   COUNT(DISTINCT m.id) as message_count,
                   COUNT(DISTINCT t.id) as tool_count
            FROM chat_sessions s
            LEFT JOIN chat_messages m ON s.session_id = m.session_id
            LEFT JOIN tool_calls t ON m.message_id = t.message_id
            GROUP BY s.session_id
            ORDER BY s.started_at DESC
            LIMIT ?
        """, (limit,))
        
        sessions = []
        for row in cursor.fetchall():
            session = dict(row)
            if session.get('metadata'):
                session['metadata'] = json.loads(session['metadata'])
            sessions.append(session)
        
        return sessions
    
    def export_session(self, session_id: str, output_path: str):
        """Export a complete session to JSON file"""
        data = {
            'session': self._get_session_info(session_id),
            'messages': [],
            'mcp_logs': self.get_session_mcp_logs(session_id)
        }
        
        messages = self.get_session_messages(session_id)
        for msg in messages:
            msg['tool_calls'] = self.get_message_tools(msg['message_id'])
            data['messages'].append(msg)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Exported session {session_id} to {output_path}")
    
    def _get_session_info(self, session_id: str) -> Dict:
        """Get session information"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM chat_sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if row:
            session = dict(row)
            if session.get('metadata'):
                session['metadata'] = json.loads(session['metadata'])
            return session
        return None
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Chat database connection closed")


# Integration with ChatSession
class ChatLogger:
    """Integrates chat logging with the ChatSession"""
    
    def __init__(self, db: ChatDatabase, session_id: str):
        self.db = db
        self.session_id = session_id
        self.message_counter = 0
        self.start_time = datetime.utcnow()
    
    def log_user_message(self, content: str, raw_data: Dict = None) -> str:
        """Log a user message"""
        message_id = f"{self.session_id}_user_{self.message_counter}"
        self.message_counter += 1
        self.db.add_message(self.session_id, message_id, "user", content, raw_data)
        return message_id
    
    def log_assistant_message(self, content: str, raw_data: Dict = None) -> str:
        """Log an assistant message"""
        message_id = f"{self.session_id}_assistant_{self.message_counter}"
        self.message_counter += 1
        self.db.add_message(self.session_id, message_id, "assistant", content, raw_data)
        return message_id
    
    def log_tool_call(self, message_id: str, tool_name: str, server_name: str,
                      request: Dict, response: Dict, duration_ms: int, error: str = None):
        """Log a tool call with timing information"""
        status = "error" if error else "success"
        self.db.add_tool_call(
            message_id, tool_name, server_name,
            request, response, duration_ms, status, error
        )
    
    def log_mcp_request(self, server_name: str, method: str, params: Dict):
        """Log an outgoing MCP request"""
        raw_data = json.dumps({
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        })
        self.db.add_mcp_log(
            self.session_id, "request", "jsonrpc",
            server_name, method, raw_data
        )
    
    def log_mcp_response(self, server_name: str, method: str, result: Any):
        """Log an incoming MCP response"""
        raw_data = json.dumps({
            "jsonrpc": "2.0",
            "result": result
        })
        self.db.add_mcp_log(
            self.session_id, "response", "jsonrpc",
            server_name, method, raw_data
        )


if __name__ == "__main__":
    # Test the database
    db = ChatDatabase("test_chats.db")
    
    # Create a test session
    session_id = f"test_session_{datetime.now().timestamp()}"
    db.create_session(session_id, "openai", {"test": True})
    
    # Add test messages
    db.add_message(session_id, "msg1", "user", "Hello, how are you?")
    db.add_message(session_id, "msg2", "assistant", "I'm doing well, thank you!")
    
    # Add test tool call
    db.add_tool_call(
        "msg2", "web_search", "brave",
        {"query": "weather today"},
        {"results": ["sunny", "72°F"]},
        250
    )
    
    # Add MCP log
    db.add_mcp_log(
        session_id, "request", "jsonrpc",
        "brave", "search", '{"query": "weather today"}'
    )
    
    # Test retrieval
    sessions = db.get_sessions()
    print(f"Found {len(sessions)} sessions")
    
    messages = db.get_session_messages(session_id)
    print(f"Found {len(messages)} messages")
    
    # Close database
    db.close()
