#!/usr/bin/env python3
"""
Chrysalis Connect - Web Application

A Flask-based web application for discovering and supporting local businesses.
This application demonstrates modern web development practices including:
- RESTful API design
- Input validation (syntactical and semantic)
- Intelligent recommendation algorithms
- Session management
- Error handling
- Security best practices

ARCHITECTURE:
- MVC (Model-View-Controller) pattern
- Models: Business, BusinessBoost (in models.py)
- Views: Jinja2 templates (in templates/)
- Controller: Flask routes (this file)

TECHNOLOGY STACK:
- Backend: Python 3.6+ with Flask framework
- Data Storage: JSON file-based (no database required)
- Frontend: HTML5, CSS3, JavaScript
- API Integration: Foursquare Places API (optional)

SECURITY FEATURES:
- Bot verification (math CAPTCHA)
- Input validation and sanitization
- Session-based user management
- API key protection (server-side only)
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import os
import random
import requests

# Import business models and utilities
from models import Business, BusinessBoost
from validators import (
    validate_business_name, validate_category, validate_address,
    validate_phone, validate_rating, validate_comment, validate_username,
    validate_deal_title, validate_date, validate_verification_answer
)
from recommendations import (
    get_personalized_recommendations, get_trending_businesses,
    get_similar_businesses, smart_filter
)

# Initialize Flask application
# Flask is a lightweight web framework - perfect for this use case
# It provides routing, templating, and session management out of the box
app = Flask(__name__)

# Generate secret key for session management
# Sessions use cookies signed with this key to prevent tampering
# os.urandom(24).hex() generates a cryptographically secure random key
# In production, this should be set as an environment variable
app.secret_key = os.urandom(24).hex()

# Initialize the business data management system
# BusinessBoost handles all business data operations
# It loads data from JSON file on startup
business_boost = BusinessBoost()

# Foursquare API key for location-based business search
# Loaded from environment variable for security
# NEVER hard-code API keys in source code
# Set with: export FOURSQUARE_API_KEY="your_key_here"
FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY")

# =============================================================================
# Shared Reviews API (for GitHub Pages static site)
# =============================================================================
#
# GitHub Pages is static hosting only, so it cannot share data between users.
# To support "shared reviews", we expose a tiny JSON API here and enable CORS
# so the static site can read/write reviews to this server.
#
# PERSISTENCE (lasting reviews):
# - Set SUPABASE_URL and SUPABASE_KEY (or SUPABASE_ANON_KEY) to store reviews in Supabase.
# - Deploy the Flask app to Render (or similar); without a DB, the filesystem is ephemeral.
#
# DATA MODEL:
# - Supabase table "reviews" or file shared_reviews.json:
#     business_id -> [ {user_name, rating, comment, verified, date}, ... ]
#
from reviews_store import (
    get_reviews,
    get_reviews_bulk,
    add_review as store_add_review,
    is_supabase_configured,
)


def _corsify(response):
    """
    Add CORS headers so GitHub Pages can call this API from a different origin.

    SECURITY TRADEOFF:
    - We allow any origin ("*") for simplicity in a school project/demo.
    - For production, lock this down to your exact site origin, e.g.:
      https://bahana-h.github.io
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route('/')
def index():
    """
    Landing page route (Chrysalis Connect).

    UX GOAL:
    - Provide a visually engaging first impression (3D chrysalis → butterfly)
    - Explain the product in one screen
    - Offer clear calls-to-action into the app
    
    QUERY PARAMETERS:
    - category: Filter by business category (food/retail/services)
    - sort: Sort order (name/rating/reviews)
    - search: Text search query
    
    USER EXPERIENCE DESIGN:
    - Shows all businesses by default (no overwhelming empty state)
    - Provides multiple ways to filter (category dropdown, search bar)
    - Multiple sorting options for different use cases
    - Maintains filter state in URL (shareable links)
    
    Returns:
        Rendered HTML template with business listings
    """
    username = session.get('username', '')
    return render_template("landing.html", username=username)


