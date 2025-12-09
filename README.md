# Byte-Sized Business Boost 🌟

A Python-based command-line tool that helps users discover and support small, local businesses in their community. This interactive application provides a comprehensive platform for exploring local businesses, leaving reviews, managing favorites, and discovering special deals.

## Features

✅ **Category-Based Sorting**: Browse businesses by category (food, retail, services)

✅ **Review & Rating System**: Leave reviews and ratings for businesses with bot verification

✅ **Smart Sorting**: Sort businesses by average rating or number of reviews

✅ **Favorites Management**: Save and bookmark your favorite local businesses

✅ **Deals & Coupons**: View special deals and promotional offers from businesses

✅ **Bot Verification**: Simple math verification prevents automated bot activity

✅ **Search Functionality**: Search businesses by name, category, or address

✅ **Interactive CLI**: User-friendly command-line interface with intuitive menus

## Requirements

- Python 3.6 or higher
- No external dependencies required (uses only Python standard library)

## Installation

1. Clone or download this repository:
```bash
git clone <repository-url>
cd FBLACP2526
```

2. Make the script executable (optional):
```bash
chmod +x business_boost.py
```

## Usage

### Running the Application

Simply run the Python script:

```bash
python3 business_boost.py
```

Or if you made it executable:

```bash
./business_boost.py
```

### Main Menu Options

1. **Browse All Businesses**: View all businesses in the directory
2. **Browse by Category**: Filter businesses by category (food, retail, services)
3. **Search Businesses**: Search by name, category, or address
4. **View Top Rated Businesses**: See businesses sorted by highest average rating
5. **View Most Reviewed Businesses**: See businesses with the most reviews
6. **Leave a Review**: Add a review and rating to a business (verification required)
7. **My Favorites**: View and manage your bookmarked businesses
8. **Add New Business**: Add a new business to the directory (verification required)
9. **View Business Details**: See full details including deals and reviews
0. **Exit**: Quit the application

### Key Features Explained

#### Bot Verification
When adding a business or leaving a review, you'll be asked to solve a simple math problem. This helps prevent automated bot activity and ensures genuine user interactions.

#### Reviews & Ratings
- Ratings are on a scale of 1-5 stars
- Reviews include the user's name, rating, comment, and timestamp
- Only verified reviews (after passing verification) are accepted
- Average ratings are calculated automatically

#### Favorites
- Save businesses to your personal favorites list
- Access your favorites anytime from the main menu
- Remove businesses from favorites when needed

#### Deals & Coupons
- Each business can have multiple deals/coupons
- Deals include title, description, and expiration date
- View deals when browsing business details

## Data Storage

The application stores all data in a JSON file (`business_data.json`) in the same directory. This file contains:
- All business information
- Reviews and ratings
- User favorites

The data persists between sessions, so your reviews and favorites are saved automatically.

## Sample Data

The application comes pre-loaded with sample businesses across different categories to help you get started:
- Coffee shops and restaurants (food)
- Bookstores and garden centers (retail)
- Auto repair and other services (services)

## Example Workflow

1. **Start the application**: `python3 business_boost.py`
2. **Enter your name** when prompted
3. **Browse businesses** by category or view all
4. **View business details** to see deals and reviews
5. **Add to favorites** for businesses you like
6. **Leave a review** to share your experience
7. **Add new businesses** you discover in your community

## Project Structure

```
FBLACP2526/
├── business_boost.py      # Main application file
├── business_data.json     # Data storage (created on first run)
└── README.md              # This file
```

## Technical Details

- **Language**: Python 3
- **Storage**: JSON file-based storage
- **Architecture**: Object-oriented design with Business and BusinessBoost classes
- **Verification**: Simple math-based CAPTCHA system
- **Interface**: Interactive command-line interface

## Future Enhancements

Potential improvements could include:
- Web interface version
- Database integration (SQLite, PostgreSQL)
- Email verification for reviews
- Business owner accounts
- Photo uploads
- Advanced search filters
- Location-based sorting
- Export favorites to PDF/CSV

## License

This project is open source and available for educational and personal use.

## Contributing

Feel free to fork this project and add your own features or improvements!

---

**Support Local Businesses!** 🏪❤️
