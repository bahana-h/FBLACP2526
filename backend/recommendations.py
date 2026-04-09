
from typing import List, Dict, Set
from .models import Business, BusinessBoost


def get_personalized_recommendations(username: str, business_boost: BusinessBoost, limit: int = 10) -> List[Business]:
    user_favorites = business_boost.get_favorites(username)
    
    if not user_favorites:
        return get_trending_businesses(business_boost, limit)
    
    category_preferences: Dict[str, int] = {}
    for fav in user_favorites:
        category = fav.category
        category_preferences[category] = category_preferences.get(category, 0) + 1
    
    if category_preferences:
        preferred_category = max(category_preferences, key=category_preferences.get)
    else:
        preferred_category = None
    
    scored_businesses: List[tuple] = []
    favorite_ids = {fav.id for fav in user_favorites}
    
    for business in business_boost.businesses:
        if business.id in favorite_ids:
            continue
        
        score = 0.0
        
        if preferred_category and business.category == preferred_category:
            score += 10.0
        
        avg_rating = business.get_average_rating()
        score += avg_rating * 2.0
        
        review_count = business.get_review_count()
        score += min(review_count * 0.5, 5.0)  # Cap at 5 points
        
        if business.deals:
            score += 1.0
        
        scored_businesses.append((score, business))
    
    scored_businesses.sort(key=lambda x: x[0], reverse=True)
    return [business for _, business in scored_businesses[:limit]]


def get_trending_businesses(business_boost: BusinessBoost, limit: int = 10) -> List[Business]:
    from datetime import datetime, timedelta
    
    scored_businesses: List[tuple] = []
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    for business in business_boost.businesses:
        if not business.reviews:
            continue
        
        score = 0.0
        
        avg_rating = business.get_average_rating()
        score += avg_rating * 3.0
        
        recent_reviews = 0
        for review in business.reviews:
            try:
                review_date = datetime.fromisoformat(review.get('date', ''))
                if review_date >= thirty_days_ago:
                    recent_reviews += 1
            except (ValueError, TypeError):
                pass
        
        score += recent_reviews * 2.0
        
        review_count = business.get_review_count()
        score += min(review_count * 0.3, 3.0)
        
        scored_businesses.append((score, business))
    
    scored_businesses.sort(key=lambda x: x[0], reverse=True)
    return [business for _, business in scored_businesses[:limit]]


def get_similar_businesses(business: Business, business_boost: BusinessBoost, limit: int = 5) -> List[Business]:
    scored_businesses: List[tuple] = []
    
    for other in business_boost.businesses:
        if other.id == business.id:
            continue
        
        score = 0.0
        
        if other.category == business.category:
            score += 20.0
        
        rating_diff = abs(other.get_average_rating() - business.get_average_rating())
        score += max(0, 10.0 - rating_diff * 2)
        
        review_diff = abs(other.get_review_count() - business.get_review_count())
        score += max(0, 5.0 - review_diff * 0.1)
        
        scored_businesses.append((score, other))
    
    scored_businesses.sort(key=lambda x: x[0], reverse=True)
    return [b for _, b in scored_businesses[:limit]]


def smart_filter(businesses: List[Business], filters: Dict) -> List[Business]:
    filtered = businesses
    
    if filters.get('search'):
        search_term = filters['search'].lower()
        filtered = [
            b for b in filtered
            if (search_term in b.name.lower() or
                search_term in b.description.lower() or
                search_term in b.address.lower() or
                search_term in b.category.lower())
        ]
    
    if filters.get('categories'):
        categories = [c.lower() for c in filters['categories']]
        filtered = [b for b in filtered if b.category.lower() in categories]
    
    if filters.get('min_rating') is not None:
        min_rating = float(filters['min_rating'])
        filtered = [b for b in filtered if b.get_average_rating() >= min_rating]
    
    if filters.get('min_reviews') is not None:
        min_reviews = int(filters['min_reviews'])
        filtered = [b for b in filtered if b.get_review_count() >= min_reviews]
    
    if filters.get('has_deals'):
        filtered = [b for b in filtered if b.deals]
    
    if filters.get('location'):
        location_term = filters['location'].lower()
        filtered = [
            b for b in filtered
            if location_term in b.address.lower()
        ]
    
    return filtered