@app.route('/directory')
def directory():
    """
    Directory page route - displays all businesses with filtering and sorting.
    """
    # Extract query parameters from URL
    # Query parameters allow for shareable, bookmarkable filtered views
    
    category = request.args.get('category', '').strip()
    sort_by = request.args.get('sort', 'name').strip()
    search = request.args.get('search', '').strip()

    # Start with all businesses
    # List data structure maintains order and allows filtering
    businesses = business_boost.businesses

    # Apply category filter if specified
    # Filtering reduces dataset size for better performance
    if category:
        # Input validation: Ensure category is valid
        is_valid, error = validate_category(category)
        if is_valid:
            businesses = business_boost.get_businesses_by_category(category)
        else:
            # Invalid category - ignore filter and show all
            flash(f'Invalid category filter: {error}', 'warning')

    # Apply text search filter
    # Case-insensitive search across multiple fields
    if search:
        # Input validation: Check search length
        if len(search) > 100:
            flash('Search query is too long (maximum 100 characters).', 'warning')
            search = search[:100]

        # Perform case-insensitive search
        # Searches name, category, address, and description for comprehensive results
        search_lower = search.lower()
        businesses = [
            b for b in businesses
            if (search_lower in b.name.lower()
                or search_lower in b.category.lower()
                or search_lower in b.address.lower()
                or search_lower in (b.description or '').lower())
        ]

    # Apply sorting
    # Different sort orders serve different user needs
    if sort_by == 'rating':
        # Sort by average rating (highest first)
        # Businesses with reviews appear first, then businesses without reviews
        businesses = sorted(businesses, key=lambda b: b.get_average_rating(), reverse=True)
        businesses = [b for b in businesses if b.get_review_count() > 0] + \
                     [b for b in businesses if b.get_review_count() == 0]
    elif sort_by == 'reviews':
        # Sort by number of reviews (most reviewed first)
        # Indicates popularity and trustworthiness
        businesses = sorted(businesses, key=lambda b: b.get_review_count(), reverse=True)
    else:
        # Default: Alphabetical by name
        # Predictable ordering for users browsing
        businesses = sorted(businesses, key=lambda b: b.name)

    # When using Supabase for reviews, overlay store reviews so listing shows correct counts/ratings
    if is_supabase_configured() and businesses:
        reviews_by_id = get_reviews_bulk([b.id for b in businesses])
        for b in businesses:
            b.reviews = reviews_by_id.get(b.id, [])

    # Get all available categories for dropdown menu
    categories = business_boost.get_all_categories()

    # Get username from session for personalized features
    username = session.get('username', '')

    # Render template with all data
    return render_template(
        'index.html',
        businesses=businesses,
        categories=categories,
        current_category=category,
        current_sort=sort_by,
        search_query=search,
        username=username,
        page_title=None,
    )


@app.route('/map')
def map_view():
    """
    Interactive map showing all local businesses with coordinates.
    Uses Leaflet + OpenStreetMap. Businesses without lat/lng are excluded.
    """
    businesses_with_coords = [
        b for b in business_boost.businesses
        if getattr(b, 'latitude', None) is not None and getattr(b, 'longitude', None) is not None
    ]
    # Build markers data for template
    markers = [
        {
            "id": b.id,
            "name": b.name,
            "address": b.address,
            "category": b.category,
            "url": url_for('business_detail', business_id=b.id),
            "lat": b.latitude,
            "lng": b.longitude,
            "rating": b.get_average_rating(),
            "review_count": b.get_review_count(),
        }
        for b in businesses_with_coords
    ]
    username = session.get('username', '')
    return render_template('map.html', markers=markers, username=username)


@app.route('/business/<business_id>')
def business_detail(business_id):
    """
    Display detailed view of a single business.
    
    ROUTE PARAMETER:
    - business_id: Unique identifier of the business
    
    ERROR HANDLING:
    - Returns 404 redirect if business not found
    - Prevents information disclosure about non-existent businesses
    
    USER EXPERIENCE:
    - Shows complete business information
    - Displays all reviews and ratings
    - Provides options to favorite or review
    - Shows similar businesses for discovery
    
    Args:
        business_id: Unique business identifier from URL
    
    Returns:
        Rendered HTML template with business details
    """
    # Find business by ID
    # Returns None if not found (handled below)
    business = business_boost.find_business_by_id(business_id)
    
    # Error handling: Business not found
    # Redirect to home page with error message
    # Prevents showing broken page
    if not business:
        flash('Business not found.', 'error')
        return redirect(url_for('index'))
    
    # Get username from session
    username = session.get('username', '')
    
    # Check if business is in user's favorites
    # Dictionary lookup is O(1) - efficient for checking membership
    is_favorite = False
    if username and business_id in business_boost.user_favorites.get(username, []):
        is_favorite = True
    
    # Get similar businesses for discovery
    # Intelligent feature: Helps users find related businesses
    similar_businesses = get_similar_businesses(business, business_boost, limit=3)

    # Reviews: use persistent store (Supabase) when configured, else in-memory from business_data.json
    if is_supabase_configured():
        business.reviews = get_reviews(business_id)

    # Render detail template
    return render_template('business_detail.html', 
                         business=business, 
                         username=username,
                         is_favorite=is_favorite,
                         similar_businesses=similar_businesses)


