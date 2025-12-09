#!/usr/bin/env python3
"""
Byte-Sized Business Boost - Web Application
A Flask-based web tool to discover and support small, local businesses.
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import json
import os
import random
import string
from datetime import datetime
from typing import Dict, List, Optional

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()  # Generate a secret key for sessions

# Import business models
from models import Business, BusinessBoost

# Initialize the business boost system
business_boost = BusinessBoost()


@app.route('/')
def index():
    """Home page - show all businesses."""
    category = request.args.get('category', '')
    sort_by = request.args.get('sort', 'name')
    search = request.args.get('search', '')
    
    businesses = business_boost.businesses
    
    # Filter by category
    if category:
        businesses = business_boost.get_businesses_by_category(category)
    
    # Search filter
    if search:
        search_lower = search.lower()
        businesses = [
            b for b in businesses
            if search_lower in b.name.lower() or 
               search_lower in b.category.lower() or 
               search_lower in b.address.lower()
        ]
    
    # Sort businesses
    if sort_by == 'rating':
        businesses = sorted(businesses, key=lambda b: b.get_average_rating(), reverse=True)
        businesses = [b for b in businesses if b.get_review_count() > 0] + [b for b in businesses if b.get_review_count() == 0]
    elif sort_by == 'reviews':
        businesses = sorted(businesses, key=lambda b: b.get_review_count(), reverse=True)
    else:
        businesses = sorted(businesses, key=lambda b: b.name)
    
    categories = business_boost.get_all_categories()
    username = session.get('username', '')
    
    return render_template('index.html', 
                         businesses=businesses, 
                         categories=categories,
                         current_category=category,
                         current_sort=sort_by,
                         search_query=search,
                         username=username,
                         page_title=None)


@app.route('/business/<business_id>')
def business_detail(business_id):
    """Show detailed view of a single business."""
    business = business_boost.find_business_by_id(business_id)
    if not business:
        flash('Business not found.', 'error')
        return redirect(url_for('index'))
    
    username = session.get('username', '')
    is_favorite = False
    if username and business_id in business_boost.user_favorites.get(username, []):
        is_favorite = True
    
    return render_template('business_detail.html', 
                         business=business, 
                         username=username,
                         is_favorite=is_favorite)


@app.route('/favorites')
def favorites():
    """Show user's favorite businesses."""
    username = session.get('username')
    if not username:
        flash('Please enter your name to view favorites.', 'info')
        return redirect(url_for('index'))
    
    favorites_list = business_boost.get_favorites(username)
    return render_template('favorites.html', 
                         businesses=favorites_list, 
                         username=username)


@app.route('/add_business', methods=['GET', 'POST'])
def add_business():
    """Add a new business."""
    if request.method == 'POST':
        # Get verification answer from session
        if 'verification_answer' not in session:
            flash('Please complete verification first.', 'error')
            return redirect(url_for('add_business'))
        
        user_answer = request.form.get('verification_answer', '').strip()
        if user_answer != str(session['verification_answer']):
            flash('Verification failed. Please try again.', 'error')
            session.pop('verification_answer', None)
            return redirect(url_for('add_business'))
        
        # Clear verification after successful check
        session.pop('verification_answer', None)
        
        # Get business data
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name or not category or not address:
            flash('Name, category, and address are required.', 'error')
            return redirect(url_for('add_business'))
        
        # Handle deals
        deals = []
        deal_title = request.form.get('deal_title', '').strip()
        deal_desc = request.form.get('deal_description', '').strip()
        deal_expires = request.form.get('deal_expires', '').strip()
        if deal_title:
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
    
    # Generate verification question for GET request
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
    """Add a review to a business."""
    business_id = request.form.get('business_id')
    user_name = request.form.get('user_name', '').strip()
    rating = request.form.get('rating')
    comment = request.form.get('comment', '').strip()
    
    if not user_name:
        flash('Please enter your name.', 'error')
        return redirect(url_for('business_detail', business_id=business_id))
    
    # Get verification answer from session
    if 'review_verification_answer' not in session:
        flash('Please complete verification first.', 'error')
        return redirect(url_for('business_detail', business_id=business_id))
    
    user_answer = request.form.get('verification_answer', '').strip()
    if user_answer != str(session['review_verification_answer']):
        flash('Verification failed. Please try again.', 'error')
        session.pop('review_verification_answer', None)
        return redirect(url_for('business_detail', business_id=business_id))
    
    session.pop('review_verification_answer', None)
    
    try:
        rating_int = int(rating)
        if business_boost.add_review(business_id, user_name, rating_int, comment):
            flash('Review added successfully!', 'success')
        else:
            flash('Failed to add review.', 'error')
    except ValueError:
        flash('Invalid rating.', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('business_detail', business_id=business_id))


@app.route('/toggle_favorite', methods=['POST'])
def toggle_favorite():
    """Add or remove a business from favorites."""
    username = session.get('username')
    if not username:
        flash('Please enter your name first.', 'info')
        return redirect(url_for('index'))
    
    business_id = request.form.get('business_id')
    action = request.form.get('action', 'add')
    
    if action == 'add':
        business_boost.add_to_favorites(username, business_id)
        flash('Business added to favorites!', 'success')
    else:
        business_boost.remove_from_favorites(username, business_id)
        flash('Business removed from favorites.', 'info')
    
    return redirect(request.referrer or url_for('index'))


@app.route('/set_username', methods=['POST'])
def set_username():
    """Set the username in session."""
    username = request.form.get('username', '').strip()
    if username:
        session['username'] = username
        flash(f'Welcome, {username}!', 'success')
    return redirect(request.referrer or url_for('index'))


@app.route('/get_verification', methods=['GET'])
def get_verification():
    """Get a new verification question for reviews."""
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    session['review_verification_answer'] = num1 + num2
    return jsonify({
        'question': f"{num1} + {num2}",
        'answer': session['review_verification_answer']
    })


@app.route('/top-rated')
def top_rated():
    """Show top rated businesses."""
    businesses = business_boost.sort_businesses_by_rating()
    # Filter out businesses with no reviews
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
    """Show most reviewed businesses."""
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
    """Show businesses in a specific category."""
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

