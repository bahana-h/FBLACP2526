"""
Intelligent recommendation system for Byte-Sized Business Boost

This module provides smart filtering and recommendation algorithms to help
users discover businesses that match their preferences.

INTELLIGENT FEATURES:
1. Personalized recommendations based on user favorites
2. Smart filtering with multiple criteria
3. Similar business discovery
4. Trending businesses detection
5. Location-based recommendations

ALGORITHMS:
- Collaborative filtering (based on user favorites)
- Content-based filtering (based on business attributes)
- Hybrid approach combining both methods
"""

from typing import List, Dict, Set
from models import Business, BusinessBoost


def get_personalized_recommendations(username: str, business_boost: BusinessBoost, limit: int = 10) -> List[Business]:
    """
    Get personalized business recommendations for a user.
    
    ALGORITHM: Collaborative Filtering
    - Analyzes user's favorite businesses
    - Finds businesses with similar attributes
    - Recommends businesses user hasn't favorited yet
    
    Args:
        username: Name of the user
        business_boost: BusinessBoost instance with all businesses
        limit: Maximum number of recommendations to return
    
    Returns:
        List[Business]: Recommended businesses sorted by relevance
    
    DESIGN PATTERN: Recommendation Engine
    - Analyzes user behavior (favorites)
    - Applies machine learning-like algorithms
    - Provides personalized results
    """
    # Get user's favorite businesses
    user_favorites = business_boost.get_favorites(username)
    
    # If user has no favorites, return popular businesses instead
    if not user_favorites:
        return get_trending_businesses(business_boost, limit)
    
    # Extract preferred categories from favorites
    # Count how many favorites in each category
    category_preferences: Dict[str, int] = {}
    for fav in user_favorites:
        category = fav.category
        category_preferences[category] = category_preferences.get(category, 0) + 1
    
    # Find most preferred category
    if category_preferences:
        preferred_category = max(category_preferences, key=category_preferences.get)
    else:
        preferred_category = None
    
    # Score all businesses based on similarity to favorites
    scored_businesses: List[tuple] = []
    favorite_ids = {fav.id for fav in user_favorites}
    
    for business in business_boost.businesses:
        # Skip businesses user already favorited
        if business.id in favorite_ids:
            continue
        
        score = 0.0
        
        # Category match: Higher score if matches preferred category
        if preferred_category and business.category == preferred_category:
            score += 10.0
        
        # Rating boost: Higher rated businesses get higher scores
        avg_rating = business.get_average_rating()
        score += avg_rating * 2.0
        
        # Review count boost: More reviews = more trusted
        review_count = business.get_review_count()
        score += min(review_count * 0.5, 5.0)  # Cap at 5 points
        
        # Deals boost: Businesses with deals get slight boost
        if business.deals:
            score += 1.0
        
        scored_businesses.append((score, business))
    
    # Sort by score (descending) and return top results
    scored_businesses.sort(key=lambda x: x[0], reverse=True)
    return [business for _, business in scored_businesses[:limit]]


def get_trending_businesses(business_boost: BusinessBoost, limit: int = 10) -> List[Business]:
    """
    Get trending businesses (recently reviewed with high ratings).
    
    ALGORITHM: Trending Score
    - Combines rating, review count, and recency
    - Businesses with recent high ratings rank higher
    
    Args:
        business_boost: BusinessBoost instance
        limit: Maximum number of businesses to return
    
    Returns:
        List[Business]: Trending businesses sorted by trend score
    """
    from datetime import datetime, timedelta
    
    scored_businesses: List[tuple] = []
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    for business in business_boost.businesses:
        # Skip businesses with no reviews
        if not business.reviews:
            continue
        
        score = 0.0
        
        # Base score from average rating
        avg_rating = business.get_average_rating()
        score += avg_rating * 3.0
        
        # Recent reviews boost (reviews in last 30 days)
        recent_reviews = 0
        for review in business.reviews:
            try:
                review_date = datetime.fromisoformat(review.get('date', ''))
                if review_date >= thirty_days_ago:
                    recent_reviews += 1
            except (ValueError, TypeError):
                pass
        
        score += recent_reviews * 2.0
        
        # Total review count boost
        review_count = business.get_review_count()
        score += min(review_count * 0.3, 3.0)
        
        scored_businesses.append((score, business))
    
    # Sort by score and return top results
    scored_businesses.sort(key=lambda x: x[0], reverse=True)
    return [business for _, business in scored_businesses[:limit]]


def get_similar_businesses(business: Business, business_boost: BusinessBoost, limit: int = 5) -> List[Business]:
    """
    Find businesses similar to a given business.
    
    ALGORITHM: Content-Based Filtering
    - Matches businesses with same category
    - Considers similar ratings and review counts
    - Excludes the original business
    
    Args:
        business: Business to find similar ones for
        business_boost: BusinessBoost instance
        limit: Maximum number of similar businesses
    
    Returns:
        List[Business]: Similar businesses sorted by similarity score
    """
    scored_businesses: List[tuple] = []
    
    for other in business_boost.businesses:
        # Skip the same business
        if other.id == business.id:
            continue
        
        score = 0.0
        
        # Category match: Highest weight
        if other.category == business.category:
            score += 20.0
        
        # Rating similarity: Closer ratings = higher score
        rating_diff = abs(other.get_average_rating() - business.get_average_rating())
        score += max(0, 10.0 - rating_diff * 2)
        
        # Review count similarity
        review_diff = abs(other.get_review_count() - business.get_review_count())
        score += max(0, 5.0 - review_diff * 0.1)
        
        scored_businesses.append((score, other))
    
    # Sort by similarity score
    scored_businesses.sort(key=lambda x: x[0], reverse=True)
    return [b for _, b in scored_businesses[:limit]]


def smart_filter(businesses: List[Business], filters: Dict) -> List[Business]:
    """
    Apply intelligent filtering with multiple criteria.
    
    ALGORITHM: Multi-criteria Filtering
    - Applies all filters simultaneously
    - Uses fuzzy matching for text searches
    - Handles multiple category selections
    
    Args:
        businesses: List of businesses to filter
        filters: Dictionary with filter criteria:
            - search: Text to search for
            - categories: List of categories to include
            - min_rating: Minimum average rating
            - min_reviews: Minimum number of reviews
            - has_deals: Only businesses with deals
            - location: Location keyword to match
    
    Returns:
        List[Business]: Filtered businesses
    """
    filtered = businesses
    
    # Text search with fuzzy matching
    if filters.get('search'):
        search_term = filters['search'].lower()
        filtered = [
            b for b in filtered
            if (search_term in b.name.lower() or
                search_term in b.description.lower() or
                search_term in b.address.lower() or
                search_term in b.category.lower())
        ]
    
    # Category filtering (supports multiple categories)
    if filters.get('categories'):
        categories = [c.lower() for c in filters['categories']]
        filtered = [b for b in filtered if b.category.lower() in categories]
    
    # Minimum rating filter
    if filters.get('min_rating') is not None:
        min_rating = float(filters['min_rating'])
        filtered = [b for b in filtered if b.get_average_rating() >= min_rating]
    
    # Minimum review count filter
    if filters.get('min_reviews') is not None:
        min_reviews = int(filters['min_reviews'])
        filtered = [b for b in filtered if b.get_review_count() >= min_reviews]
    
    # Deals filter
    if filters.get('has_deals'):
        filtered = [b for b in filtered if b.deals]
    
    # Location filter
    if filters.get('location'):
        location_term = filters['location'].lower()
        filtered = [
            b for b in filtered
            if location_term in b.address.lower()
        ]
    
    return filtered