@app.route('/favorites')
def favorites():
    """
    Display user's favorite businesses.
    
    AUTHENTICATION:
    - Requires username in session
    - Redirects to home if not logged in
    
    USER EXPERIENCE:
    - Personal collection of saved businesses
    - Quick access to frequently visited businesses
    - Can remove favorites directly from this page
    
    Returns:
        Rendered HTML template with user's favorites
    """
    # Get username from session
    username = session.get('username')
    
    # Authentication check: Require username
    # Prevents unauthorized access to favorites
    if not username:
        flash('Please enter your name to view favorites.', 'info')
        return redirect(url_for('index'))
    
    # Get user's favorite businesses
    # Returns empty list if user has no favorites
    favorites_list = business_boost.get_favorites(username)
    
    # Render favorites template
    return render_template('favorites.html', 
                         businesses=favorites_list, 
                         username=username)


@app.route('/recommendations')
def recommendations():
    """
    Display personalized business recommendations.
    
    INTELLIGENT FEATURE: Personalized Recommendations
    - Analyzes user's favorite businesses
    - Recommends similar businesses user hasn't favorited
    - Uses collaborative filtering algorithm
    
    Returns:
        Rendered HTML template with recommendations
    """
    username = session.get('username', '')
    
    if not username:
        # If no username, show trending businesses instead
        recommended = get_trending_businesses(business_boost, limit=20)
        page_title = 'Trending Businesses'
    else:
        # Get personalized recommendations
        recommended = get_personalized_recommendations(username, business_boost, limit=20)
        page_title = 'Recommended for You'
    
    categories = business_boost.get_all_categories()
    
    return render_template('index.html',
                         businesses=recommended,
                         categories=categories,
                         current_category='',
                         current_sort='name',
                         search_query='',
                         username=username,
                         page_title=page_title)


