# Coding & Programming Presentation — Rating Sheet Alignment

This document maps **Chrysalis Connect** (the GitHub Pages site in `docs/`) to each expectation on the Coding & Programming rating sheet so judges and presenters can see how the project meets or exceeds criteria.

---

## Code Quality

### 1. Language Selection (Industry terms; reflects project needs)

**Languages and technologies used:**

| Choice | Industry rationale |
|--------|---------------------|
| **HTML5** | Semantic structure, accessibility (ARIA, landmarks), and clear document outline for assistive technologies and SEO. |
| **CSS3** | Layout (Grid, Flexbox), custom properties (design tokens), responsive breakpoints, and print media for reports. |
| **JavaScript (ES6+)** | Client-side logic with no server required: single-page behavior, localStorage persistence, and modular scripts (IIFEs) to avoid global scope pollution. |

**Why this stack fits the project:**

- **Static hosting (e.g. GitHub Pages):** No backend or API key is required for core use. The app runs entirely in the browser (client-side rendering).
- **Progressive enhancement:** Core content is in HTML; JavaScript adds interactivity (filters, modals, map). If JS is slow or disabled, structure and navigation still work.
- **Maintainability:** Separation of concerns—HTML (structure), CSS (presentation), JS (behavior)—and one script per major feature (app.js, qa.js, reports.js, add-business.js, map-page.js) support readable, maintainable code.

**Where to show:** README “How to view the site” and project structure; this section in PRESENTATION.md.

---

### 2. Code Comments (Complete, logical, enhance readability)

- **Section comments** in `docs/assets/app.js` separate state, persistence, geolocation, filters/render, and event binding. Key functions have one-line descriptions (e.g. what `loadState`, `filteredBusinesses`, `openDetails` do).
- **File-level comments** in `docs/assets/qa.js`, `reports.js`, `add-business.js`, and `map-page.js` describe each script’s role. Functions that drive behavior (e.g. `getAnswers`, `buildReport`, form submit, map markers) are commented.
- **CSS** (`docs/assets/styles.css`) has block comments for design tokens, base layout, navbar, hero/directory, filters, business cards, detail modal, Help modal, map page, Q&A page, Add Business page, Reports page, and print.
- **HTML** pages include short comments for main sections (e.g. directory, filters, business list, modals, templates) and how they are filled by JavaScript.

Comments focus on **purpose** and **data flow** so future changes and judging are easier.

**Where to show:** Any of `docs/assets/app.js`, `qa.js`, `reports.js`, `add-business.js`, `map-page.js`, `styles.css`, and `docs/*.html`.

---

### 3. Programming Knowledge (Modular design, clean logic, effective data types)

- **Modular design:**  
  - `app.js`: main directory, state, filters, render, detail modal, shared reviews, geolocation, OSM.  
  - `qa.js`: knowledge base and matching only.  
  - `reports.js`: read from storage, compute stats, build report, print/download.  
  - `add-business.js`: form and localStorage write.  
  - `map-page.js`: read storage, filter by lat/lon, Leaflet map and markers.  
  Each file has a single responsibility and is loaded only on the pages that need it.

- **Clean logic:**  
  - State in one place (`state` in app.js: businesses, favorites, filters, view).  
  - Render path: `filteredBusinesses()` → `render()` → `cardForBusiness()` / detail HTML.  
  - No duplicate business-load logic; shared helpers (`averageRating`, `totalReviews`, `escapeHtml`) reused where needed.

- **Effective data types:**  
  - **Arrays:** `state.businesses`, `biz.reviews`, `biz.deals`; used for ordered lists and iteration.  
  - **Set:** `state.favorites` for O(1) membership and no duplicates.  
  - **Map:** In `mergeLocalReviewsInto`, a `Map` keyed by business id for fast lookup when merging.  
  - **Objects:** `state.filters`, `stored` (businesses + favorites), and business records with consistent shape (id, name, category, address, etc.).

**Where to show:** Structure of `docs/assets/*.js`, `state` and `filteredBusinesses()` in app.js, `getStored()` and list handling in reports.js and map-page.js.

---

## User Experience

### 4. UX Design (User journey, design rationale, accessibility)

- **User journey:**  
  1. **Landing** → value proposition and “Explore” / “Use My Location.”  
  2. **Directory** → location search or use current location → list with filters (search, category, sort) and stats.  
  3. **Detail** → click card → modal with info, deals, similar businesses, reviews, and “Add a Review.”  
  4. **Favorites / Recommendations** → from nav; same list UI with different data.  
  5. **Add Business, Map, Q&A, Reports** → clear nav links and back to directory.

