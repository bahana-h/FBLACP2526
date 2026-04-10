#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import json
import os
import random
import string
from datetime import datetime
from typing import Dict, List, Optional
import requests

from backend.models import Business, BusinessBoost
from backend.validators import (
    validate_business_name, validate_category, validate_address,
    validate_phone, validate_rating, validate_comment, validate_username,
    validate_deal_title, validate_date, validate_verification_answer
)
from backend.recommendations import (
    get_personalized_recommendations, get_trending_businesses,
    get_similar_businesses, smart_filter
)

app = Flask(__name__)

app.secret_key = os.urandom(24).hex()

business_boost = BusinessBoost()

FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY")

SHARED_REVIEWS_FILE = os.getenv("SHARED_REVIEWS_FILE", "shared_reviews.json")

def _corsify(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


def load_shared_reviews() -> Dict[str, List[Dict]]:
    if not os.path.exists(SHARED_REVIEWS_FILE):
        return {}
    try:
        with open(SHARED_REVIEWS_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_shared_reviews(data: Dict[str, List[Dict]]) -> None:
    with open(SHARED_REVIEWS_FILE, "w") as f:
        json.dump(data, f, indent=2)


@app.route('/')
def index():
    username = session.get('username', '')
    return render_template("landing.html", username=username)


@app.route('/directory')
def directory():
    category = request.args.get('category', '').strip()
    sort_by = request.args.get('sort', 'name').strip()
    search = request.args.get('search', '').strip()

    businesses = business_boost.businesses

    if category:
        is_valid, error = validate_category(category)
        if is_valid:
            businesses = business_boost.get_businesses_by_category(category)
        else:
            flash(f'Invalid category filter: {error}', 'warning')

    if search:
        if len(search) > 100:
            flash('Search query is too long (maximum 100 characters).', 'warning')
            search = search[:100]

        search_lower = search.lower()
        businesses = [
            b for b in businesses
            if (search_lower in b.name.lower()
                or search_lower in b.category.lower()
                or search_lower in b.address.lower()
                or search_lower in (b.description or '').lower())
        ]

    if sort_by == 'rating':
        businesses = sorted(businesses, key=lambda b: b.get_average_rating(), reverse=True)
        businesses = [b for b in businesses if b.get_review_count() > 0] + \
                     [b for b in businesses if b.get_review_count() == 0]
    elif sort_by == 'reviews':
        businesses = sorted(businesses, key=lambda b: b.get_review_count(), reverse=True)
    else:
        businesses = sorted(businesses, key=lambda b: b.name)

    categories = business_boost.get_all_categories()

    username = session.get('username', '')

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


@app.route('/business/<business_id>')
def business_detail(business_id):
    business = business_boost.find_business_by_id(business_id)
    
    if not business:
        flash('Business not found.', 'error')
        return redirect(url_for('index'))
    
    username = session.get('username', '')
    
    is_favorite = False
    if username and business_id in business_boost.user_favorites.get(username, []):
        is_favorite = True
    
    similar_businesses = get_similar_businesses(business, business_boost, limit=3)
    
    return render_template('business_detail.html', 
                         business=business, 
                         username=username,
                         is_favorite=is_favorite,
                         similar_businesses=similar_businesses)


@app.route('/favorites')
def favorites():
    username = session.get('username')
    
    if not username:
        flash('Please enter your name to view favorites.', 'info')
        return redirect(url_for('index'))
    
    favorites_list = business_boost.get_favorites(username)
    
    return render_template('favorites.html', 
                         businesses=favorites_list, 
                         username=username)


@app.route('/recommendations')
def recommendations():
    username = session.get('username', '')
    
    if not username:
        recommended = get_trending_businesses(business_boost, limit=20)
        page_title = 'Trending Businesses'
    else:
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
    if request.method == 'POST':
        if 'verification_answer' not in session:
            flash('Please complete verification first.', 'error')
            return redirect(url_for('add_business'))
        
        user_answer = request.form.get('verification_answer', '').strip()
        correct_answer = session.get('verification_answer')
        
        is_valid, error = validate_verification_answer(user_answer, correct_answer)
        if not is_valid:
            flash(error or 'Verification failed. Please try again.', 'error')
            session.pop('verification_answer', None)
            return redirect(url_for('add_business'))
        
        session.pop('verification_answer', None)
        
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        description = request.form.get('description', '').strip()
        
        
        is_valid, error = validate_business_name(name)
        if not is_valid:
            flash(f'Business name: {error}', 'error')
            return redirect(url_for('add_business'))
        
        is_valid, error = validate_category(category)
        if not is_valid:
            flash(f'Category: {error}', 'error')
            return redirect(url_for('add_business'))
        
        is_valid, error = validate_address(address)
        if not is_valid:
            flash(f'Address: {error}', 'error')
            return redirect(url_for('add_business'))
        
        if phone:
            is_valid, error = validate_phone(phone)
            if not is_valid:
                flash(f'Phone: {error}', 'error')
                return redirect(url_for('add_business'))
        
        deals = []
        deal_title = request.form.get('deal_title', '').strip()
        deal_desc = request.form.get('deal_description', '').strip()
        deal_expires = request.form.get('deal_expires', '').strip()
        
        if deal_title:
            is_valid, error = validate_deal_title(deal_title)
            if not is_valid:
                flash(f'Deal title: {error}', 'error')
                return redirect(url_for('add_business'))
            
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
        
        if business_boost.add_business(name, category, address, phone, description, deals):
            flash(f'Business "{name}" added successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Failed to add business. Please try again.', 'error')
    
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    session['verification_answer'] = num1 + num2
    session['verification_question'] = f"{num1} + {num2}"
    
    categories = business_boost.get_all_categories()
    username = session.get('username', '')
    
    return render_template('add_business.html', 
                         verification_question=session['verification_question'],
                         categories=categories,
                         username=username)


@app.route('/add_review', methods=['POST'])
def add_review():
    business_id = request.form.get('business_id')
    user_name = request.form.get('user_name', '').strip()
    rating = request.form.get('rating')
    comment = request.form.get('comment', '').strip()
    
    is_valid, error = validate_username(user_name)
    if not is_valid:
        flash(error or 'Please enter your name.', 'error')
        return redirect(url_for('business_detail', business_id=business_id))
    
    if 'review_verification_answer' not in session:
        flash('Please complete verification first.', 'error')
        return redirect(url_for('business_detail', business_id=business_id))
    
    correct_answer = session.get('review_verification_answer')
    user_answer = request.form.get('verification_answer', '').strip()
    is_valid, error = validate_verification_answer(user_answer, correct_answer)
    if not is_valid:
        flash(error or 'Verification failed. Please try again.', 'error')
        session.pop('review_verification_answer', None)
        return redirect(url_for('business_detail', business_id=business_id))
    
    session.pop('review_verification_answer', None)
    
    is_valid, rating_int, error = validate_rating(rating)
    if not is_valid:
        flash(error or 'Invalid rating.', 'error')
        return redirect(url_for('business_detail', business_id=business_id))
    
    is_valid, error = validate_comment(comment)
    if not is_valid:
        flash(error or 'Comment is required and must be meaningful.', 'error')
        return redirect(url_for('business_detail', business_id=business_id))
    
    try:
        if business_boost.add_review(business_id, user_name, rating_int, comment):
            flash('Review added successfully!', 'success')
        else:
            flash('Failed to add review. Business may not exist.', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('business_detail', business_id=business_id))


@app.route('/toggle_favorite', methods=['POST'])
def toggle_favorite():
    username = session.get('username')
    if not username:
        flash('Please enter your name first.', 'info')
        return redirect(url_for('index'))
    
    business_id = request.form.get('business_id')
    action = request.form.get('action', 'add')
    
    business = business_boost.find_business_by_id(business_id)
    if not business:
        flash('Business not found.', 'error')
        return redirect(request.referrer or url_for('index'))
    
    if action == 'add':
        business_boost.add_to_favorites(username, business_id)
        flash('Business added to favorites!', 'success')
    else:
        business_boost.remove_from_favorites(username, business_id)
        flash('Business removed from favorites.', 'info')
    
    return redirect(request.referrer or url_for('index'))


@app.route('/set_username', methods=['POST'])
def set_username():
    username = request.form.get('username', '').strip()
    
    is_valid, error = validate_username(username)
    if is_valid:
        session['username'] = username
        flash(f'Welcome, {username}!', 'success')
    else:
        flash(error or 'Invalid username.', 'error')
    
    return redirect(request.referrer or url_for('index'))


@app.route('/get_verification', methods=['GET'])
def get_verification():
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    
    session['review_verification_answer'] = num1 + num2
    
    return jsonify({
        'question': f"{num1} + {num2}",
        'answer': session['review_verification_answer']  # For testing only - remove in production
    })


@app.route('/top-rated')
def top_rated():
    businesses = business_boost.sort_businesses_by_rating()
    
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
    is_valid, error = validate_category(category_name)
    if not is_valid:
        flash(f'Invalid category: {error}', 'error')
        return redirect(url_for('index'))
    
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
    if not FOURSQUARE_API_KEY:
        return jsonify(
            {"error": "FOURSQUARE_API_KEY is not set on the server."}
        ), 500
    
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    query = request.args.get("q", "small business")
    category = request.args.get("category")
    radius = request.args.get("radius", "2000")
    limit = request.args.get("limit", "20")
    
    if not lat or not lon:
        return jsonify({"error": "lat and lon query parameters are required."}), 400
    
    try:
        lat_float = float(lat)
        lon_float = float(lon)
        radius_int = int(radius)
        limit_int = int(limit)
        
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
    
    params = {
        "ll": f"{lat_float},{lon_float}",
        "radius": str(radius_int),
        "limit": str(limit_int),
        "query": query,
    }
    
    if category:
        params["categories"] = category
    
    try:
        resp = requests.get(
            "https://api.foursquare.com/v3/places/search",
            headers={"Authorization": FOURSQUARE_API_KEY},
            params=params,
            timeout=10,  # Prevent hanging requests
        )
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        return jsonify({"error": "Foursquare API request timed out."}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Foursquare request failed: {str(e)}"}), 502
    
    data = resp.json()
    return jsonify(data)


@app.route("/api/health", methods=["GET"])
def api_health():
    resp = jsonify({"ok": True, "service": "chrysalis-connect-backend"})
    return _corsify(resp)


@app.route("/api/shared-reviews/bulk", methods=["POST", "OPTIONS"])
def shared_reviews_bulk():
    if request.method == "OPTIONS":
        return _corsify(jsonify({"ok": True}))

    payload = request.get_json(silent=True) or {}
    business_ids = payload.get("business_ids", [])
    if not isinstance(business_ids, list) or not all(isinstance(x, str) for x in business_ids):
        return _corsify(jsonify({"error": "business_ids must be a list of strings."})), 400

    data = load_shared_reviews()
    out = {bid: data.get(bid, []) for bid in business_ids}
    return _corsify(jsonify({"reviews_by_id": out}))


@app.route("/api/shared-reviews", methods=["POST", "OPTIONS"])
def shared_reviews_add():
    if request.method == "OPTIONS":
        return _corsify(jsonify({"ok": True}))

    payload = request.get_json(silent=True) or {}
    business_id = payload.get("business_id")
    user_name = (payload.get("user_name") or "").strip()
    rating = payload.get("rating")
    comment = (payload.get("comment") or "").strip()
    verified = bool(payload.get("verified", True))

    if not business_id or not isinstance(business_id, str):
        return _corsify(jsonify({"error": "business_id is required."})), 400

    is_valid, err = validate_username(user_name)
    if not is_valid:
        return _corsify(jsonify({"error": err or "Invalid user_name."})), 400

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

    data = load_shared_reviews()
    reviews = data.get(business_id, [])
    if not isinstance(reviews, list):
        reviews = []

    review = {
        "user_name": user_name,
        "rating": rating_int,
        "comment": comment,
        "verified": verified,
        "date": datetime.now().isoformat(),
    }
    reviews.append(review)
    data[business_id] = reviews
    save_shared_reviews(data)

    return _corsify(jsonify({"ok": True, "review": review, "review_count": len(reviews)}))


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    print(f"Internal error: {error}")
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