@app.route('/add_business', methods=['GET', 'POST'])
def add_business():
    """
    Add a new business to the directory.
    
    SECURITY FEATURES:
    - Bot verification (math CAPTCHA)
    - Comprehensive input validation
    - Prevents duplicate submissions
    
    VALIDATION:
    - Syntactical: Format checking (length, type)
    - Semantic: Meaning checking (valid category, reasonable address)
    
    USER EXPERIENCE:
    - Clear form with helpful labels
    - Real-time validation feedback
    - Success confirmation after submission
    
    Returns:
        GET: Form for adding business
        POST: Redirects to home page after successful addition
    """
    if request.method == 'POST':
        # SECURITY: Bot verification check
        # Prevents automated spam submissions
        if 'verification_answer' not in session:
            flash('Please complete verification first.', 'error')
            return redirect(url_for('add_business'))
        
        # Get and validate verification answer
        user_answer = request.form.get('verification_answer', '').strip()
        correct_answer = session.get('verification_answer')
        
        # Input validation: Verify CAPTCHA answer
        is_valid, error = validate_verification_answer(user_answer, correct_answer)
        if not is_valid:
            flash(error or 'Verification failed. Please try again.', 'error')
            session.pop('verification_answer', None)
            return redirect(url_for('add_business'))
        
        # Clear verification after successful check
        # Prevents reuse of verification answer
        session.pop('verification_answer', None)
        
        # Extract and validate form data
        # .strip() removes leading/trailing whitespace
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        description = request.form.get('description', '').strip()
        
        # COMPREHENSIVE INPUT VALIDATION
        # Syntactical validation: Check format and length
        # Semantic validation: Check meaning and validity
        
        # Validate business name
        is_valid, error = validate_business_name(name)
        if not is_valid:
            flash(f'Business name: {error}', 'error')
            return redirect(url_for('add_business'))
        
        # Validate category
        is_valid, error = validate_category(category)
        if not is_valid:
            flash(f'Category: {error}', 'error')
            return redirect(url_for('add_business'))
        
        # Validate address
        is_valid, error = validate_address(address)
        if not is_valid:
            flash(f'Address: {error}', 'error')
            return redirect(url_for('add_business'))
        
        # Validate phone (optional field)
        if phone:
            is_valid, error = validate_phone(phone)
            if not is_valid:
                flash(f'Phone: {error}', 'error')
                return redirect(url_for('add_business'))
        
        # Handle optional deals
        deals = []
        deal_title = request.form.get('deal_title', '').strip()
        deal_desc = request.form.get('deal_description', '').strip()
        deal_expires = request.form.get('deal_expires', '').strip()
        
        # Validate deal if provided
        if deal_title:
            is_valid, error = validate_deal_title(deal_title)
            if not is_valid:
                flash(f'Deal title: {error}', 'error')
                return redirect(url_for('add_business'))
            
            # Validate expiration date if provided
            if deal_expires:
                is_valid, error = validate_date(deal_expires, allow_past=False)
                if not is_valid:
                    flash(f'Deal expiration: {error}', 'error')
                    return redirect(url_for('add_business'))
            
            deals.append({
                "title": deal_title,
                "description": deal_desc,
                "expires": deal_expires
            })
        
        # Add business to system
        # BusinessBoost handles ID generation and persistence
        if business_boost.add_business(name, category, address, phone, description, deals):
            flash(f'Business "{name}" added successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Failed to add business. Please try again.', 'error')
    
    # GET request: Show form
    # Generate new verification question for bot prevention
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    session['verification_answer'] = num1 + num2
    session['verification_question'] = f"{num1} + {num2}"
    
    # Get categories for dropdown
    categories = business_boost.get_all_categories()
    username = session.get('username', '')
    
    # Render form template
    return render_template('add_business.html', 
                         verification_question=session['verification_question'],
                         categories=categories,
                         username=username)


@app.route('/add_review', methods=['POST'])
def add_review():
    """
    Add a review to a business.
    
    VALIDATION:
    - Rating must be 1-5 (semantic validation)
    - Comment must meet length requirements
    - Bot verification required
    
    SECURITY:
    - Prevents spam reviews with CAPTCHA
    - Validates all inputs before processing
    
    Args:
        business_id: ID of business being reviewed (from form)
        user_name: Name of reviewer (from form)
        rating: Rating value 1-5 (from form)
        comment: Review text (from form)
        verification_answer: CAPTCHA answer (from form)
    
    Returns:
        Redirects to business detail page with success/error message
    """
    # Extract form data
    business_id = request.form.get('business_id')
    user_name = request.form.get('user_name', '').strip()
    rating = request.form.get('rating')
    comment = request.form.get('comment', '').strip()
    
    # Input validation: Username required
    is_valid, error = validate_username(user_name)
    if not is_valid:
        flash(error or 'Please enter your name.', 'error')
        return redirect(url_for('business_detail', business_id=business_id))
    
    # SECURITY: Bot verification check
    if 'review_verification_answer' not in session:
        flash('Please complete verification first.', 'error')
        return redirect(url_for('business_detail', business_id=business_id))
    
    # Validate verification answer
    correct_answer = session.get('review_verification_answer')
    user_answer = request.form.get('verification_answer', '').strip()
    is_valid, error = validate_verification_answer(user_answer, correct_answer)
    if not is_valid:
        flash(error or 'Verification failed. Please try again.', 'error')
        session.pop('review_verification_answer', None)
        return redirect(url_for('business_detail', business_id=business_id))
    
    # Clear verification after successful check
    session.pop('review_verification_answer', None)
    
    # Validate rating (semantic validation: must be 1-5)
    is_valid, rating_int, error = validate_rating(rating)
    if not is_valid:
        flash(error or 'Invalid rating.', 'error')
        return redirect(url_for('business_detail', business_id=business_id))
    
    # Validate comment (syntactical: length, semantic: meaningful content)
    is_valid, error = validate_comment(comment)
    if not is_valid:
        flash(error or 'Comment is required and must be meaningful.', 'error')
        return redirect(url_for('business_detail', business_id=business_id))
    
    # Add review: use persistent store (Supabase) when configured, else BusinessBoost (file)
    try:
        if is_supabase_configured():
            store_add_review(business_id, user_name, rating_int, comment, verified=True)
            flash('Review added successfully!', 'success')
        elif business_boost.add_review(business_id, user_name, rating_int, comment):
            flash('Review added successfully!', 'success')
        else:
            flash('Failed to add review. Business may not exist.', 'error')
    except Exception as e:
        # Error handling: Catch unexpected errors
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('business_detail', business_id=business_id))