- **Design rationale:**  
  - **Butterfly/chrysalis theme:** Visual identity and “growth” metaphor; gradient nav and card layout for clarity.  
  - **Card layout:** Scannable list; each card shows name, category, address, rating, deals, favorite, and “Details.”  
  - **Single detail modal:** Stay on the same page; less context switching.

- **Accessibility:**  
  - Semantic HTML (header, main, section, nav, article, labels).  
  - ARIA where needed (e.g. `aria-live` for dynamic list title, `aria-hidden` for decorative 3D scene, `aria-label` for close buttons).  
  - Focus and keyboard: buttons and links are focusable; modal can be closed via button or overlay.  
  - Star rating: `aria-label` with numeric value (e.g. “4.3 out of 5 stars”).  
  - Form labels and required fields and placeholders to guide input.

**Where to show:** `docs/index.html` (landing, directory, modals), `docs/assets/styles.css` (layout and theme), and this UX section.

---

### 5. Program Intuitiveness (Easy to navigate; clear instructions)

- **Navigation:**  
  - Persistent nav: Recommendations, Favorites, Shared Reviews, Map, Help, Q&A, Reports, Add Business.  
  - Same nav pattern on index, map, add-business, qa, reports with “Back” or “Explore” to return.

- **Instructions:**  
  - **Help modal** (nav → Help): “How to Use Chrysalis Connect” with short sections (Explore, Shared Reviews, Favorites, Reviews, Add Business, Recommendations, Map, Q&A, Reports).  
  - **Q&A page:** Placeholder and hint (e.g. try “reviews”, “map”, “favorites”) so users know they can type natural questions.  
  - **Add Business:** Labels and “*” for required fields; verification question and inline error message.  
  - **Reports:** Toolbar labels (Category, Sort), Refresh, Print, Download; summary and table make the output clear.

- **No spelling or navigation errors:** Copy is proofread; links and buttons are consistent and correct.

**Where to show:** Nav and Help modal on index; Q&A page; Add Business form; Reports toolbar and output.

---

### 6. Intelligent Feature (e.g. Q&A, recommendations, smart filters)

- **Interactive Q&A** (`docs/qa.html`, `docs/assets/qa.js`):  
  - User types a question; the app scores it against a knowledge base (exact match, phrase overlap, keyword phrases).  
  - Top 1–3 answers are shown; suggested question buttons prefill and run the same matching.  
  - Demonstrates a non-trivial, user-facing “intelligent” feature.

- **Recommendations:**  
  - Nav → “Recommendations” shows the same directory list sorted by rating (top-rated and trending from current data).  
  - In the detail modal, “Similar businesses” shows same-category businesses sorted by rating (content-based suggestion).

- **Smart filtering:**  
  - **Category:** Dropdown or pills (Food, Retail, Services).  
  - **Text search:** Filters by name, category, or address (case-insensitive, partial match).  
  - **Sort:** Name, Highest Rated, Most Reviewed.  
  - Filters and sort are combined (e.g. category + search + sort) for focused results.

**Where to show:** Q&A page; Recommendations view and Similar businesses in detail modal; filters and sort on directory.

---

### 7. User Input Validation (Format and meaning; prevents crashes; helpful errors)

- **Syntactical (format):**  
  - Required fields: Add Business (name, address); review form (verification answer).  
  - Trim: All relevant text inputs are `.trim()`’d before use.  
  - Category: Restricted to options (food, retail, services) in dropdown.  
  - Rating: Select 1–5 in review form (no free text).

- **Semantic (meaning):**  
  - **Verification (captcha):** Add Business and Add Review require the correct math answer before submit; wrong answer shows “Verification failed. Please try again.”  
  - **Presence:** “Please enter a business name.” / “Please enter an address.” when required fields are empty.  
  - **Location:** If geocoding or search fails, a status message is shown (e.g. “Could not find location…”) and the app falls back to sample data instead of crashing.

- **Error handling:**  
  - Add Business: `formError` element shows one message at a time; no alert stack.  
  - Review in modal: Alert for verification failure; success path updates modal and list.  
  - Network/API errors: Caught, message shown, fallback data used so the app remains usable.

**Where to show:** `docs/assets/add-business.js` (required fields, captcha, showError); app.js review submit (captcha, trim); app.js search/geocode (try/catch and status messages).

---

## Functionality

