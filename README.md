# Byte-Sized Business Boost 🌟

A modern web application built with Flask that helps users discover and support small, local businesses in their community. Features a clean, responsive UI with all the functionality you need to explore local businesses, leave reviews, manage favorites, and discover special deals.

## Features

✅ **Category-Based Sorting**: Browse businesses by category (food, retail, services)

✅ **Review & Rating System**: Leave reviews and ratings for businesses with bot verification

✅ **Smart Sorting**: Sort businesses by average rating or number of reviews

✅ **Favorites Management**: Save and bookmark your favorite local businesses

✅ **Deals & Coupons**: View special deals and promotional offers from businesses

✅ **Bot Verification**: Simple math verification prevents automated bot activity

✅ **Search Functionality**: Search businesses by name, category, or address

✅ **Modern Web UI**: Beautiful, responsive design that works on all devices

✅ **Real-time Updates**: All changes are saved instantly

## Requirements

- Python 3.6 or higher
- Flask 3.0.0+ (see requirements.txt)

## Installation

1. Clone or download this repository:
```bash
git clone <repository-url>
cd FBLACP2526
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Web Application

1. Start the Flask development server:
```bash
python3 app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

The application will automatically create sample data on first run if no data file exists.

## Usage Guide

### Getting Started

1. **Enter Your Name**: Click on the username field in the navigation bar and enter your name to personalize your experience.

2. **Browse Businesses**: 
   - View all businesses on the home page
   - Use filters to search by category, name, or address
   - Sort by name, rating, or number of reviews

3. **View Business Details**: Click on any business card to see:
   - Full business information
   - Current deals and coupons
   - Reviews and ratings from other users
   - Option to add to favorites

4. **Leave Reviews**: 
   - Navigate to a business detail page
   - Fill out the review form with your rating (1-5 stars) and comment
   - Complete the verification to submit your review

5. **Manage Favorites**: 
   - Click the heart icon on any business detail page
   - View all your favorites from the "Favorites" link in the navigation
   - Remove businesses from favorites anytime

6. **Add New Businesses**: 
   - Click "Add Business" in the navigation
   - Fill out the business information
   - Optionally add deals or coupons
   - Complete verification to submit

### Key Features Explained

#### Bot Verification
When adding a business or leaving a review, you'll be asked to solve a simple math problem. This helps prevent automated bot activity and ensures genuine user interactions.

#### Reviews & Ratings
- Ratings are on a scale of 1-5 stars with visual star display
- Reviews include the user's name, rating, comment, and timestamp
- Only verified reviews (after passing verification) are accepted
- Average ratings are calculated automatically and displayed prominently

#### Favorites
- Save businesses to your personal favorites list
- Access your favorites from the navigation menu
- Remove businesses from favorites when needed
- Favorites are saved per user session

#### Deals & Coupons
- Each business can have multiple deals/coupons
- Deals include title, description, and expiration date
- Deals are displayed prominently on business detail pages
- Special styling highlights available deals

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

## Project Structure

```
FBLACP2526/
├── app.py                  # Flask web application
├── models.py               # Business and BusinessBoost classes
├── business_boost.py      # Original CLI version (still available)
├── requirements.txt        # Python dependencies
├── business_data.json      # Data storage (created on first run)
├── templates/              # HTML templates
│   ├── base.html          # Base template with navigation
│   ├── index.html         # Home page with business listings
│   ├── business_detail.html # Individual business detail page
│   ├── favorites.html     # User favorites page
│   └── add_business.html  # Add new business form
├── static/                 # Static files
│   ├── css/
│   │   └── style.css      # Main stylesheet
│   └── js/
│       └── main.js        # JavaScript for interactivity
└── README.md              # This file
```

## Technical Details

- **Backend**: Flask (Python web framework)
- **Frontend**: HTML5, CSS3, JavaScript
- **Storage**: JSON file-based storage
- **Architecture**: MVC pattern with Flask routes, templates, and models
- **Verification**: Simple math-based CAPTCHA system
- **UI Framework**: Custom CSS with modern design principles
- **Icons**: Font Awesome 6.4.0

## Development

### Running in Development Mode

The app runs in debug mode by default. To disable debug mode, modify `app.py`:

```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

### Customization

- **Colors**: Modify CSS variables in `static/css/style.css` (`:root` section)
- **Port**: Change the port in `app.py` (default: 5000)
- **Data File**: Change `data_file` parameter in `BusinessBoost` class initialization

## Browser Compatibility

The application works on all modern browsers:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## Future Enhancements

Potential improvements could include:
- User authentication and accounts
- Database integration (SQLite, PostgreSQL)
- Email verification for reviews
- Business owner accounts
- Photo uploads
- Advanced search filters with location
- Map integration
- Export favorites to PDF/CSV
- REST API endpoints
- Real-time notifications

## License

This project is open source and available for educational and personal use.

## Contributing

Feel free to fork this project and add your own features or improvements!

---

**Support Local Businesses!** 🏪❤️
