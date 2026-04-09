#!/usr/bin/env python3
"""
Byte-Sized Business Boost
A tool to discover and support small, local businesses in your community.
"""

import json
import os
import random
import string
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict


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
                description="Cozy local coffee shop with artisanal brews",
                deals=[{"title": "Buy 2 Get 1 Free", "description": "Any coffee drinks", "expires": "2024-12-31"}]
            ),
            Business(
                name="Green Thumb Garden Center",
                category="retail",
                address="456 Oak Ave, Garden District",
                phone="555-0102",
                description="Family-owned garden center with expert advice",
                deals=[{"title": "20% Off All Seeds", "description": "Valid this month", "expires": "2024-12-31"}]
            ),
            Business(
                name="Quick Fix Auto Repair",
                category="services",
                address="789 Industrial Blvd",
                phone="555-0103",
                description="Honest and reliable auto repair service",
                deals=[{"title": "Free Oil Change", "description": "With any major service", "expires": "2024-12-31"}]
            ),
            Business(
                name="Mama's Italian Kitchen",
                category="food",
                address="321 Elm St, Little Italy",
                phone="555-0104",
                description="Authentic Italian cuisine made with love",
                deals=[{"title": "10% Off Dinner", "description": "Monday-Thursday", "expires": "2024-12-31"}]
            ),
            Business(
                name="The Book Nook",
                category="retail",
                address="654 Pine St, Arts Quarter",
                phone="555-0105",
                description="Independent bookstore with curated selection",
                deals=[{"title": "Buy 2 Get 1 Free", "description": "All paperback books", "expires": "2024-12-31"}]
            ),
        ]
        self.businesses = sample_businesses
        self.save_data()
    
    def verify_user(self) -> bool:
        """Simple verification to prevent bot activity."""
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        answer = num1 + num2
        
        user_answer = input(f"\n🤖 Verification: What is {num1} + {num2}? ")
        try:
            return int(user_answer) == answer
        except ValueError:
            return False
    
    def add_business(self, name: str, category: str, address: str, phone: str = "", 
                     description: str = "", deals: List[Dict] = None):
        """Add a new business to the directory."""
        if not self.verify_user():
            print("❌ Verification failed. Please try again.")
            return False
        
        business = Business(name, category, address, phone, description, deals)
        self.businesses.append(business)
        self.save_data()
        print(f"✅ Business '{name}' added successfully!")
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
        if not self.verify_user():
            print("❌ Verification failed. Please try again.")
            return False
        
        business = self.find_business_by_id(business_id)
        if not business:
            print("❌ Business not found.")
            return False
        
        try:
            business.add_review(user_name, rating, comment, verified=True)
            self.save_data()
            print(f"✅ Review added successfully!")
            return True
        except ValueError as e:
            print(f"❌ Error: {e}")
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
            print(f"✅ Business added to favorites!")
        else:
            print("ℹ️  Business is already in your favorites.")
    
    def remove_from_favorites(self, username: str, business_id: str):
        """Remove a business from user's favorites."""
        if username in self.user_favorites and business_id in self.user_favorites[username]:
            self.user_favorites[username].remove(business_id)
            self.save_data()
            print(f"✅ Business removed from favorites!")
        else:
            print("ℹ️  Business not found in favorites.")
    
    def get_favorites(self, username: str) -> List[Business]:
        """Get user's favorite businesses."""
        if username not in self.user_favorites:
            return []
        
        favorite_ids = self.user_favorites[username]
        return [b for b in self.businesses if b.id in favorite_ids]
    
    def display_business(self, business: Business, show_deals: bool = True):
        """Display business information."""
        print("\n" + "="*60)
        print(f"🏢 {business.name}")
        print("="*60)
        print(f"Category: {business.category.title()}")
        print(f"Address: {business.address}")
        if business.phone:
            print(f"Phone: {business.phone}")
        if business.description:
            print(f"Description: {business.description}")
        
        avg_rating = business.get_average_rating()
        review_count = business.get_review_count()
        if review_count > 0:
            stars = "⭐" * int(avg_rating)
            print(f"Rating: {avg_rating:.1f}/5.0 {stars} ({review_count} review{'s' if review_count != 1 else ''})")
        else:
            print("Rating: No reviews yet")
        
        if show_deals and business.deals:
            print("\n🎟️  Special Deals & Coupons:")
            for i, deal in enumerate(business.deals, 1):
                print(f"  {i}. {deal.get('title', 'Special Offer')}")
                print(f"     {deal.get('description', '')}")
                if deal.get('expires'):
                    print(f"     Expires: {deal.get('expires')}")
        
        if business.reviews:
            print("\n💬 Recent Reviews:")
            for review in business.reviews[-3:]:  # Show last 3 reviews
                stars = "⭐" * review["rating"]
                print(f"  {stars} {review['user_name']}: {review['comment']}")
        
        print("="*60)
    
    def display_business_list(self, businesses: List[Business], show_index: bool = True):
        """Display a list of businesses."""
        if not businesses:
            print("\n❌ No businesses found.")
            return
        
        print(f"\n📋 Found {len(businesses)} business(es):\n")
        for i, business in enumerate(businesses, 1):
            avg_rating = business.get_average_rating()
            review_count = business.get_review_count()
            rating_str = f"{avg_rating:.1f}⭐ ({review_count} reviews)" if review_count > 0 else "No reviews"
            
            if show_index:
                print(f"{i}. {business.name} - {business.category.title()}")
            else:
                print(f"   {business.name} - {business.category.title()}")
            print(f"   📍 {business.address}")
            print(f"   {rating_str}")
            if business.deals:
                print(f"   🎟️  {len(business.deals)} deal(s) available")
            print()


