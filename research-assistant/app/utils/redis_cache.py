import redis
import json
from typing import Optional, Any
import hashlib

class ResearchCache:
    def __init__(self):
        self.client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )
        self.ttl = 3600  # 1 hour
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached result"""
        data = self.client.get(key)
        return json.loads(data) if data else None
    
    async def set(self, key: str, value: Any, ttl: int = None):
        """Cache result with TTL"""
        self.client.setex(
            key,
            ttl or self.ttl,
            json.dumps(value)
        )
    
    def generate_key(self, query: str, params: dict) -> str:
        """Generate cache key from query and parameters"""
        data = {'query': query, **params}
        return hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()