@app.route('/toggle_favorite', methods=['POST'])
def toggle_favorite():
    """
    Add or remove a business from user's favorites.
    
    USER EXPERIENCE:
    - One-click favorite/unfavorite
    - Immediate visual feedback
    - Persists across sessions
    
    SECURITY:
    - Requires username in session
    - Validates business_id exists
    
    Returns:
        Redirects back to referring page
    """
    # Authentication check
    username = session.get('username')
    if not username:
        flash('Please enter your name first.', 'info')
        return redirect(url_for('index'))
    
    # Get business ID and action from form
    business_id = request.form.get('business_id')
    action = request.form.get('action', 'add')
    
    # Validate business exists
    business = business_boost.find_business_by_id(business_id)
    if not business:
        flash('Business not found.', 'error')
        return redirect(request.referrer or url_for('index'))
    
    # Perform favorite/unfavorite action
    if action == 'add':
        business_boost.add_to_favorites(username, business_id)
        flash('Business added to favorites!', 'success')
    else:
        business_boost.remove_from_favorites(username, business_id)
        flash('Business removed from favorites.', 'info')
    
    # Redirect back to referring page
    # request.referrer gets the page user came from
    return redirect(request.referrer or url_for('index'))


@app.route('/set_username', methods=['POST'])
def set_username():
    """
    Set username in session for personalization.
    
    VALIDATION:
    - Username format validation
    - Length constraints
    
    USER EXPERIENCE:
    - Simple one-field form
    - Immediate session activation
    - Welcome message confirmation
    
    Returns:
        Redirects back to referring page
    """
    # Get username from form
    username = request.form.get('username', '').strip()
    
    # Validate username
    is_valid, error = validate_username(username)
    if is_valid:
        # Store in session
        # Session persists across requests via signed cookies
        session['username'] = username
        flash(f'Welcome, {username}!', 'success')
    else:
        flash(error or 'Invalid username.', 'error')
    
    # Redirect back to referring page
    return redirect(request.referrer or url_for('index'))


@app.route('/get_verification', methods=['GET'])
def get_verification():
    """
    API endpoint to get a new verification question.
    
    USE CASE: AJAX requests for dynamic CAPTCHA
    - Frontend can request new question without page reload
    - Returns JSON for easy JavaScript consumption
    
    SECURITY:
    - Generates random math problem
    - Stores answer in server session (not exposed to client)
    
    Returns:
        JSON with verification question
    """
    # Generate random math problem
    # Random numbers prevent predictable answers
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    
    # Store answer in session
    # Session is server-side, client cannot access answer
    session['review_verification_answer'] = num1 + num2
    
    # Return question as JSON
    # JSON format is easy for JavaScript to parse
    return jsonify({
        'question': f"{num1} + {num2}",
        'answer': session['review_verification_answer']  # For testing only - remove in production
    })


@app.route('/top-rated')
def top_rated():
    """
    Display top-rated businesses.
    
    FILTERING LOGIC:
    - Only shows businesses with at least one review
    - Sorted by average rating (highest first)
    
    USER EXPERIENCE:
    - Quick access to best businesses
    - Helps users find quality establishments
    
    Returns:
        Rendered HTML template with top-rated businesses
    """
    # Get all businesses sorted by rating
    businesses = business_boost.sort_businesses_by_rating()
    
    # Filter out businesses with no reviews
    # Only businesses with reviews can have meaningful ratings
    businesses = [b for b in businesses if b.get_review_count() > 0]
    
    categories = business_boost.get_all_categories()
    username = session.get('username', '')
    
    return render_template('index.html', 
                         businesses=businesses, 
                         categories=categories,
                         current_category='',
                         current_sort='rating',
                         search_query='',
                         username=username,
                         page_title='Top Rated Businesses')


