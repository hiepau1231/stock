import logging
import time
from functools import wraps
from django.core.cache import cache
from django.db import connection, reset_queries
from django.conf import settings

logger = logging.getLogger(__name__)

def query_debugger(func):
    """Decorator để đếm và log số lượng queries trong một function"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        reset_queries()
        number_of_start_queries = len(connection.queries)
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        number_of_end_queries = len(connection.queries)
        queries = connection.queries
        logger.debug(f"Function : {func.__name__}")
        logger.debug(f"Number of Queries : {number_of_end_queries - number_of_start_queries}")
        logger.debug(f"Finished in : {(end - start):.2f}s")
        return result
    return wrapper

def cache_with_key(key_prefix, timeout=300):
    """Decorator để cache kết quả của một function với custom key"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}_{args}_{kwargs}"
            result = cache.get(cache_key)
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator

def bulk_create_or_update(model, objects, batch_size=1000):
    """Helper function để tối ưu việc tạo/cập nhật nhiều records"""
    if not objects:
        return

    existing_objects = model.objects.filter(
        id__in=[obj.id for obj in objects if obj.id]
    )
    existing_ids = {obj.id for obj in existing_objects}
    
    # Tách thành objects cần create và update
    to_create = [obj for obj in objects if not obj.id]
    to_update = [obj for obj in objects if obj.id in existing_ids]
    
    # Bulk create
    if to_create:
        model.objects.bulk_create(
            to_create,
            batch_size=batch_size
        )
    
    # Bulk update
    if to_update:
        model.objects.bulk_update(
            to_update,
            fields=[field.name for field in model._meta.fields if field.name != 'id'],
            batch_size=batch_size
        )

def optimize_queryset(queryset, select_related=None, prefetch_related=None):
    """Helper function để tối ưu queryset"""
    if select_related:
        queryset = queryset.select_related(*select_related)
    if prefetch_related:
        queryset = queryset.prefetch_related(*prefetch_related)
    return queryset
