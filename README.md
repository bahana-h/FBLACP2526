# Chrysalis Connect

Here at Chrysalis Connect, our mission is to ensure that all local small businesses are able to be seen by the public because we believe that “Behind every small business, there’s a story worth knowing.” - Paul Ryan

Live site (GitHub Pages):
https://bahana-h.github.io/FBLACP2526/

## Mascot!!!

![Alt Text](C:\Users\henryw\Downloads\Chrysalis Connect Logo Picture.png)

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

## Project structure

- app.py: Flask app entry point
- backend/: backend modules (models, validators, recommendations, reviews store)
- docs/: GitHub Pages frontend files
- templates/: Flask templates
- static/: Flask static files
- requirements.txt: Python dependencies

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