@app.route('/most-reviewed')
def most_reviewed():
    """
    Display most-reviewed businesses.
    
    USE CASE: Find popular businesses
    - High review count indicates popularity
    - Helps users discover well-known establishments
    
    Returns:
        Rendered HTML template with most-reviewed businesses
    """
    # Sort by review count (descending)
    businesses = business_boost.sort_businesses_by_review_count()
    
    categories = business_boost.get_all_categories()
    username = session.get('username', '')
    
    return render_template('index.html', 
                         businesses=businesses, 
                         categories=categories,
                         current_category='',
                         current_sort='reviews',
                         search_query='',
                         username=username,
                         page_title='Most Reviewed Businesses')


@app.route('/category/<category_name>')
def category_view(category_name):
    """
    Display businesses in a specific category.
    
    ROUTE PARAMETER:
    - category_name: Category to filter by (food/retail/services)
    
    VALIDATION:
    - Validates category exists
    - Handles invalid categories gracefully
    
    Returns:
        Rendered HTML template with filtered businesses
    """
    # Validate category
    is_valid, error = validate_category(category_name)
    if not is_valid:
        flash(f'Invalid category: {error}', 'error')
        return redirect(url_for('index'))
    
    # Get businesses in category
    businesses = business_boost.get_businesses_by_category(category_name)
    
    categories = business_boost.get_all_categories()
    username = session.get('username', '')
    
    return render_template('index.html', 
                         businesses=businesses, 
                         categories=categories,
                         current_category=category_name,
                         current_sort='name',
                         search_query='',
                         username=username,
                         page_title=f'{category_name.title()} Businesses')


@app.route('/api/foursquare/places')
def foursquare_places():
    """
    Proxy endpoint for Foursquare Places API.
    
    SECURITY DESIGN:
    - Keeps API key on server (never exposed to browser)
    - Prevents API key theft from client-side code
    - Validates all inputs before making API call
    
    ARCHITECTURE PATTERN: API Gateway/Proxy
    - Centralizes external API access
    - Allows for caching, rate limiting, error handling
    - Simplifies frontend code (no API key needed)
    
    QUERY PARAMETERS:
    - lat: Latitude (required)
    - lon: Longitude (required)
    - q: Search query (optional, defaults to "small business")
    - category: Category filter (optional)
    - radius: Search radius in meters (optional, defaults to 2000)
    - limit: Maximum results (optional, defaults to 20)
    
    Returns:
        JSON response from Foursquare API or error message
    """
    # Check if API key is configured
    if not FOURSQUARE_API_KEY:
        return jsonify(
            {"error": "FOURSQUARE_API_KEY is not set on the server."}
        ), 500
    
    # Extract and validate query parameters
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    query = request.args.get("q", "small business")
    category = request.args.get("category")
    radius = request.args.get("radius", "2000")
    limit = request.args.get("limit", "20")
    
    # Input validation: Latitude and longitude required
    if not lat or not lon:
        return jsonify({"error": "lat and lon query parameters are required."}), 400
    
    # Input validation: Validate numeric values
    try:
        lat_float = float(lat)
        lon_float = float(lon)
        radius_int = int(radius)
        limit_int = int(limit)
        
        # Semantic validation: Valid coordinate ranges
        if not (-90 <= lat_float <= 90):
            return jsonify({"error": "Latitude must be between -90 and 90."}), 400
        if not (-180 <= lon_float <= 180):
            return jsonify({"error": "Longitude must be between -180 and 180."}), 400
        if radius_int < 100 or radius_int > 50000:
            return jsonify({"error": "Radius must be between 100 and 50000 meters."}), 400
        if limit_int < 1 or limit_int > 50:
            return jsonify({"error": "Limit must be between 1 and 50."}), 400
    except ValueError:
        return jsonify({"error": "Invalid numeric parameter format."}), 400
    
    # Build API request parameters
    params = {
        "ll": f"{lat_float},{lon_float}",
        "radius": str(radius_int),
        "limit": str(limit_int),
        "query": query,
    }
    
    # Add category filter if provided
    if category:
        params["categories"] = category
    
    # Make API request with error handling
    try:
        resp = requests.get(
            "https://api.foursquare.com/v3/places/search",
            headers={"Authorization": FOURSQUARE_API_KEY},
            params=params,
            timeout=10,  # Prevent hanging requests
        )
        # Raise exception for HTTP errors (4xx, 5xx)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        return jsonify({"error": "Foursquare API request timed out."}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Foursquare request failed: {str(e)}"}), 502
    
    # Parse and return JSON response
    data = resp.json()
    return jsonify(data)


