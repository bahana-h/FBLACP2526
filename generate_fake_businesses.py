#!/usr/bin/env python3
"""
Generate a large set of fake businesses for Byte-Sized Business Boost.

Targets:
- ~5,000 businesses in California (USA)
- ~10,000 businesses in other US states
- ~5,000 businesses in the rest of the world

This uses simple random generators and does NOT call any external APIs.
It overwrites the businesses in the current BusinessBoost data file.
"""

import random
from datetime import datetime, timedelta

from models import Business, BusinessBoost


RANDOM = random.Random(42)  # deterministic seed for reproducible data

CATEGORIES = ["food", "retail", "services"]

CA_CITIES = [
    "Los Angeles, CA, USA",
    "San Francisco, CA, USA",
    "San Diego, CA, USA",
    "San Jose, CA, USA",
    "Sacramento, CA, USA",
    "Fresno, CA, USA",
    "Oakland, CA, USA",
    "Long Beach, CA, USA",
    "Irvine, CA, USA",
    "Berkeley, CA, USA",
]

US_CITIES_OTHER = [
    "New York, NY, USA",
    "Chicago, IL, USA",
    "Houston, TX, USA",
    "Phoenix, AZ, USA",
    "Philadelphia, PA, USA",
    "San Antonio, TX, USA",
    "Dallas, TX, USA",
    "Austin, TX, USA",
    "Seattle, WA, USA",
    "Miami, FL, USA",
    "Boston, MA, USA",
    "Portland, OR, USA",
    "Atlanta, GA, USA",
    "Denver, CO, USA",
    "Minneapolis, MN, USA",
]

WORLD_CITIES = [
    "Toronto, ON, Canada",
    "Vancouver, BC, Canada",
    "London, UK",
    "Manchester, UK",
    "Paris, France",
    "Berlin, Germany",
    "Munich, Germany",
    "Tokyo, Japan",
    "Osaka, Japan",
    "Seoul, South Korea",
    "Sydney, Australia",
    "Melbourne, Australia",
    "Auckland, New Zealand",
    "Mexico City, Mexico",
    "São Paulo, Brazil",
    "Buenos Aires, Argentina",
    "Cape Town, South Africa",
    "Johannesburg, South Africa",
    "Mumbai, India",
    "Delhi, India",
]

FOOD_PREFIXES = [
    "Mama's", "Uncle Joe's", "Golden Gate", "Sunrise", "Lakeside",
    "Coastal", "Downtown", "Neighborhood", "Happy", "Smiling",
]
FOOD_TYPES = [
    "Diner", "Cafe", "Bistro", "Grill", "Pizzeria",
    "Noodle House", "Taco Shop", "BBQ", "Bakery", "Coffee Roasters",
]

RETAIL_PREFIXES = [
    "Green Leaf", "Urban", "Corner", "Central", "Main Street",
    "Bright", "Value", "Golden", "Evergreen", "Sunset",
]
RETAIL_TYPES = [
    "Bookstore", "Market", "Boutique", "Garden Center", "Toy Store",
    "Electronics", "Thrift Shop", "Clothing", "Home Goods", "Gift Shop",
]

SERVICE_PREFIXES = [
    "Quick", "Reliable", "Friendly", "Pro", "Premier",
    "Citywide", "Neighborhood", "Ace", "All-Star", "Trusted",
]
SERVICE_TYPES = [
    "Auto Repair", "Salon", "Barbershop", "Cleaning Services",
    "Pet Grooming", "IT Services", "Accounting", "Legal Services",
    "Tutoring Center", "Fitness Studio",
]

DEAL_TITLES = [
    "10% Off First Visit",
    "Buy 2 Get 1 Free",
    "Happy Hour Specials",
    "Free Consultation",
    "Student Discount",
    "Loyalty Card Bonus",
]
DEAL_DESCS = [
    "Limited time offer.",
    "Valid Monday–Thursday.",
    "Show this coupon at checkout.",
    "New customers only.",
    "Online orders included.",
]

REVIEW_COMMENTS = [
    "Amazing service and very friendly staff.",
    "Great experience overall, will come back again.",
    "Good value for the price.",
    "The atmosphere was nice and welcoming.",
    "Solid choice if you're in the area.",
    "Could be better, but still okay.",
    "My favorite place in the neighborhood.",
]

