"""
Business models for Byte-Sized Business Boost
"""

import json
import os
import random
import string
from datetime import datetime
from typing import Dict, List, Optional


class Business:
    """Represents a local business."""
    
    def __init__(self, name: str, category: str, address: str, phone: str = "", 
                 description: str = "", deals: List[Dict] = None):
        self.id = self._generate_id()
        self.name = name
        self.category = category.lower()
        self.address = address
        self.phone = phone
        self.description = description
        self.deals = deals or []
        self.reviews = []
        self.created_at = datetime.now().isoformat()
    
    def _generate_id(self) -> str:
        """Generate a unique ID for the business."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    def add_review(self, user_name: str, rating: int, comment: str, verified: bool = False):
        """Add a review to the business."""
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        review = {
            "user_name": user_name,
            "rating": rating,
            "comment": comment,
            "verified": verified,
            "date": datetime.now().isoformat()
        }
        self.reviews.append(review)
    
    def get_average_rating(self) -> float:
        """Calculate average rating from all reviews."""
        if not self.reviews:
            return 0.0
        return sum(r["rating"] for r in self.reviews) / len(self.reviews)
    
    def get_review_count(self) -> int:
        """Get total number of reviews."""
        return len(self.reviews)
    
    def to_dict(self) -> Dict:
        """Convert business to dictionary for JSON storage."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "address": self.address,
            "phone": self.phone,
            "description": self.description,
            "deals": self.deals,
            "reviews": self.reviews,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Business':
        """Create a Business instance from dictionary."""
        business = cls(
            name=data["name"],
            category=data["category"],
            address=data["address"],
            phone=data.get("phone", ""),
            description=data.get("description", ""),
            deals=data.get("deals", [])
        )
        business.id = data["id"]
        business.reviews = data.get("reviews", [])
        business.created_at = data.get("created_at", datetime.now().isoformat())
        return business


class BusinessBoost:
    """Main application class for Byte-Sized Business Boost."""
    
    def __init__(self, data_file: str = "business_data.json"):
        self.data_file = data_file
        self.businesses: List[Business] = []
        self.user_favorites: Dict[str, List[str]] = {}  # username -> [business_ids]
        self.load_data()
    
    def load_data(self):
        """Load businesses and user data from JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.businesses = [Business.from_dict(b) for b in data.get("businesses", [])]
                    self.user_favorites = data.get("user_favorites", {})
            except Exception as e:
                print(f"Error loading data: {e}")
                self.businesses = []
                self.user_favorites = {}
        else:
            # Initialize with sample data
            self._initialize_sample_data()
    
    def save_data(self):
        """Save businesses and user data to JSON file."""
        data = {
            "businesses": [b.to_dict() for b in self.businesses],
            "user_favorites": self.user_favorites
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _initialize_sample_data(self):
        """Initialize with sample businesses for demonstration."""
        sample_businesses = [
            Business(
                name="Joe's Coffee House",
                category="food",
                address="123 Main St, Downtown",
                phone="555-0101",
                description="Cozy local coffee shop with artisanal brews and fresh pastries. Family-owned since 2010.",
                deals=[{"title": "Buy 2 Get 1 Free", "description": "Any coffee drinks", "expires": "2024-12-31"}]
            ),
            Business(
                name="Green Thumb Garden Center",
                category="retail",
                address="456 Oak Ave, Garden District",
                phone="555-0102",
                description="Family-owned garden center with expert advice and quality plants. Your one-stop shop for all gardening needs.",
                deals=[{"title": "20% Off All Seeds", "description": "Valid this month", "expires": "2024-12-31"}]
            ),
            Business(
                name="Quick Fix Auto Repair",
                category="services",
                address="789 Industrial Blvd",
                phone="555-0103",
                description="Honest and reliable auto repair service. We've been serving the community for over 20 years.",
                deals=[{"title": "Free Oil Change", "description": "With any major service", "expires": "2024-12-31"}]
            ),
            Business(
                name="Mama's Italian Kitchen",
                category="food",
                address="321 Elm St, Little Italy",
                phone="555-0104",
                description="Authentic Italian cuisine made with love. Traditional recipes passed down through generations.",
                deals=[{"title": "10% Off Dinner", "description": "Monday-Thursday", "expires": "2024-12-31"}]
            ),
            Business(
                name="The Book Nook",
                category="retail",
                address="654 Pine St, Arts Quarter",
                phone="555-0105",
                description="Independent bookstore with curated selection of new and used books. Weekly book clubs and author events.",
                deals=[{"title": "Buy 2 Get 1 Free", "description": "All paperback books", "expires": "2024-12-31"}]
            ),
        ]
        self.businesses = sample_businesses
        self.save_data()
    
    def add_business(self, name: str, category: str, address: str, phone: str = "", 
                     description: str = "", deals: List[Dict] = None):
        """Add a new business to the directory."""
        business = Business(name, category, address, phone, description, deals)
        self.businesses.append(business)
        self.save_data()
        return True
    
    def get_businesses_by_category(self, category: str) -> List[Business]:
        """Get all businesses in a specific category."""
        return [b for b in self.businesses if b.category.lower() == category.lower()]
    
    def get_all_categories(self) -> List[str]:
        """Get list of all available categories."""
        categories = set(b.category for b in self.businesses)
        return sorted(categories)
    
    def sort_businesses_by_rating(self, reverse: bool = True) -> List[Business]:
        """Sort businesses by average rating."""
        return sorted(self.businesses, key=lambda b: b.get_average_rating(), reverse=reverse)
    
    def sort_businesses_by_review_count(self, reverse: bool = True) -> List[Business]:
        """Sort businesses by number of reviews."""
        return sorted(self.businesses, key=lambda b: b.get_review_count(), reverse=reverse)
    
    def add_review(self, business_id: str, user_name: str, rating: int, comment: str):
        """Add a review to a business."""
        business = self.find_business_by_id(business_id)
        if not business:
            return False
        
        try:
            business.add_review(user_name, rating, comment, verified=True)
            self.save_data()
            return True
        except ValueError:
            return False
    
    def find_business_by_id(self, business_id: str) -> Optional[Business]:
        """Find a business by its ID."""
        for business in self.businesses:
            if business.id == business_id:
                return business
        return None
    
    def add_to_favorites(self, username: str, business_id: str):
        """Add a business to user's favorites."""
        if username not in self.user_favorites:
            self.user_favorites[username] = []
        
        if business_id not in self.user_favorites[username]:
            self.user_favorites[username].append(business_id)
            self.save_data()
    
    def remove_from_favorites(self, username: str, business_id: str):
        """Remove a business from user's favorites."""
        if username in self.user_favorites and business_id in self.user_favorites[username]:
            self.user_favorites[username].remove(business_id)
            self.save_data()
    
    def get_favorites(self, username: str) -> List[Business]:
        """Get user's favorite businesses."""
        if username not in self.user_favorites:
            return []
        
        favorite_ids = self.user_favorites[username]
        return [b for b in self.businesses if b.id in favorite_ids]

