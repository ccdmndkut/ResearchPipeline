import json
import hashlib
import pickle
from typing import Any, Optional, Union
from datetime import datetime, timedelta
import asyncio
from pathlib import Path

try:
    import aioredis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

from app.settings import settings
from app.utils.logging_config import setup_logging

logger = setup_logging(__name__)


class Cache:
    """
    Caching utility with Redis and local file fallback
    """

    def __init__(self):
        self.redis_client = None
        self.local_cache = {}
        self.cache_dir = settings.TEMP_DIR / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = settings.CACHE_TTL

    async def connect(self):
        """
        Connect to Redis if available
        """
        if settings.CACHE_ENABLED and settings.REDIS_URL and HAS_REDIS:
            try:
                self.redis_client = await aioredis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True
                )
                await self.redis_client.ping()
                logger.info("Connected to Redis cache")
            except Exception as e:
                logger.warning(f"Redis connection failed, using local cache: {e}")
                self.redis_client = None
        else:
            logger.info("Redis not available, using local cache only")
            self.redis_client = None

    async def disconnect(self):
        """
        Disconnect from Redis
        """
        if self.redis_client:
            await self.redis_client.close()

    def _generate_key(self, key: str, prefix: Optional[str] = None) -> str:
        """
        Generate a cache key with optional prefix
        """
        if prefix:
            return f"{prefix}:{key}"
        return key

    def _hash_key(self, key: str) -> str:
        """
        Hash a key for file-based caching
        """
        return hashlib.md5(key.encode()).hexdigest()

    async def get(
        self,
        key: str,
        prefix: Optional[str] = None,
        default: Any = None
    ) -> Any:
        """
        Get value from cache
        """
        if not settings.CACHE_ENABLED:
            return default

        full_key = self._generate_key(key, prefix)

        # Try Redis first
        if self.redis_client:
            try:
                value = await self.redis_client.get(full_key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.error(f"Redis get error: {e}")

        # Try local memory cache
        if full_key in self.local_cache:
            entry = self.local_cache[full_key]
            if entry["expires"] > datetime.now():
                return entry["value"]
            else:
                del self.local_cache[full_key]

        # Try file cache
        file_path = self.cache_dir / f"{self._hash_key(full_key)}.cache"
        if file_path.exists():
            try:
                with open(file_path, 'rb') as f:
                    entry = pickle.load(f)
                    if entry["expires"] > datetime.now():
                        return entry["value"]
                    else:
                        file_path.unlink()
            except Exception as e:
                logger.error(f"File cache read error: {e}")

        return default

    async def set(
        self,
        key: str,
        value: Any,
        prefix: Optional[str] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache
        """
        if not settings.CACHE_ENABLED:
            return False

        full_key = self._generate_key(key, prefix)
        ttl = ttl or self.ttl
        expires = datetime.now() + timedelta(seconds=ttl)

        # Try Redis first
        if self.redis_client:
            try:
                await self.redis_client.set(
                    full_key,
                    json.dumps(value),
                    ex=ttl
                )
                return True
            except Exception as e:
                logger.error(f"Redis set error: {e}")

        # Set in local memory cache
        self.local_cache[full_key] = {
            "value": value,
            "expires": expires
        }

        # Set in file cache
        file_path = self.cache_dir / f"{self._hash_key(full_key)}.cache"
        try:
            with open(file_path, 'wb') as f:
                pickle.dump({
                    "value": value,
                    "expires": expires
                }, f)
            return True
        except Exception as e:
            logger.error(f"File cache write error: {e}")
            return False

    async def delete(self, key: str, prefix: Optional[str] = None) -> bool:
        """
        Delete value from cache
        """
        full_key = self._generate_key(key, prefix)

        # Delete from Redis
        if self.redis_client:
            try:
                await self.redis_client.delete(full_key)
            except Exception as e:
                logger.error(f"Redis delete error: {e}")

        # Delete from local memory cache
        if full_key in self.local_cache:
            del self.local_cache[full_key]

        # Delete from file cache
        file_path = self.cache_dir / f"{self._hash_key(full_key)}.cache"
        if file_path.exists():
            file_path.unlink()

        return True

    async def clear(self, prefix: Optional[str] = None) -> bool:
        """
        Clear cache (optionally by prefix)
        """
        if prefix:
            # Clear by prefix
            if self.redis_client:
                try:
                    keys = await self.redis_client.keys(f"{prefix}:*")
                    if keys:
                        await self.redis_client.delete(*keys)
                except Exception as e:
                    logger.error(f"Redis clear error: {e}")

            # Clear from local memory cache
            keys_to_delete = [
                k for k in self.local_cache.keys()
                if k.startswith(f"{prefix}:")
            ]
            for key in keys_to_delete:
                del self.local_cache[key]

        else:
            # Clear all
            if self.redis_client:
                try:
                    await self.redis_client.flushdb()
                except Exception as e:
                    logger.error(f"Redis flush error: {e}")

            self.local_cache.clear()

            # Clear file cache
            for file_path in self.cache_dir.glob("*.cache"):
                file_path.unlink()

        return True

    async def exists(self, key: str, prefix: Optional[str] = None) -> bool:
        """
        Check if key exists in cache
        """
        full_key = self._generate_key(key, prefix)

        # Check Redis
        if self.redis_client:
            try:
                exists = await self.redis_client.exists(full_key)
                if exists:
                    return True
            except Exception as e:
                logger.error(f"Redis exists error: {e}")

        # Check local memory cache
        if full_key in self.local_cache:
            if self.local_cache[full_key]["expires"] > datetime.now():
                return True

        # Check file cache
        file_path = self.cache_dir / f"{self._hash_key(full_key)}.cache"
        return file_path.exists()

    def cleanup_expired(self):
        """
        Remove expired entries from local caches
        """
        # Cleanup memory cache
        now = datetime.now()
        expired_keys = [
            k for k, v in self.local_cache.items()
            if v["expires"] <= now
        ]
        for key in expired_keys:
            del self.local_cache[key]

        # Cleanup file cache
        for file_path in self.cache_dir.glob("*.cache"):
            try:
                with open(file_path, 'rb') as f:
                    entry = pickle.load(f)
                    if entry["expires"] <= now:
                        file_path.unlink()
            except Exception:
                # Remove corrupted cache files
                file_path.unlink()


# Singleton cache instance
_cache = Cache()


async def get_cache() -> Cache:
    """
    Get the singleton cache instance
    """
    if not _cache.redis_client and settings.CACHE_ENABLED and HAS_REDIS:
        await _cache.connect()
    return _cache