REVIEW_NAMES = [
    "Alex", "Taylor", "Jordan", "Morgan", "Sam", "Riley", "Casey",
    "Avery", "Quinn", "Jamie", "Cameron", "Harper", "Parker",
]


def random_phone() -> str:
    return f"({RANDOM.randint(200, 999)}) {RANDOM.randint(200, 999)}-{RANDOM.randint(1000, 9999)}"


def random_street() -> str:
    num = RANDOM.randint(10, 9999)
    name = RANDOM.choice(
        ["Main St", "Elm St", "Maple Ave", "Oak St", "Pine St", "Cedar Rd", "Sunset Blvd", "Broadway"]
    )
    return f"{num} {name}"


def build_business_name(category: str) -> str:
    if category == "food":
        return f"{RANDOM.choice(FOOD_PREFIXES)} {RANDOM.choice(FOOD_TYPES)}"
    if category == "retail":
        return f"{RANDOM.choice(RETAIL_PREFIXES)} {RANDOM.choice(RETAIL_TYPES)}"
    return f"{RANDOM.choice(SERVICE_PREFIXES)} {RANDOM.choice(SERVICE_TYPES)}"


def build_description(category: str) -> str:
    base = {
        "food": "Cozy local spot serving fresh, flavorful dishes.",
        "retail": "Community-focused shop with a curated selection of products.",
        "services": "Reliable, customer-first services for the local community.",
    }[category]
    extra = " Family-owned and operated." if RANDOM.random() < 0.5 else " Locally owned small business."
    return base + extra


def random_deals() -> list:
    deals = []
    if RANDOM.random() < 0.7:  # 70% of businesses have at least one deal
        count = 1 if RANDOM.random() < 0.6 else 2
        for _ in range(count):
            title = RANDOM.choice(DEAL_TITLES)
            desc = RANDOM.choice(DEAL_DESCS)
            # Expiration within next 6 months
            days = RANDOM.randint(7, 180)
            expires = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
            deals.append({"title": title, "description": desc, "expires": expires})
    return deals


def random_reviews() -> list:
    reviews = []
    if RANDOM.random() < 0.6:  # 60% of businesses have reviews
        count = RANDOM.randint(1, 8)
        for _ in range(count):
            rating = RANDOM.choices([5, 4, 3, 2, 1], weights=[40, 30, 15, 10, 5])[0]
            comment = RANDOM.choice(REVIEW_COMMENTS)
            name = RANDOM.choice(REVIEW_NAMES)
            days_ago = RANDOM.randint(0, 720)
            date = (datetime.now() - timedelta(days=days_ago)).isoformat()
            reviews.append(
                {
                    "user_name": name,
                    "rating": rating,
                    "comment": comment,
                    "verified": True,
                    "date": date,
                }
            )
    return reviews


def make_business(city_label: str, category: str) -> Business:
    name = build_business_name(category)
    address = f"{random_street()}, {city_label}"
    phone = random_phone()
    description = build_description(category)
    deals = random_deals()

    biz = Business(
        name=name,
        category=category,
        address=address,
        phone=phone,
        description=description,
        deals=deals,
    )
    biz.reviews = random_reviews()
    return biz


def generate_region_businesses(count: int, cities: list[str], label: str) -> list[Business]:
    businesses: list[Business] = []
    for i in range(count):
        category = RANDOM.choice(CATEGORIES)
        city = RANDOM.choice(cities)
        biz = make_business(city, category)
        businesses.append(biz)
        if (i + 1) % 1000 == 0:
            print(f"[{label}] generated {i + 1} businesses...")
    return businesses


def main():
    target_ca = 5000
    target_us_other = 10000
    target_world = 5000

    print("Generating fake businesses...")
    ca_businesses = generate_region_businesses(target_ca, CA_CITIES, "California")
    us_other_businesses = generate_region_businesses(target_us_other, US_CITIES_OTHER, "US Other")
    world_businesses = generate_region_businesses(target_world, WORLD_CITIES, "World")

    all_businesses = ca_businesses + us_other_businesses + world_businesses
    print(f"Total generated businesses: {len(all_businesses)}")

    boost = BusinessBoost()
    boost.businesses = all_businesses
    # Keep any existing favorites but clear businesses to avoid invalid IDs
    # (favorites will simply point to nonexistent IDs if left as-is)
    boost.user_favorites = {}
    boost.save_data()

    print("Saved fake businesses to business_data.json")


if __name__ == "__main__":
    main()

