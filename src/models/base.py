import sqlite3
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import uuid

@dataclass
class BaseModel:
    """Base model for all entities"""
    id: str
    
    def to_dict(self) -> dict:
        """Convert model to dictionary for database insertion"""
        data = asdict(self)
        # Convert datetime to ISO format
        for key, value in data.items():
            if isinstance(value, (datetime, date)):
                data[key] = value.isoformat()
        return data

class Database:
    def __init__(self, db_path: str = "output/asana_simulation.sqlite"):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to SQLite database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access
        return self.conn
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def initialize(self):
        """Initialize database with schema"""
        with self.connect() as conn:
            with open('schema.sql', 'r') as f:
                schema = f.read()
            conn.executescript(schema)
            conn.commit()
    
    def insert(self, table: str, data: dict) -> str:
        """Insert data into table and return ID"""
        with self.connect() as conn:
            # Remove None values
            data = {k: v for k, v in data.items() if v is not None}
            
            # Generate UUID if not provided
            if 'id' not in data:
                data['id'] = str(uuid.uuid4())
            
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            values = list(data.values())
            
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            conn.execute(sql, values)
            conn.commit()
            return data['id']
    
    def insert_many(self, table: str, data_list: List[dict]):
        """Batch insert multiple records"""
        if not data_list:
            return
        
        with self.connect() as conn:
            # Generate IDs for all records
            for data in data_list:
                if 'id' not in data:
                    data['id'] = str(uuid.uuid4())
            
            columns = ', '.join(data_list[0].keys())
            placeholders = ', '.join(['?' for _ in data_list[0]])
            values = [list(data.values()) for data in data_list]
            
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            conn.executemany(sql, values)
            conn.commit()
    
    def query(self, sql: str, params: tuple = ()) -> List[dict]:
        """Execute query and return results as dicts"""
        with self.connect() as conn:
            cursor = conn.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_random(self, table: str, limit: int = 1) -> List[dict]:
        """Get random records from table"""
        sql = f"SELECT * FROM {table} ORDER BY RANDOM() LIMIT ?"
        return self.query(sql, (limit,))

# Helper function for Asana-like GID generation
def generate_gid() -> str:
    """Generate Asana-style GID (not exactly, but similar pattern)"""
    return str(uuid.uuid4()).replace('-', '')