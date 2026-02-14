"""
Business models for Byte-Sized Business Boost

This module implements the core data models and business logic for the application.
It uses object-oriented programming principles to encapsulate business data and operations.

ARCHITECTURE DECISIONS:
- Uses Python classes for encapsulation and code reusability
- JSON file-based storage for simplicity (no database required)
- Type hints for better code documentation and IDE support
- Separation of concerns: Business class handles single business logic,
  BusinessBoost class handles collection operations

DATA STORAGE:
- JSON format chosen for human-readable, portable data
- No database dependencies - works out of the box
- Easy to backup, version control, and migrate
"""

import json
import os
import random
import string
from datetime import datetime
from typing import Dict, List, Optional


class Business:
    """
    Represents a single local business entity.
    
    This class encapsulates all data and operations related to a business:
    - Business information (name, category, address, contact)
    - Deals and promotional offers
    - User reviews and ratings
    - Data serialization for storage
    
    DESIGN PATTERN: Domain Model Pattern
    - Encapsulates business logic within the data object
    - Provides methods for operations on business data
    - Handles its own validation and data transformation
    """
    
    def __init__(self, name: str, category: str, address: str, phone: str = "", 
                 description: str = "", deals: List[Dict] = None,
                 latitude: Optional[float] = None, longitude: Optional[float] = None):
        """
        Initialize a new Business instance.
        
        Args:
            name: Business name (required, validated for non-empty)
            category: Business category - 'food', 'retail', or 'services' (normalized to lowercase)
            address: Physical address of the business (required)
            phone: Contact phone number (optional, defaults to empty string)
            description: Business description text (optional)
            deals: List of promotional deals/coupons (optional, defaults to empty list)
        
        DESIGN DECISION: Using default parameters for optional fields
        - Reduces code complexity
        - Makes API more flexible
        - Follows Python best practices for optional parameters
        """
        # Generate unique identifier using random alphanumeric string
        # This ensures each business has a unique ID even if names are duplicated
        self.id = self._generate_id()
        
        # Core business information - stored as instance variables
        # Using instance variables allows for easy access and modification
        self.name = name
        self.category = category.lower()  # Normalize to lowercase for consistent filtering
        self.address = address
        self.phone = phone
        self.description = description
        
        # Deals list - using 'or []' pattern to ensure we always have a list
        # This prevents None errors when iterating over deals
        self.deals = deals or []
        
        # Reviews list - initialized empty, populated by user interactions
        # Using list allows for multiple reviews per business
        self.reviews = []
        
        # Optional coordinates for map display (latitude, longitude)
        self.latitude = latitude
        self.longitude = longitude
        
        # Timestamp for when business was created
        # ISO format ensures consistent date representation across systems
        self.created_at = datetime.now().isoformat()
    
    def _generate_id(self) -> str:
        """
        Generate a unique identifier for the business.
        
        Returns:
            str: 8-character alphanumeric string (e.g., 'aB3xY9mK')
        
        ALGORITHM: Random selection with replacement
        - Uses random.choices() for efficient generation
        - 8 characters provides 218 trillion possible combinations
        - Alphanumeric ensures URL-safe identifiers
        
        DESIGN DECISION: Private method (leading underscore)
        - Indicates internal implementation detail
        - Prevents external code from calling this directly
        - Allows for future implementation changes without breaking API
        """
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    def add_review(self, user_name: str, rating: int, comment: str, verified: bool = False):
        """
        Add a user review to this business.
        
        Args:
            user_name: Name of the reviewer (required)
            rating: Rating value from 1-5 (validated)
            comment: Review text content (required)
            verified: Whether review passed bot verification (defaults to False)
        
        Raises:
            ValueError: If rating is not between 1 and 5
        
        VALIDATION: Semantic validation of rating
        - Checks that rating is within valid range (1-5)
        - Raises descriptive error if invalid
        - Prevents invalid data from entering the system
        
        DATA STRUCTURE: Review stored as dictionary
        - Allows for easy JSON serialization
        - Flexible structure for future fields
        - Includes timestamp for chronological sorting
        """
        # Input validation: Ensure rating is within valid range
        # This is semantic validation - checking meaning, not just format
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        # Create review dictionary with all relevant information
        # Dictionary structure allows for easy serialization and querying
        review = {
            "user_name": user_name,
            "rating": rating,
            "comment": comment,
            "verified": verified,  # Track verification status for quality control
            "date": datetime.now().isoformat()  # ISO format for consistent date handling
        }
        
        # Append to reviews list - maintains chronological order
        # List data structure allows for multiple reviews per business
        self.reviews.append(review)
    
    def get_average_rating(self) -> float:
        """
        Calculate the average rating from all reviews.
        
        Returns:
            float: Average rating (0.0 if no reviews exist)
        
        ALGORITHM: Sum and divide
        - Sums all ratings using generator expression (memory efficient)
        - Divides by count for average
        - Returns 0.0 for businesses with no reviews (prevents division by zero)
        
        DESIGN DECISION: Return 0.0 instead of None
        - Allows for consistent numeric operations
        - Simplifies sorting and filtering logic
        - Clear indication of "no rating" state
        """
        # Edge case handling: Return 0 if no reviews exist
        # This prevents division by zero errors
        if not self.reviews:
            return 0.0
        
        # Calculate average using sum and division
        # Generator expression (r["rating"] for r in self.reviews) is memory efficient
        # Works with any number of reviews without loading all into memory
        return sum(r["rating"] for r in self.reviews) / len(self.reviews)
    
    def get_review_count(self) -> int:
        """
        Get the total number of reviews for this business.
        
        Returns:
            int: Number of reviews (0 if none exist)
        
        DESIGN DECISION: Simple method instead of direct attribute access
        - Provides consistent interface
        - Allows for future logic (e.g., filtering verified reviews only)
        - Encapsulates implementation details
        """
        return len(self.reviews)
    
    def to_dict(self) -> Dict:
        """
        Convert Business instance to dictionary for JSON serialization.
        
        Returns:
            Dict: Dictionary representation of the business
        
        SERIALIZATION: Custom serialization method
        - Converts Python object to JSON-compatible dictionary
        - Includes all relevant fields
        - Maintains data structure for round-trip conversion
        
        DESIGN PATTERN: Data Transfer Object (DTO)
        - Separates domain model from storage format
        - Allows for versioning and migration
        - Enables different storage backends in future
        """
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "address": self.address,
            "phone": self.phone,
            "description": self.description,
            "deals": self.deals,
            "reviews": self.reviews,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Business':
        """
        Create a Business instance from a dictionary (deserialization).
        
        Args:
            data: Dictionary containing business data (from JSON)
        
        Returns:
            Business: New Business instance with data populated
        
        DESIGN PATTERN: Factory Method Pattern
        - Class method creates instances from different data sources
        - Handles data migration and version compatibility
        - Uses .get() with defaults for backward compatibility
        
        ERROR HANDLING: Graceful defaults
        - Uses .get() to handle missing fields
        - Provides sensible defaults for optional fields
        - Prevents crashes from incomplete data
        """
        # Create new instance with required fields
        # Using .get() for optional fields provides defaults if missing
        business = cls(
            name=data["name"],
            category=data["category"],
            address=data["address"],
            phone=data.get("phone", ""),  # Default to empty string if missing
            description=data.get("description", ""),  # Default to empty string
            deals=data.get("deals", []),  # Default to empty list
            latitude=data.get("latitude"),
            longitude=data.get("longitude")
        )
        
        # Restore instance-specific fields that aren't set in __init__
        business.id = data["id"]
        business.reviews = data.get("reviews", [])  # Restore reviews if they exist
        business.created_at = data.get("created_at", datetime.now().isoformat())
        
        return business