def main():
    """Main interactive CLI interface."""
    app = BusinessBoost()
    current_user = None
    
    print("\n" + "="*60)
    print("🌟 BYTE-SIZED BUSINESS BOOST 🌟")
    print("Discover and Support Local Businesses")
    print("="*60)
    
    while True:
        if not current_user:
            print("\n📝 Please enter your name to continue:")
            current_user = input("Name: ").strip()
            if not current_user:
                print("❌ Name cannot be empty.")
                continue
        
        print("\n" + "-"*60)
        print("MAIN MENU")
        print("-"*60)
        print("1. Browse All Businesses")
        print("2. Browse by Category")
        print("3. Search Businesses")
        print("4. View Top Rated Businesses")
        print("5. View Most Reviewed Businesses")
        print("6. Leave a Review")
        print("7. My Favorites")
        print("8. Add New Business")
        print("9. View Business Details")
        print("0. Exit")
        
        choice = input("\nSelect an option: ").strip()
        
        if choice == "1":
            app.display_business_list(app.businesses)
            input("\nPress Enter to continue...")
        
        elif choice == "2":
            categories = app.get_all_categories()
            if not categories:
                print("\n❌ No categories available.")
            else:
                print("\nAvailable Categories:")
                for i, cat in enumerate(categories, 1):
                    print(f"  {i}. {cat.title()}")
                
                try:
                    cat_choice = int(input("\nSelect category number: ")) - 1
                    if 0 <= cat_choice < len(categories):
                        selected_cat = categories[cat_choice]
                        businesses = app.get_businesses_by_category(selected_cat)
                        app.display_business_list(businesses)
                    else:
                        print("❌ Invalid selection.")
                except ValueError:
                    print("❌ Please enter a valid number.")
            input("\nPress Enter to continue...")
        
        elif choice == "3":
            search_term = input("\nEnter search term (name, category, or address): ").strip().lower()
            if search_term:
                results = [
                    b for b in app.businesses
                    if search_term in b.name.lower() or 
                       search_term in b.category.lower() or 
                       search_term in b.address.lower()
                ]
                app.display_business_list(results)
            else:
                print("❌ Please enter a search term.")
            input("\nPress Enter to continue...")
        
        elif choice == "4":
            sorted_businesses = app.sort_businesses_by_rating()
            # Filter out businesses with no reviews
            reviewed = [b for b in sorted_businesses if b.get_review_count() > 0]
            if reviewed:
                print("\n⭐ TOP RATED BUSINESSES ⭐")
                app.display_business_list(reviewed[:10])  # Top 10
            else:
                print("\n❌ No businesses with reviews yet.")
            input("\nPress Enter to continue...")
        
        elif choice == "5":
            sorted_businesses = app.sort_businesses_by_review_count()
            if sorted_businesses:
                print("\n💬 MOST REVIEWED BUSINESSES 💬")
                app.display_business_list(sorted_businesses[:10])  # Top 10
            else:
                print("\n❌ No businesses with reviews yet.")
            input("\nPress Enter to continue...")
        
        elif choice == "6":
            app.display_business_list(app.businesses)
            try:
                biz_num = int(input("\nEnter business number to review: "))
                if 1 <= biz_num <= len(app.businesses):
                    business = app.businesses[biz_num - 1]
                    print(f"\nReviewing: {business.name}")
                    
                    rating = int(input("Rating (1-5): "))
                    comment = input("Comment: ").strip()
                    
                    app.add_review(business.id, current_user, rating, comment)
                else:
                    print("❌ Invalid business number.")
            except ValueError:
                print("❌ Please enter a valid number.")
            except Exception as e:
                print(f"❌ Error: {e}")
            input("\nPress Enter to continue...")
        
        elif choice == "7":
            favorites = app.get_favorites(current_user)
            if favorites:
                print(f"\n❤️  {current_user}'s Favorites:")
                app.display_business_list(favorites)
                
                print("Options:")
                print("  1. View business details")
                print("  2. Remove from favorites")
                print("  3. Back to main menu")
                fav_choice = input("Select: ").strip()
                
                if fav_choice == "1":
                    try:
                        biz_num = int(input("Enter business number: "))
                        if 1 <= biz_num <= len(favorites):
                            app.display_business(favorites[biz_num - 1])
                        else:
                            print("❌ Invalid number.")
                    except ValueError:
                        print("❌ Please enter a valid number.")
                
                elif fav_choice == "2":
                    try:
                        biz_num = int(input("Enter business number to remove: "))
                        if 1 <= biz_num <= len(favorites):
                            business = favorites[biz_num - 1]
                            app.remove_from_favorites(current_user, business.id)
                        else:
                            print("❌ Invalid number.")
                    except ValueError:
                        print("❌ Please enter a valid number.")
            else:
                print(f"\n❤️  You don't have any favorites yet.")
                print("   Add businesses to favorites from the business details view.")
            input("\nPress Enter to continue...")
        
        elif choice == "8":
            print("\n➕ Add New Business")
            print("(Verification required)")
            name = input("Business Name: ").strip()
            if not name:
                print("❌ Name is required.")
            else:
                category = input("Category (food/retail/services): ").strip()
                address = input("Address: ").strip()
                phone = input("Phone (optional): ").strip()
                description = input("Description (optional): ").strip()
                
                deals_input = input("Add a deal? (y/n): ").strip().lower()
                deals = []
                if deals_input == 'y':
                    deal_title = input("Deal Title: ").strip()
                    deal_desc = input("Deal Description: ").strip()
                    deal_expires = input("Expires (YYYY-MM-DD): ").strip()
                    deals.append({
                        "title": deal_title,
                        "description": deal_desc,
                        "expires": deal_expires
                    })
                
                app.add_business(name, category, address, phone, description, deals)
            input("\nPress Enter to continue...")
        
        elif choice == "9":
            app.display_business_list(app.businesses)
            try:
                biz_num = int(input("\nEnter business number to view details: "))
                if 1 <= biz_num <= len(app.businesses):
                    business = app.businesses[biz_num - 1]
                    app.display_business(business)
                    
                    print("\nOptions:")
                    print("  1. Add to favorites")
                    print("  2. Leave a review")
                    print("  3. Back to main menu")
                    detail_choice = input("Select: ").strip()
                    
                    if detail_choice == "1":
                        app.add_to_favorites(current_user, business.id)
                    elif detail_choice == "2":
                        rating = int(input("Rating (1-5): "))
                        comment = input("Comment: ").strip()
                        app.add_review(business.id, current_user, rating, comment)
                else:
                    print("❌ Invalid business number.")
            except ValueError:
                print("❌ Please enter a valid number.")
            except Exception as e:
                print(f"❌ Error: {e}")
            input("\nPress Enter to continue...")
        
        elif choice == "0":
            print("\n👋 Thank you for supporting local businesses!")
            print("   Have a great day!")
            break
        
        else:
            print("\n❌ Invalid option. Please try again.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()