### 8. Functionality & Relevance (Fully meets prompt; instructions explain how program addresses the topic)

- **Topic:** Local business discovery and support—browse, search, filter, sort, view details, add businesses, leave reviews, save favorites, see recommendations, map, and reports.

- **How the program addresses it:**  
  - **Discovery:** Location-based search (OpenStreetMap/Nominatim), category and text filters, and sort by name/rating/reviews.  
  - **Support:** Reviews and ratings, favorites, deals on businesses, and Add Business for user-contributed listings.  
  - **Analysis:** Reports page with summary stats and a customizable, printable, and downloadable table.

- **Instructions:**  
  - README describes features and how to view the site (GitHub Pages or local).  
  - In-app Help modal explains each feature (Explore, Shared Reviews, Favorites, Reviews, Add Business, Recommendations, Map, Q&A, Reports).  
  - Q&A page answers common “how do I…?” questions.  
  - Add Business and Reports use clear labels and buttons.

**Where to show:** README, Help modal, Q&A page, and this section.

---

### 9. Output & Data Analysis (Customizable reports; meaningful analysis)

- **Reports page** (`docs/reports.html`, `docs/assets/reports.js`):  
  - **Summary:** Total businesses, total reviews, average rating, “In this view” count, number of categories.  
  - **Table:** Business name, category, rating, review count, address for each business in the current view.  
  - **Customization:** Category filter (All, Food, Retail, Services) and Sort (Name, Highest rated, Most reviewed).  
  - **Output:** Print (print-friendly CSS hides nav/toolbar) and Download (tab-separated .txt with same data and filters).

- **Meaningful analysis:** Users can see directory size, review activity, and average quality; filter by category and sort to compare businesses and focus on high-rated or most-reviewed ones.

**Where to show:** Reports page (toolbar, summary boxes, table, Print and Download buttons) and `reports.js` (`buildReport`, `printReport`, `downloadReport`).

---

## Data Storage

### 10. Data Structures & Scope (Arrays/lists used appropriately; variable scope logical and efficient)

- **Data structures:**  
  - **Arrays:** `state.businesses`, `stored.businesses`, `biz.reviews`, `biz.deals`; used for ordered sequences and `.filter()`, `.sort()`, `.map()`.  
  - **Set:** `state.favorites` (business IDs); O(1) add/delete/has; no duplicates.  
  - **Map:** In `mergeLocalReviewsInto()`, `Map` from business id → business for fast lookup when merging previous reviews into new search results.  
  - **Objects:** `state`, `state.filters`, each business record; consistent property names (id, name, category, address, phone, description, deals, reviews, latitude, longitude, etc.).

- **Persistence:**  
  - Single key `cc-data` in localStorage: `{ businesses: [...], favorites: [...] }`.  
  - Read on load (`loadState`, `getStored` in reports/add-business/map); write on change (`saveState`, `setStored`).

- **Scope:**  
  - **app.js:** `state` and `els` at script top level; helpers and handlers in functions; no unnecessary globals.  
  - **qa.js, reports.js, add-business.js, map-page.js:** Wrapped in IIFEs so all variables are function-scoped and do not pollute the global object.  
  - Event handlers close over the data they need (e.g. `biz` in card click, `answer` in review submit).

**Where to show:** `state` and `filteredBusinesses()` in app.js; `mergeLocalReviewsInto` (Map); `getStored` / `setStored` and list handling in reports.js and add-business.js; IIFE wrappers in qa.js, reports.js, add-business.js, map-page.js.

---

## Presentation Delivery (Reminders)

- **Organization:** Use this document as a roadmap: go through each numbered item and point to the corresponding part of the project (file, feature, or UI).  
- **Confidence and delivery:** Rehearse the flow (language → comments → modularity → UX → intuitiveness → Q&A/recommendations/filters → validation → functionality → reports → data structures).  
- **Q&A:** Be ready to give a one-sentence answer for each criterion (e.g. “We use a Set for favorites for O(1) lookup and no duplicates” or “Validation is both syntactical—required fields and trim—and semantic—captcha and clear error messages”).

---

**Summary:** Chrysalis Connect is a client-side web application (HTML, CSS, JavaScript) for local business discovery. It uses modular scripts, clear comments, and appropriate data structures (arrays, Set, Map); validates input in both format and meaning; provides an intuitive UI with Help and Q&A; includes intelligent features (Q&A matching, recommendations, smart filters); and delivers customizable reports for data analysis, aligned with the Coding & Programming rating sheet expectations.