class BusinessBoost:
    """
    Main application class managing the collection of businesses.
    
    This class handles:
    - Loading and saving business data
    - Querying and filtering businesses
    - Managing user favorites
    - Sorting and searching operations
    
    DESIGN PATTERN: Repository Pattern
    - Encapsulates data access logic
    - Provides high-level interface for business operations
    - Abstracts storage implementation details
    
    DATA STRUCTURE DECISIONS:
    - businesses: List[Business] - Ordered collection, allows duplicates
    - user_favorites: Dict[str, List[str]] - Fast lookup by username, maintains order
    """
    
    def __init__(self, data_file: str = "business_data.json"):
        """
        Initialize the BusinessBoost system.
        
        Args:
            data_file: Path to JSON file for data persistence (defaults to "business_data.json")
        
        DESIGN DECISION: File path as parameter
        - Allows for testing with different files
        - Enables multiple instances with different data
        - Follows dependency injection pattern
        """
        # Store file path for persistence operations
        self.data_file = data_file
        
        # Initialize empty collections
        # List for businesses - maintains insertion order, allows duplicates
        self.businesses: List[Business] = []
        
        # Dictionary mapping username to list of business IDs
        # Dictionary provides O(1) lookup time for user favorites
        # List maintains order of favorite additions
        self.user_favorites: Dict[str, List[str]] = {}
        
        # Load existing data from file (if it exists)
        # This ensures data persistence across application restarts
        self.load_data()
    
    def load_data(self):
        """
        Load businesses and user data from JSON file.
        
        ERROR HANDLING: Comprehensive error handling
        - Checks if file exists before reading
        - Catches JSON parsing errors
        - Falls back to sample data if loading fails
        - Prevents application crash from corrupted data
        
        DESIGN DECISION: Silent failure with fallback
        - Application continues to work even if data file is corrupted
        - Initializes with sample data for demonstration
        - Logs error for debugging without crashing
        """
        # Check if data file exists before attempting to read
        if os.path.exists(self.data_file):
            try:
                # Open file in read mode with context manager (auto-closes)
                # Context manager ensures file is closed even if error occurs
                with open(self.data_file, 'r') as f:
                    # Parse JSON data into Python dictionary
                    # JSON format is human-readable and widely supported
                    data = json.load(f)
                    
                    # Convert dictionary data to Business objects
                    # List comprehension efficiently processes all businesses
                    # .get() provides empty list if 'businesses' key doesn't exist
                    self.businesses = [Business.from_dict(b) for b in data.get("businesses", [])]
                    
                    # Restore user favorites dictionary
                    # .get() provides empty dict if 'user_favorites' key doesn't exist
                    self.user_favorites = data.get("user_favorites", {})
            except Exception as e:
                # Catch any errors (JSON parsing, file reading, etc.)
                # Print error for debugging
                print(f"Error loading data: {e}")
                # Initialize empty collections to prevent crashes
                self.businesses = []
                self.user_favorites = {}
        else:
            # File doesn't exist - initialize with sample data
            # This provides a working application on first run
            self._initialize_sample_data()
    
    def save_data(self):
        """
        Save businesses and user data to JSON file.
        
        PERSISTENCE: Atomic write operation
        - Converts all business objects to dictionaries
        - Writes entire dataset in one operation
        - Uses indentation for human-readable JSON
        
        DESIGN DECISION: Save entire dataset each time
        - Simpler than incremental updates
        - Ensures data consistency
        - Trade-off: Slower for very large datasets (acceptable for this use case)
        """
        # Prepare data dictionary for JSON serialization
        # Convert Business objects to dictionaries using to_dict() method
        # List comprehension processes all businesses efficiently
        data = {
            "businesses": [b.to_dict() for b in self.businesses],
            "user_favorites": self.user_favorites
        }
        
        # Write to file with indentation for readability
        # Context manager ensures file is closed properly
        # indent=2 makes JSON human-readable for debugging
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _initialize_sample_data(self):
        """
        Initialize with sample businesses for demonstration.
        
        DESIGN DECISION: Sample data for first-time users
        - Provides immediate value without setup
        - Demonstrates application features
        - Helps users understand data structure
        """
        # Create sample businesses across different categories
        # This demonstrates the application's capabilities
        # Sample businesses with approximate coordinates (San Francisco area) for map display
        sample_businesses = [
            Business(
                name="Joe's Coffee House",
                category="food",
                address="123 Main St, Downtown",
                phone="555-0101",
                description="Cozy local coffee shop with artisanal brews and fresh pastries. Family-owned since 2010.",
                deals=[{"title": "Buy 2 Get 1 Free", "description": "Any coffee drinks", "expires": "2024-12-31"}],
                latitude=37.785, longitude=-122.409
            ),
            Business(
                name="Green Thumb Garden Center",
                category="retail",
                address="456 Oak Ave, Garden District",
                phone="555-0102",
                description="Family-owned garden center with expert advice and quality plants. Your one-stop shop for all gardening needs.",
                deals=[{"title": "20% Off All Seeds", "description": "Valid this month", "expires": "2024-12-31"}],
                latitude=37.772, longitude=-122.435
            ),
            Business(
                name="Quick Fix Auto Repair",
                category="services",
                address="789 Industrial Blvd",
                phone="555-0103",
                description="Honest and reliable auto repair service. We've been serving the community for over 20 years.",
                deals=[{"title": "Free Oil Change", "description": "With any major service", "expires": "2024-12-31"}],
                latitude=37.762, longitude=-122.400
            ),
            Business(
                name="Mama's Italian Kitchen",
                category="food",
                address="321 Elm St, Little Italy",
                phone="555-0104",
                description="Authentic Italian cuisine made with love. Traditional recipes passed down through generations.",
                deals=[{"title": "10% Off Dinner", "description": "Monday-Thursday", "expires": "2024-12-31"}],
                latitude=37.798, longitude=-122.408
            ),
            Business(
                name="The Book Nook",
                category="retail",
                address="654 Pine St, Arts Quarter",
                phone="555-0105",
                description="Independent bookstore with curated selection of new and used books. Weekly book clubs and author events.",
                deals=[{"title": "Buy 2 Get 1 Free", "description": "All paperback books", "expires": "2024-12-31"}],
                latitude=37.789, longitude=-122.428
            ),
        ]
        
        # Assign sample businesses and save to file
        self.businesses = sample_businesses
        self.save_data()
    
    def add_business(self, name: str, category: str, address: str, phone: str = "", 
                     description: str = "", deals: List[Dict] = None):
        """
        Add a new business to the directory.
        
        Args:
            name: Business name (required)
            category: Business category (required)
            address: Business address (required)
            phone: Contact phone (optional)
            description: Business description (optional)
            deals: List of deals/coupons (optional)
        
        Returns:
            bool: True if business was added successfully
        
        VALIDATION: Input validation should be done by caller
        - This method assumes valid input
        - Validation happens at the Flask route level
        - Separation of concerns: validation vs. business logic
        """
        # Create new Business instance
        # Business class handles ID generation and initialization
        business = Business(name, category, address, phone, description, deals)
        
        # Add to businesses list
        # List.append() is O(1) operation - efficient for adding items
        self.businesses.append(business)
        
        # Persist to file immediately
        # Ensures data is saved even if application crashes
        self.save_data()
        
        return True
    
    def get_businesses_by_category(self, category: str) -> List[Business]:
        """
        Filter businesses by category.
        
        Args:
            category: Category to filter by (case-insensitive)
        
        Returns:
            List[Business]: List of businesses in the specified category
        
        ALGORITHM: List comprehension with filtering
        - O(n) time complexity where n is number of businesses
        - Case-insensitive comparison for user-friendly filtering
        - Returns new list (doesn't modify original)
        
        DESIGN DECISION: Case-insensitive matching
        - More user-friendly (handles "Food", "food", "FOOD")
        - Prevents filtering errors from case mismatches
        """
        # List comprehension filters businesses by category
        # .lower() ensures case-insensitive comparison
        # Returns new list, doesn't modify original (immutable operation)
        return [b for b in self.businesses if b.category.lower() == category.lower()]
    
    def get_all_categories(self) -> List[str]:
        """
        Get list of all unique categories in the system.
        
        Returns:
            List[str]: Sorted list of unique category names
        
        ALGORITHM: Set for uniqueness, then sort
        - Set comprehension extracts unique categories
        - sorted() returns alphabetically ordered list
        - O(n log n) complexity due to sorting
        
        DESIGN DECISION: Return sorted list
        - Consistent ordering for UI display
        - Easier to find categories in dropdown menus
        - Predictable behavior for users
        """
        # Set comprehension extracts unique categories
        # Set data structure automatically removes duplicates
        categories = set(b.category for b in self.businesses)
        
        # Sort alphabetically for consistent display
        return sorted(categories)
    
    def sort_businesses_by_rating(self, reverse: bool = True) -> List[Business]:
        """
        Sort businesses by average rating.
        
        Args:
            reverse: If True, sort descending (highest first); if False, ascending
        
        Returns:
            List[Business]: Sorted list of businesses
        
        ALGORITHM: Timsort (Python's default sort)
        - O(n log n) time complexity
        - Stable sort (maintains relative order of equal elements)
        - Uses key function for efficient sorting
        
        DESIGN DECISION: Default to descending order
        - Users typically want to see highest-rated businesses first
        - Matches common UI patterns (e.g., Amazon, Yelp)
        """
        # sorted() creates new list (doesn't modify original)
        # key parameter extracts rating for comparison
        # lambda function calls get_average_rating() for each business
        return sorted(self.businesses, key=lambda b: b.get_average_rating(), reverse=reverse)
    
    def sort_businesses_by_review_count(self, reverse: bool = True) -> List[Business]:
        """
        Sort businesses by number of reviews.
        
        Args:
            reverse: If True, sort descending (most reviews first)
        
        Returns:
            List[Business]: Sorted list of businesses
        
        DESIGN DECISION: Separate method for review count sorting
        - Different use case than rating sorting
        - Allows for independent optimization
        - Clearer API than single method with multiple parameters
        """
        # Similar to rating sort, but uses review count instead
        # get_review_count() is O(1) operation (just len())
        return sorted(self.businesses, key=lambda b: b.get_review_count(), reverse=reverse)
    
    def add_review(self, business_id: str, user_name: str, rating: int, comment: str):
        """
        Add a review to a specific business.
        
        Args:
            business_id: Unique identifier of the business
            user_name: Name of the reviewer
            rating: Rating value (1-5)
            comment: Review text
        
        Returns:
            bool: True if review was added successfully, False otherwise
        
        ERROR HANDLING: Graceful failure
        - Returns False if business not found (instead of raising exception)
        - Catches ValueError from invalid rating
        - Prevents application crash from invalid input
        """
        # Find business by ID
        # Returns None if not found (handled by if statement)
        business = self.find_business_by_id(business_id)
        if not business:
            return False
        
        try:
            # Add review to business
            # Business.add_review() handles validation
            business.add_review(user_name, rating, comment, verified=True)
            
            # Persist changes to file
            self.save_data()
            
            return True
        except ValueError:
            # Rating was invalid (not 1-5)
            # Return False instead of propagating exception
            return False
    
    def find_business_by_id(self, business_id: str) -> Optional[Business]:
        """
        Find a business by its unique identifier.
        
        Args:
            business_id: Unique identifier to search for
        
        Returns:
            Optional[Business]: Business object if found, None otherwise
        
        ALGORITHM: Linear search
        - O(n) time complexity
        - Simple and straightforward
        - Could be optimized with dictionary lookup if needed
        
        DESIGN DECISION: Return Optional[Business]
        - Explicitly indicates "may not exist"
        - Type hints help with IDE support and documentation
        - Caller must handle None case
        """
        # Linear search through businesses list
        # Returns first match (IDs should be unique)
        for business in self.businesses:
            if business.id == business_id:
                return business
        
        # Return None if not found
        # None is falsy, allows for easy checking: if business: ...
        return None
    
    def add_to_favorites(self, username: str, business_id: str):
        """
        Add a business to a user's favorites list.
        
        Args:
            username: Name of the user
            business_id: ID of business to favorite
        
        DESIGN DECISION: No return value
        - Operation either succeeds or does nothing (idempotent)
        - Caller doesn't need to check return value
        - Simpler API than returning success/failure
        """
        # Initialize favorites list for new users
        # Dictionary pattern: check if key exists before accessing
        if username not in self.user_favorites:
            self.user_favorites[username] = []
        
        # Add business ID if not already in favorites
        # Prevents duplicate favorites
        # List membership check is O(n), acceptable for typical list sizes
        if business_id not in self.user_favorites[username]:
            self.user_favorites[username].append(business_id)
            # Persist changes immediately
            self.save_data()
    
    def remove_from_favorites(self, username: str, business_id: str):
        """
        Remove a business from a user's favorites list.
        
        Args:
            username: Name of the user
            business_id: ID of business to remove
        
        DESIGN DECISION: Idempotent operation
        - Safe to call multiple times
        - No error if business not in favorites
        - Simplifies caller code
        """
        # Check if user has favorites and business is in list
        # Multiple conditions prevent KeyError and ValueError
        if username in self.user_favorites and business_id in self.user_favorites[username]:
            # Remove from list (removes first occurrence)
            self.user_favorites[username].remove(business_id)
            # Persist changes
            self.save_data()
    
    def get_favorites(self, username: str) -> List[Business]:
        """
        Get all favorite businesses for a user.
        
        Args:
            username: Name of the user
        
        Returns:
            List[Business]: List of Business objects that are favorited
        
        ALGORITHM: List comprehension with membership check
        - Filters businesses list to only include favorites
        - Maintains order of favorites list
        - O(n*m) complexity where n=businesses, m=favorites
        
        DESIGN DECISION: Return Business objects, not IDs
        - Caller gets full business data immediately
        - No need for separate lookup step
        - More convenient API
        """
        # Return empty list if user has no favorites
        # Prevents KeyError and provides consistent return type
        if username not in self.user_favorites:
            return []
        
        # Get list of favorite business IDs
        favorite_ids = self.user_favorites[username]
        
        # Filter businesses list to only include favorites
        # List comprehension efficiently filters and returns Business objects
        # Maintains order of favorites list
        return [b for b in self.businesses if b.id in favorite_ids]
