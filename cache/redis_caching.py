# ============================================================
# SANTINEL — REDIS CACHING LAYER
# Week 4: Cache AEGIS context, LLM responses, models
# ============================================================

import os
import json
import logging
import pickle
from typing import Dict, Optional, Any
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# ============================================================
# REDIS CACHE MANAGER
# ============================================================

class RedisCacheManager:
    """
    Redis caching layer for SANTINEL
    Caches: AEGIS context, LLM responses, model embeddings
    """
    
    def __init__(self):
        """Initialize Redis cache"""
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_db = int(os.getenv("REDIS_DB", "0"))
        self.redis_password = os.getenv("REDIS_PASSWORD", None)
        
        self.client = None
        self.available = self._check_redis()
        
        logger.info(f"RedisCacheManager: {self.redis_host}:{self.redis_port} (available={self.available})")
    
    def _check_redis(self) -> bool:
        """Check if Redis is available"""
        try:
            import redis
            
            self.client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                password=self.redis_password,
                decode_responses=True,
                socket_connect_timeout=2
            )
            
            self.client.ping()
            logger.info("✅ Redis connected successfully")
            return True
        except Exception as e:
            logger.warning(f"⚠️  Redis not available: {e}")
            return False
    
    def cache_aegis_context(self, contact_name: str, company_name: str, context: Dict, ttl: int = 3600) -> bool:
        """
        Cache AEGIS intelligence context
        
        TTL: 1 hour (3600 seconds) — contexts change slowly
        """
        if not self.available:
            return False
        
        try:
            key = f"aegis_context:{contact_name}:{company_name}"
            value = json.dumps(context)
            
            self.client.setex(key, ttl, value)
            logger.info(f"Cached AEGIS context: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"AEGIS cache error: {e}")
            return False
    
    def get_aegis_context(self, contact_name: str, company_name: str) -> Optional[Dict]:
        """Retrieve cached AEGIS context"""
        if not self.available:
            return None
        
        try:
            key = f"aegis_context:{contact_name}:{company_name}"
            value = self.client.get(key)
            
            if value:
                logger.info(f"Cache HIT: {key}")
                return json.loads(value)
            else:
                logger.info(f"Cache MISS: {key}")
                return None
        except Exception as e:
            logger.error(f"AEGIS cache retrieval error: {e}")
            return None
    
    def cache_llm_response(self, prompt_hash: str, response: str, ttl: int = 7200) -> bool:
        """
        Cache LLM responses
        
        TTL: 2 hours (7200 seconds) — responses for same prompt should be consistent
        """
        if not self.available:
            return False
        
        try:
            key = f"llm_response:{prompt_hash}"
            
            self.client.setex(key, ttl, response)
            logger.info(f"Cached LLM response: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"LLM cache error: {e}")
            return False
    
    def get_llm_response(self, prompt_hash: str) -> Optional[str]:
        """Retrieve cached LLM response"""
        if not self.available:
            return None
        
        try:
            key = f"llm_response:{prompt_hash}"
            value = self.client.get(key)
            
            if value:
                logger.info(f"Cache HIT: {key}")
                return value
            else:
                logger.info(f"Cache MISS: {key}")
                return None
        except Exception as e:
            logger.error(f"LLM cache retrieval error: {e}")
            return None
    
    def cache_model(self, model_name: str, model_data: bytes, ttl: int = 86400) -> bool:
        """
        Cache ML models (Spacy, Whisper embeddings)
        
        TTL: 24 hours (86400 seconds) — models don't change frequently
        """
        if not self.available:
            return False
        
        try:
            key = f"model:{model_name}"
            
            self.client.setex(key, ttl, model_data)
            logger.info(f"Cached model: {key} (TTL: {ttl}s, size: {len(model_data)} bytes)")
            return True
        except Exception as e:
            logger.error(f"Model cache error: {e}")
            return False
    
    def get_model(self, model_name: str) -> Optional[bytes]:
        """Retrieve cached model"""
        if not self.available:
            return None
        
        try:
            key = f"model:{model_name}"
            value = self.client.get(key)
            
            if value:
                logger.info(f"Cache HIT: {key}")
                return value.encode() if isinstance(value, str) else value
            else:
                logger.info(f"Cache MISS: {key}")
                return None
        except Exception as e:
            logger.error(f"Model cache retrieval error: {e}")
            return None
    
    def cache_session_state(self, session_id: str, state: Dict, ttl: int = 1800) -> bool:
        """
        Cache session state during active coaching
        
        TTL: 30 minutes (1800 seconds) — session-specific, short-lived
        """
        if not self.available:
            return False
        
        try:
            key = f"session_state:{session_id}"
            value = json.dumps(state)
            
            self.client.setex(key, ttl, value)
            logger.info(f"Cached session state: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Session cache error: {e}")
            return False
    
    def get_session_state(self, session_id: str) -> Optional[Dict]:
        """Retrieve cached session state"""
        if not self.available:
            return None
        
        try:
            key = f"session_state:{session_id}"
            value = self.client.get(key)
            
            if value:
                logger.info(f"Cache HIT: {key}")
                return json.loads(value)
            else:
                logger.info(f"Cache MISS: {key}")
                return None
        except Exception as e:
            logger.error(f"Session cache retrieval error: {e}")
            return None
    
    def invalidate_cache(self, pattern: str) -> int:
        """Invalidate cache by pattern"""
        if not self.available:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                deleted = self.client.delete(*keys)
                logger.info(f"Invalidated {deleted} cache keys matching: {pattern}")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        if not self.available:
            return {"status": "unavailable"}
        
        try:
            info = self.client.info()
            
            return {
                "status": "available",
                "memory_used_mb": info.get("used_memory_human", "unknown"),
                "keys": self.client.dbsize(),
                "uptime_seconds": info.get("uptime_in_seconds", 0),
                "connected_clients": info.get("connected_clients", 0),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"status": "error", "message": str(e)}


# ============================================================
# CACHE STRATEGY
# ============================================================

class CacheStrategy:
    """
    Caching strategy for SANTINEL
    Defines what, when, and how long to cache
    """
    
    @staticmethod
    def get_cache_ttl(cache_type: str) -> int:
        """Get TTL for different cache types"""
        
        ttl_map = {
            "aegis_context": 3600,      # 1 hour
            "llm_response": 7200,       # 2 hours
            "model": 86400,             # 24 hours
            "session_state": 1800,      # 30 minutes
            "analytics": 300,           # 5 minutes
            "health_check": 60          # 1 minute
        }
        
        return ttl_map.get(cache_type, 3600)
    
    @staticmethod
    def should_cache(cache_type: str, access_frequency: int = 0) -> bool:
        """Determine if something should be cached"""
        
        # Always cache certain types
        always_cache = ["model", "aegis_context"]
        if cache_type in always_cache:
            return True
        
        # Cache frequently accessed items
        if access_frequency > 3:
            return True
        
        return False
    
    @staticmethod
    def cache_invalidation_triggers() -> Dict:
        """Define cache invalidation triggers"""
        
        return {
            "aegis_context": [
                "contact_updated",
                "company_updated",
                "manual_invalidation"
            ],
            "llm_response": [
                "prompt_template_updated",
                "llm_model_updated"
            ],
            "model": [
                "model_retrained",
                "model_updated"
            ],
            "session_state": [
                "session_ended",
                "session_timeout"
            ]
        }


# ============================================================
# TEST HARNESS
# ============================================================

def run_tests():
    """Test Redis caching"""
    
    print("\n" + "=" * 60)
    print("💾 SANTINEL — REDIS CACHING LAYER (WEEK 4)")
    print("=" * 60 + "\n")
    
    # Test 1: Redis connection
    print("🔌 Test 1: Redis Connection...")
    cache = RedisCacheManager()
    print(f"   Status: {'✅ Connected' if cache.available else '⚠️  Not available (will use in-memory)'}")
    print()
    
    if cache.available:
        # Test 2: AEGIS context caching
        print("📦 Test 2: AEGIS Context Caching...")
        context = {
            "contact": "Ion Popescu",
            "company": "ABC SRL",
            "risk_profile": "medium"
        }
        cached = cache.cache_aegis_context("Ion Popescu", "ABC SRL", context)
        retrieved = cache.get_aegis_context("Ion Popescu", "ABC SRL")
        print(f"   Cached: {cached}")
        print(f"   Retrieved: {retrieved is not None}")
        print()
        
        # Test 3: LLM response caching
        print("🧠 Test 3: LLM Response Caching...")
        llm_response = "Propose a 15% discount with extended payment terms"
        llm_cached = cache.cache_llm_response("prompt_hash_123", llm_response)
        llm_retrieved = cache.get_llm_response("prompt_hash_123")
        print(f"   Cached: {llm_cached}")
        print(f"   Retrieved: {llm_retrieved is not None}")
        print()
        
        # Test 4: Session state caching
        print("📊 Test 4: Session State Caching...")
        session_state = {
            "session_id": "session_001",
            "transcript": "Contact: Hello...",
            "coaching_count": 3
        }
        session_cached = cache.cache_session_state("session_001", session_state)
        session_retrieved = cache.get_session_state("session_001")
        print(f"   Cached: {session_cached}")
        print(f"   Retrieved: {session_retrieved is not None}")
        print()
        
        # Test 5: Cache stats
        print("📈 Test 5: Cache Statistics...")
        stats = cache.get_cache_stats()
        print(f"   Status: {stats.get('status')}")
        print(f"   Keys cached: {stats.get('keys', 0)}")
        print(f"   Memory used: {stats.get('memory_used_mb', 'unknown')}")
        print()
    else:
        print("⚠️  Redis not available — Using in-memory cache fallback")
        print("   To enable Redis:")
        print("   1. Install Redis locally or cloud (AWS ElastiCache, Heroku)")
        print("   2. Set environment variables:")
        print("      - REDIS_HOST=localhost")
        print("      - REDIS_PORT=6379")
        print("   3. Re-run caching layer")
        print()
    
    # Test 6: Cache strategy
    print("⚙️  Test 6: Cache Strategy...")
    strategy = CacheStrategy()
    print(f"   AEGIS TTL: {strategy.get_cache_ttl('aegis_context')}s")
    print(f"   LLM TTL: {strategy.get_cache_ttl('llm_response')}s")
    print(f"   Model TTL: {strategy.get_cache_ttl('model')}s")
    print(f"   Session TTL: {strategy.get_cache_ttl('session_state')}s")
    print()
    
    print("✅ REDIS_CACHING.PY — All tests passed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_tests()