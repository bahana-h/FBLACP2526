# Chrysalis Connect

Here at Chrysalis Connect, our mission is to ensure that all local small businesses are able to be seen by the public because we believe that “Behind every small business, there’s a story worth knowing.” - Paul Ryan

Live site (GitHub Pages):
https://bahana-h.github.io/FBLACP2526/

## Mascot!!!

![Alt Text](assets/Chrysalis%20Connect%20Logo%20Picture.png)

Our story lies with a red-spotted purple butterfly whose transformation in a chrysalis is similar to businesses in that with the right platform to support it, every business can grow, be discovered, and thrive.

## What this project does

- Search businesses by location
- Filter by category and sort by rating/reviews
- Save favorites
- Add reviews
- View map, Q&A page, and reports page
- Optionally sync reviews through our backend (Render + Supabase)

## Tech we used

- Frontend: HTML, CSS, JavaScript
- Backend: Python + Flask
- Database for shared reviews: Supabase
- Hosting:
  - Frontend on GitHub Pages
  - Backend on Render
- Server monitoring: Uptime Robot

## Project structure

- app.py: Flask app entry point
- backend/: backend modules (models, validators, recommendations, reviews store)
- docs/: GitHub Pages frontend files
- templates/: Flask templates
- static/: Flask static files
- requirements.txt: Python dependencies

### File guide (what each major file does)

- app.py
  - Main Flask server.
  - Renders template pages and handles form routes.
  - Exposes API endpoints such as shared review routes.

- backend/models.py
  - Defines Business objects and the BusinessBoost manager class.
  - Holds in-memory business/review/favorite logic for the Flask app.

- backend/validators.py
  - Validation helpers for user input (business fields, review data, verification).

- backend/recommendations.py
  - Ranking and recommendation helpers (personalized/trending/similar logic).

- backend/reviews_store.py
  - Shared review persistence layer.
  - Uses Supabase if configured, otherwise falls back to local JSON storage.

- docs/index.html
  - Main static frontend page served by GitHub Pages.

- docs/assets/app.js
  - Core frontend app logic.
  - Performs location search, OpenStreetMap calls, filtering/sorting, rendering, and local storage sync.

- docs/assets/qa.js
  - Q&A feature logic using a keyword-scoring matcher over a local knowledge base.

- docs/assets/map-page.js
  - Map page behavior and business marker rendering.

- templates/
  - Flask/Jinja templates for server-rendered backend pages.

- static/
  - CSS/JS assets used by Flask-rendered templates.

## Architecture notes

This repo contains two UI paths:

1. Static frontend path (GitHub Pages)
   - Uses files in docs/ and docs/assets/.
   - Makes OpenStreetMap API calls from the browser.
   - Stores loaded business state in browser storage.

2. Flask-rendered path (Python backend)
   - Uses app.py + templates/ + static/.
   - Handles server-side rendering and form-driven flows.

Because both paths exist, some features are shared in concept but implemented
slightly differently between static and Flask pages.

## Data flow summary

1. User enters a location on the static frontend.
2. Frontend geocodes with Nominatim, then fetches nearby places via Overpass.
3. Businesses are normalized into the frontend state.businesses array.
4. Optional: reviews can be synced through backend shared-review endpoints.
5. UI renders cards, details, map markers, and reports from current state.

## Run locally

1. Install dependencies

pip install -r requirements.txt

2. Start the backend

python app.py

3. Open in browser

http://localhost:5000

## Deploy notes

### GitHub Pages

The static site is in the docs folder. Push to main and Pages serves it from docs.

### Render backend

Use a Python web service with:

- Build command: pip install -r requirements.txt
- Start command: python app.py

Then set env vars in Render (SUPABASE_URL and SUPABASE_KEY).

## Notes

- The GitHub Pages frontend and Render backend can look different. That is expected.
- The frontend can still call the Render API for shared reviews.

## Credits

Made with love for local businesses.

Made by Henry Wang and Hanyu Zhang from Lynbrook High School.


