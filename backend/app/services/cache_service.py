"""
Cache Service for Hospital Management System.
Provides centralized caching functionality with Redis backend and fallback to simple cache.
"""
import hashlib
import json
import logging
from functools import wraps
from flask import current_app, request
from flask_caching import Cache

logger = logging.getLogger(__name__)

# Initialize cache instance (configured in app factory)
cache = Cache()


class CacheService:
    """Service class for managing cache operations with helper methods."""

    # Cache key prefixes for different data types
    PREFIXES = {
        'department': 'dept',
        'doctor': 'doc',
        'patient': 'pat',
        'availability': 'avail',
        'appointment': 'apt',
        'dashboard': 'dash',
        'search': 'search',
        'stats': 'stats'
    }

    @staticmethod
    def make_key(*args, **kwargs):
        """
        Generate a cache key from arguments.

        Args:
            *args: Positional arguments to include in key
            **kwargs: Keyword arguments to include in key

        Returns:
            str: Cache key string
        """
        key_parts = [str(arg) for arg in args]
        for k, v in sorted(kwargs.items()):
            if v is not None:
                key_parts.append(f"{k}:{v}")
        return ':'.join(key_parts)

    @staticmethod
    def make_search_key(prefix, query_params):
        """
        Generate a cache key for search queries using hash.

        Args:
            prefix: Key prefix (e.g., 'search:doctors')
            query_params: Dictionary of query parameters

        Returns:
            str: Hashed cache key
        """
        # Sort params for consistent key generation
        sorted_params = json.dumps(query_params, sort_keys=True)
        param_hash = hashlib.md5(sorted_params.encode()).hexdigest()[:12]
        return f"{prefix}:{param_hash}"

    @staticmethod
    def get_ttl(ttl_type='default'):
        """
        Get TTL value from configuration.

        Args:
            ttl_type: Type of TTL ('static', 'semi_static', 'dynamic', 'realtime', 'search')

        Returns:
            int: TTL value in seconds
        """
        ttl_map = {
            'static': 'CACHE_TTL_STATIC',
            'semi_static': 'CACHE_TTL_SEMI_STATIC',
            'dynamic': 'CACHE_TTL_DYNAMIC',
            'realtime': 'CACHE_TTL_REALTIME',
            'search': 'CACHE_TTL_SEARCH',
            'default': 'CACHE_DEFAULT_TIMEOUT'
        }
        config_key = ttl_map.get(ttl_type, 'CACHE_DEFAULT_TIMEOUT')
        return current_app.config.get(config_key, 300)

    @staticmethod
    def invalidate_pattern(pattern):
        """
        Invalidate all cache keys matching a pattern.

        Args:
            pattern: Key pattern to match (e.g., 'dept:*')
        """
        try:
            if hasattr(cache, 'cache') and hasattr(cache.cache, '_read_client'):
                # Redis backend - use SCAN for pattern matching
                redis_client = cache.cache._read_client
                prefix = current_app.config.get('CACHE_KEY_PREFIX', 'hms_cache_')
                full_pattern = f"{prefix}{pattern}"

                cursor = 0
                while True:
                    cursor, keys = redis_client.scan(cursor, match=full_pattern, count=100)
                    if keys:
                        redis_client.delete(*keys)
                    if cursor == 0:
                        break
                logger.info(f"Invalidated cache keys matching: {pattern}")
            else:
                # Simple cache - clear all (fallback)
                cache.clear()
                logger.info("Cleared all cache (simple cache backend)")
        except Exception as e:
            logger.warning(f"Failed to invalidate cache pattern {pattern}: {e}")

    @staticmethod
    def invalidate_department_cache(department_id=None):
        """Invalidate department-related cache."""
        if department_id:
            cache.delete(f"dept:{department_id}")
            cache.delete(f"dept:{department_id}:details")
        CacheService.invalidate_pattern("dept:*")
        CacheService.invalidate_pattern("search:dept:*")
        logger.info(f"Invalidated department cache (id={department_id})")

    @staticmethod
    def invalidate_doctor_cache(doctor_id=None, department_id=None):
        """Invalidate doctor-related cache."""
        if doctor_id:
            cache.delete(f"doc:{doctor_id}")
            cache.delete(f"doc:{doctor_id}:details")
            CacheService.invalidate_pattern(f"avail:{doctor_id}:*")
        if department_id:
            CacheService.invalidate_pattern(f"dept:{department_id}:doctors:*")
        CacheService.invalidate_pattern("doc:list:*")
        CacheService.invalidate_pattern("search:doc:*")
        logger.info(f"Invalidated doctor cache (id={doctor_id}, dept={department_id})")

    @staticmethod
    def invalidate_availability_cache(doctor_id, date=None):
        """Invalidate availability cache for a doctor."""
        if date:
            cache.delete(f"avail:{doctor_id}:{date}")
        else:
            CacheService.invalidate_pattern(f"avail:{doctor_id}:*")
        logger.info(f"Invalidated availability cache (doctor={doctor_id}, date={date})")

    @staticmethod
    def invalidate_appointment_cache(doctor_id=None, patient_id=None):
        """Invalidate appointment-related cache."""
        if doctor_id:
            CacheService.invalidate_pattern(f"apt:doc:{doctor_id}:*")
            CacheService.invalidate_pattern(f"dash:doc:{doctor_id}:*")
        if patient_id:
            CacheService.invalidate_pattern(f"apt:pat:{patient_id}:*")
            CacheService.invalidate_pattern(f"dash:pat:{patient_id}:*")
        CacheService.invalidate_pattern("dash:admin:*")
        logger.info(f"Invalidated appointment cache (doctor={doctor_id}, patient={patient_id})")

    @staticmethod
    def invalidate_patient_cache(patient_id=None):
        """Invalidate patient-related cache."""
        if patient_id:
            cache.delete(f"pat:{patient_id}")
            CacheService.invalidate_pattern(f"pat:{patient_id}:*")
        CacheService.invalidate_pattern("pat:list:*")
        CacheService.invalidate_pattern("search:pat:*")
        logger.info(f"Invalidated patient cache (id={patient_id})")

    @staticmethod
    def invalidate_dashboard_cache(role=None, user_id=None):
        """Invalidate dashboard statistics cache."""
        if role and user_id:
            cache.delete(f"dash:{role}:{user_id}:stats")
        elif role:
            CacheService.invalidate_pattern(f"dash:{role}:*")
        else:
            CacheService.invalidate_pattern("dash:*")
        logger.info(f"Invalidated dashboard cache (role={role}, user={user_id})")