@app.route("/api/health", methods=["GET"])
def api_health():
    """Simple health check endpoint for the static site."""
    resp = jsonify({"ok": True, "service": "chrysalis-connect-backend"})
    return _corsify(resp)


@app.route("/api/shared-reviews/bulk", methods=["POST", "OPTIONS"])
def shared_reviews_bulk():
    """
    Fetch shared reviews for many business IDs in one request.

    Request JSON:
      { "business_ids": ["id1", "id2", ...] }

    Response JSON:
      { "reviews_by_id": { "id1": [...], "id2": [...] } }
    """
    if request.method == "OPTIONS":
        return _corsify(jsonify({"ok": True}))

    payload = request.get_json(silent=True) or {}
    business_ids = payload.get("business_ids", [])
    if not isinstance(business_ids, list) or not all(isinstance(x, str) for x in business_ids):
        return _corsify(jsonify({"error": "business_ids must be a list of strings."})), 400

    out = get_reviews_bulk(business_ids)
    return _corsify(jsonify({"reviews_by_id": out}))


@app.route("/api/shared-reviews", methods=["POST", "OPTIONS"])
def shared_reviews_add():
    """
    Add a shared review for an external business ID.

    Request JSON:
      {
        "business_id": "external-id",
        "user_name": "Hannah",
        "rating": 5,
        "comment": "Great!",
        "verified": true
      }
    """
    if request.method == "OPTIONS":
        return _corsify(jsonify({"ok": True}))

    payload = request.get_json(silent=True) or {}
    business_id = payload.get("business_id")
    user_name = (payload.get("user_name") or "").strip()
    rating = payload.get("rating")
    comment = (payload.get("comment") or "").strip()
    verified = bool(payload.get("verified", True))

    # Syntactical + semantic validation using existing validators.
    if not business_id or not isinstance(business_id, str):
        return _corsify(jsonify({"error": "business_id is required."})), 400

    is_valid, err = validate_username(user_name)
    if not is_valid:
        return _corsify(jsonify({"error": err or "Invalid user_name."})), 400

    # Accept either numeric or string rating from clients.
    try:
        rating_str = str(rating)
    except Exception:
        rating_str = ""
    ok, rating_int, err = validate_rating(rating_str)
    if not ok:
        return _corsify(jsonify({"error": err or "Invalid rating."})), 400

    is_valid, err = validate_comment(comment)
    if not is_valid:
        return _corsify(jsonify({"error": err or "Invalid comment."})), 400

    review = store_add_review(business_id, user_name, rating_int, comment, verified)
    reviews = get_reviews(business_id)
    return _corsify(jsonify({"ok": True, "review": review, "review_count": len(reviews)}))


@app.errorhandler(404)
def not_found(error):
    """
    Handle 404 Not Found errors.
    
    USER EXPERIENCE:
    - Friendly error page instead of default browser error
    - Provides navigation back to home
    
    Returns:
        Rendered 404 error page
    """
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """
    Handle 500 Internal Server errors.
    
    ERROR HANDLING:
    - Logs error for debugging
    - Shows user-friendly error message
    - Prevents sensitive error information leakage
    
    Returns:
        Rendered 500 error page
    """
    # Log error for debugging (in production, use proper logging)
    print(f"Internal error: {error}")
    return render_template('500.html'), 500


if __name__ == '__main__':
    """
    Application entry point.
    
    DEVELOPMENT MODE:
    - debug=True enables auto-reload on code changes
    - Shows detailed error pages for debugging
    - host='0.0.0.0' allows access from other devices on network
    
    PRODUCTION DEPLOYMENT:
    - Use production WSGI server (e.g., Gunicorn, uWSGI)
    - Set debug=False
    - Configure proper logging
    - Use environment variables for configuration
    """
    # Run Flask development server
    # In production, use: gunicorn app:app
    app.run(debug=True, host='0.0.0.0', port=5000)