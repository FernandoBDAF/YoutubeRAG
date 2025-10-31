from typing import Any, Dict, Optional


def build_filters(
    topic: Optional[str] = None,
    channel: Optional[str] = None,
    max_age: Optional[int] = None,
    trust_min: Optional[float] = None,
    exclude_redundant: bool = False,
) -> Dict[str, Any]:
    """Build a Mongo/Atlas filter for common UI settings."""
    filters: Dict[str, Any] = {}
    if topic:
        filters = {"metadata.tags": {"$regex": topic, "$options": "i"}}
    if channel:
        if filters:
            filters = {
                "$and": [
                    filters,
                    {"metadata.channel_id": {"$regex": channel, "$options": "i"}},
                ]
            }
        else:
            filters = {"metadata.channel_id": {"$regex": channel, "$options": "i"}}
    if isinstance(max_age, int) and max_age > 0 and max_age < 10000:
        age_filter = {"metadata.age_days": {"$lte": max_age}}
        filters = {"$and": [filters, age_filter]} if filters else age_filter
    if isinstance(trust_min, (int, float)) and trust_min > 0:
        trust_filter = {"trust_score": {"$gte": float(trust_min)}}
        filters = {"$and": [filters, trust_filter]} if filters else trust_filter
    if exclude_redundant:
        red_filter = {"is_redundant": {"$ne": True}}
        filters = {"$and": [filters, red_filter]} if filters else red_filter
    return filters
