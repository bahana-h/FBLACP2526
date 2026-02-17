#!/usr/bin/env python3
"""
Chrysalis Connect - CLI Tool

Command-line interface for discovering and supporting local businesses.
Uses models.Business and models.BusinessBoost; shares business_data.json with the web app.
"""

import random
from typing import List

from models import Business, BusinessBoost


class CLIApp(BusinessBoost):
    """CLI extension of BusinessBoost with display and verification methods."""

    def verify_user(self) -> bool:
        """Interactive verification to prevent bot activity."""
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        answer = num1 + num2
        user_answer = input(f"\n🤖 Verification: What is {num1} + {num2}? ")
        try:
            return int(user_answer) == answer
        except ValueError:
            return False

    def add_business(self, name: str, category: str, address: str, phone: str = "",
                     description: str = "", deals: List[dict] = None) -> bool:
        """Add business after verification."""
        if not self.verify_user():
            print("❌ Verification failed. Please try again.")
            return False
        if super().add_business(name, category, address, phone, description, deals):
            print(f"✅ Business '{name}' added successfully!")
            return True
        return False

    def add_review(self, business_id: str, user_name: str, rating: int, comment: str) -> bool:
        """Add review after verification."""
        if not self.verify_user():
            print("❌ Verification failed. Please try again.")
            return False
        if super().add_review(business_id, user_name, rating, comment):
            print("✅ Review added successfully!")
            return True
        return False

    def add_to_favorites(self, username: str, business_id: str) -> None:
        """Add to favorites with feedback."""
        was_in = business_id in self.user_favorites.get(username, [])
        super().add_to_favorites(username, business_id)
        print("ℹ️  Business is already in your favorites." if was_in else "✅ Business added to favorites!")

    def remove_from_favorites(self, username: str, business_id: str) -> None:
        """Remove from favorites with feedback."""
        super().remove_from_favorites(username, business_id)
        print("✅ Business removed from favorites!")

    def display_business(self, business: Business, show_deals: bool = True) -> None:
        """Display business details in the terminal."""
        print("\n" + "=" * 60)
        print(f"🏢 {business.name}")
        print("=" * 60)
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
            for review in business.reviews[-3:]:
                stars = "⭐" * review["rating"]
                print(f"  {stars} {review['user_name']}: {review['comment']}")
        print("=" * 60)

    def display_business_list(self, businesses: List[Business], show_index: bool = True) -> None:
        """Display a list of businesses in the terminal."""
        if not businesses:
            print("\n❌ No businesses found.")
            return
        print(f"\n📋 Found {len(businesses)} business(es):\n")
        for i, business in enumerate(businesses, 1):
            avg_rating = business.get_average_rating()
            review_count = business.get_review_count()
            rating_str = f"{avg_rating:.1f}⭐ ({review_count} reviews)" if review_count > 0 else "No reviews"
            prefix = f"{i}. " if show_index else "   "
            print(f"{prefix}{business.name} - {business.category.title()}")
            print(f"   📍 {business.address}")
            print(f"   {rating_str}")
            if business.deals:
                print(f"   🎟️  {len(business.deals)} deal(s) available")
            print()


def main() -> None:
    """Main interactive CLI interface."""
    app = CLIApp()
    current_user = None

    print("\n" + "=" * 60)
    print("🌟 CHRYSALIS CONNECT 🌟")
    print("Discover and Support Local Businesses")
    print("=" * 60)

    while True:
        if not current_user:
            print("\n📝 Please enter your name to continue:")
            current_user = input("Name: ").strip()
            if not current_user:
                print("❌ Name cannot be empty.")
                continue

        print("\n" + "-" * 60)
        print("MAIN MENU")
        print("-" * 60)
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
                        app.display_business_list(app.get_businesses_by_category(categories[cat_choice]))
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
                    if search_term in b.name.lower() or search_term in b.category.lower()
                    or search_term in b.address.lower()
                ]
                app.display_business_list(results)
            else:
                print("❌ Please enter a search term.")
            input("\nPress Enter to continue...")

        elif choice == "4":
            reviewed = [b for b in app.sort_businesses_by_rating() if b.get_review_count() > 0]
            if reviewed:
                print("\n⭐ TOP RATED BUSINESSES ⭐")
                app.display_business_list(reviewed[:10])
            else:
                print("\n❌ No businesses with reviews yet.")
            input("\nPress Enter to continue...")

        elif choice == "5":
            sorted_businesses = app.sort_businesses_by_review_count()
            if sorted_businesses:
                print("\n💬 MOST REVIEWED BUSINESSES 💬")
                app.display_business_list(sorted_businesses[:10])
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
            except (ValueError, Exception) as e:
                print(f"❌ Error: {e}")
            input("\nPress Enter to continue...")

        elif choice == "7":
            favorites = app.get_favorites(current_user)
            if favorites:
                print(f"\n❤️  {current_user}'s Favorites:")
                app.display_business_list(favorites)
                print("Options: 1=View details 2=Remove 3=Back")
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
                            app.remove_from_favorites(current_user, favorites[biz_num - 1].id)
                        else:
                            print("❌ Invalid number.")
                    except ValueError:
                        print("❌ Please enter a valid number.")
            else:
                print(f"\n❤️  You don't have any favorites yet.")
            input("\nPress Enter to continue...")

        elif choice == "8":
            print("\n➕ Add New Business (Verification required)")
            name = input("Business Name: ").strip()
            if name:
                category = input("Category (food/retail/services): ").strip()
                address = input("Address: ").strip()
                phone = input("Phone (optional): ").strip()
                description = input("Description (optional): ").strip()
                deals = []
                if input("Add a deal? (y/n): ").strip().lower() == 'y':
                    deals.append({
                        "title": input("Deal Title: ").strip(),
                        "description": input("Deal Description: ").strip(),
                        "expires": input("Expires (YYYY-MM-DD): ").strip()
                    })
                app.add_business(name, category, address, phone, description, deals)
            else:
                print("❌ Name is required.")
            input("\nPress Enter to continue...")

        elif choice == "9":
            app.display_business_list(app.businesses)
            try:
                biz_num = int(input("\nEnter business number to view details: "))
                if 1 <= biz_num <= len(app.businesses):
                    business = app.businesses[biz_num - 1]
                    app.display_business(business)
                    print("\nOptions: 1=Add to favorites 2=Leave review 3=Back")
                    detail_choice = input("Select: ").strip()
                    if detail_choice == "1":
                        app.add_to_favorites(current_user, business.id)
                    elif detail_choice == "2":
                        rating = int(input("Rating (1-5): "))
                        comment = input("Comment: ").strip()
                        app.add_review(business.id, current_user, rating, comment)
                else:
                    print("❌ Invalid business number.")
            except (ValueError, Exception) as e:
                print(f"❌ Error: {e}")
            input("\nPress Enter to continue...")

        elif choice == "0":
            print("\n👋 Thank you for supporting local businesses!")
            break

        else:
            print("\n❌ Invalid option. Please try again.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