def cached_with_key(key_func, ttl_type='default'):
    """
    Decorator for caching with custom key function.

    Args:
        key_func: Function that returns cache key from request
        ttl_type: TTL type for cache expiration

    Returns:
        Decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                cache_key = key_func(*args, **kwargs)
                cached_value = cache.get(cache_key)

                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_value

                logger.debug(f"Cache miss: {cache_key}")
                result = f(*args, **kwargs)

                ttl = CacheService.get_ttl(ttl_type)
                cache.set(cache_key, result, timeout=ttl)

                return result
            except Exception as e:
                logger.warning(f"Cache error, falling back to direct call: {e}")
                return f(*args, **kwargs)

        return decorated_function
    return decorator


def cache_response(ttl_type='default', key_prefix=None):
    """
    Decorator for caching API responses.

    Args:
        ttl_type: TTL type for cache expiration
        key_prefix: Optional prefix for cache key

    Returns:
        Decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Build cache key from endpoint and arguments
                prefix = key_prefix or f.__name__
                key_parts = [prefix]

                # Add URL parameters
                for arg in args:
                    key_parts.append(str(arg))
                for k, v in sorted(kwargs.items()):
                    if v is not None:
                        key_parts.append(f"{k}:{v}")

                # Add query parameters
                if request and request.args:
                    for k, v in sorted(request.args.items()):
                        key_parts.append(f"{k}:{v}")

                cache_key = ':'.join(key_parts)
                cached_value = cache.get(cache_key)

                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_value

                logger.debug(f"Cache miss: {cache_key}")
                result = f(*args, **kwargs)

                # Only cache successful responses
                if isinstance(result, tuple):
                    response, status = result
                    if 200 <= status < 300:
                        ttl = CacheService.get_ttl(ttl_type)
                        cache.set(cache_key, result, timeout=ttl)
                else:
                    ttl = CacheService.get_ttl(ttl_type)
                    cache.set(cache_key, result, timeout=ttl)

                return result
            except Exception as e:
                logger.warning(f"Cache error, falling back to direct call: {e}")
                return f(*args, **kwargs)

        return decorated_function
    return decorator


# Export commonly used items
cache_service = CacheService()
