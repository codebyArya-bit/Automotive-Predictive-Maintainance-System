"""
Cache Manager for AutoMind API
Implements Redis-based caching for frequently accessed data
"""

import json
import os
import redis
from typing import Any, Optional, Dict
import structlog
from config import Config

logger = structlog.get_logger(__name__)


class CacheManager:
    """
    Redis-based cache manager for API responses and frequently accessed data
    """

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self._redis_client: Optional[redis.Redis] = None
        self._initialized = False

        # Cache TTL settings (in seconds)
        self.cache_ttl = {
            "dashboard": 60,  # 1 minute
            "vehicles": 300,  # 5 minutes
            "telemetry": 30,  # 30 seconds
            "maintenance": 600,  # 10 minutes
            "vehicle_count": 1800,  # 30 minutes
        }

    async def initialize(self):
        """Initialize Redis connection"""
        if self._initialized:
            return

        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self._redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )

            # Test connection
            await self._redis_client.ping()
            self._initialized = True
            logger.info("Cache manager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize cache manager: {e}")
            # Continue without cache if Redis is unavailable
            self._redis_client = None

    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate a consistent cache key"""
        key_parts = [prefix]
        for k, v in sorted(kwargs.items()):
            if v is not None:
                key_parts.append(f"{k}:{v}")
        return ":".join(key_parts)

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self._redis_client:
            return None

        try:
            value = await self._redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")

        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        if not self._redis_client:
            return False

        try:
            serialized_value = json.dumps(value, default=str)
            if ttl:
                await self._redis_client.setex(key, ttl, serialized_value)
            else:
                await self._redis_client.set(key, serialized_value)
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self._redis_client:
            return False

        try:
            await self._redis_client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern"""
        if not self._redis_client:
            return 0

        try:
            keys = await self._redis_client.keys(pattern)
            if keys:
                return await self._redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache invalidate pattern error for {pattern}: {e}")
            return 0

    # Specific cache methods for different data types

    async def get_vehicles_cache(
        self, page: int, limit: int, make: str = None, model: str = None, status: str = None
    ) -> Optional[Dict]:
        """Get cached vehicles data"""
        key = self._generate_cache_key("vehicles", page=page, limit=limit, make=make, model=model, status=status)
        return await self.get(key)

    async def set_vehicles_cache(
        self, data: Dict, page: int, limit: int, make: str = None, model: str = None, status: str = None
    ) -> bool:
        """Cache vehicles data"""
        key = self._generate_cache_key("vehicles", page=page, limit=limit, make=make, model=model, status=status)
        return await self.set(key, data, self.cache_ttl["vehicles"])

    async def get_telemetry_cache(
        self, vehicle_id: str, page: int, limit: int, start_date: str = None, end_date: str = None
    ) -> Optional[Dict]:
        """Get cached telemetry data"""
        key = self._generate_cache_key(
            "telemetry", vehicle_id=vehicle_id, page=page, limit=limit, start_date=start_date, end_date=end_date
        )
        return await self.get(key)

    async def set_telemetry_cache(
        self, data: Dict, vehicle_id: str, page: int, limit: int, start_date: str = None, end_date: str = None
    ) -> bool:
        """Cache telemetry data"""
        key = self._generate_cache_key(
            "telemetry", vehicle_id=vehicle_id, page=page, limit=limit, start_date=start_date, end_date=end_date
        )
        return await self.set(key, data, self.cache_ttl["telemetry"])

    async def get_dashboard_cache(self) -> Optional[Dict]:
        """Get cached dashboard data"""
        return await self.get("dashboard:data")

    async def set_dashboard_cache(self, data: Dict) -> bool:
        """Cache dashboard data"""
        return await self.set("dashboard:data", data, self.cache_ttl["dashboard"])

    async def invalidate_vehicle_cache(self, vehicle_id: str = None):
        """Invalidate vehicle-related cache"""
        patterns = ["vehicles:*"]
        if vehicle_id:
            patterns.append(f"telemetry:vehicle_id:{vehicle_id}:*")

        for pattern in patterns:
            await self.invalidate_pattern(pattern)

    async def invalidate_telemetry_cache(self, vehicle_id: str):
        """Invalidate telemetry cache for a specific vehicle"""
        pattern = f"telemetry:vehicle_id:{vehicle_id}:*"
        await self.invalidate_pattern(pattern)

    async def health_check(self) -> Dict[str, Any]:
        """Check cache health status"""
        if not self._redis_client:
            return {"status": "unavailable", "message": "Redis not connected"}

        try:
            await self._redis_client.ping()
            info = await self._redis_client.info()
            return {
                "status": "healthy",
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "unknown"),
                "uptime": info.get("uptime_in_seconds", 0),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Global cache manager instance
cache_manager = CacheManager()
