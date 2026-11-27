from django.core.cache import cache


def dashboard_key(user_id):
    return f"dashboard:{user_id}"


def invalidate_dashboard(user_id):
    cache.delete(dashboard_key(user_id))