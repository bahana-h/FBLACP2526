// Byte-Sized Business Boost - Real Local Business Finder
// Uses Google Places API (works directly in browser - no backend needed!)

// Sample businesses as fallback
const sampleBusinesses = [
  {
    id: "joescoffee",
    name: "Joe's Coffee House",
    category: "food",
    address: "123 Main St, Downtown",
    phone: "555-0101",
    description: "Cozy local coffee shop with artisanal brews and fresh pastries.",
    deals: [{ title: "Buy 2 Get 1 Free", description: "Any coffee drinks", expires: "2024-12-31" }],
    reviews: [
      { user_name: "Ava", rating: 5, comment: "Best latte in town!", date: "2024-01-12" },
      { user_name: "Liam", rating: 4, comment: "Great vibe and friendly staff.", date: "2024-02-03" }
    ]
  }
];

const state = {
  businesses: [],
  favorites: new Set(),
  filters: { search: "", category: "", sort: "name" },
  currentLocation: null,
  apiKey: null,
  loading: false,
  placesService: null,
  map: null
};

const els = {};

function qs(id) {
  return document.getElementById(id);
}

// API Key Management
function loadApiKey() {
  const stored = localStorage.getItem("bsbb-google-api-key");
  if (stored) {
    state.apiKey = stored;
    qs("apiKeyBanner").style.display = "none";
    initializeGooglePlaces();
    return true;
  }
  qs("apiKeyBanner").style.display = "block";
  return false;
}

function saveApiKey(key) {
  state.apiKey = key;
  localStorage.setItem("bsbb-google-api-key", key);
  qs("apiKeyBanner").style.display = "none";
  qs("apiKeyModal").style.display = "none";
  
  // Update the Google Maps script with new API key
  const script = document.querySelector('script[src*="maps.googleapis.com"]');
  if (script) {
    script.src = script.src.replace(/key=[^&]+/, `key=${key}`);
  } else {
    // Add script if it doesn't exist
    const newScript = document.createElement('script');
    newScript.src = `https://maps.googleapis.com/maps/api/js?key=${key}&libraries=places&callback=initializeGooglePlaces`;
    newScript.async = true;
    newScript.defer = true;
    document.head.appendChild(newScript);
  }
  
  initializeGooglePlaces();
  if (state.currentLocation) {
    searchBusinesses(state.currentLocation);
  }
}

function initializeGooglePlaces() {
  if (!state.apiKey || typeof google === 'undefined' || !google.maps) {
    return;
  }
  
  // Initialize a hidden map (required for PlacesService)
  if (!state.map) {
    state.map = new google.maps.Map(document.createElement('div'));
  }
  
  if (!state.placesService) {
    state.placesService = new google.maps.places.PlacesService(state.map);
  }
}

// Make initializeGooglePlaces available globally for callback
window.initializeGooglePlaces = initializeGooglePlaces;

function showApiKeyModal() {
  qs("apiKeyModal").style.display = "flex";
  qs("apiKeyInput").value = state.apiKey || "";
}

function hideApiKeyModal() {
  qs("apiKeyModal").style.display = "none";
}

// Geolocation
function getCurrentLocation() {
  if (!navigator.geolocation) {
    showStatus("Geolocation is not supported by your browser.", "error");
    return;
  }

  showStatus("Getting your location...", "info");
  state.loading = true;

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const location = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
      };
      state.currentLocation = location;
      showStatus(`Location found! Searching nearby businesses...`, "success");
      searchBusinesses(location);
    },
    (error) => {
      showStatus("Could not get your location. Please enter a location manually.", "error");
      state.loading = false;
    }
  );
}

function searchByLocationText() {
  const locationText = qs("locationInput").value.trim();
  if (!locationText) {
    showStatus("Please enter a location.", "error");
    return;
  }

  state.currentLocation = locationText;
  showStatus(`Searching businesses in ${locationText}...`, "info");
  searchBusinesses(locationText);
}

// Google Places API Integration
function searchBusinesses(location) {
  if (!state.apiKey) {
    showStatus("Please enter your Google Places API key to search for businesses.", "error");
    showApiKeyModal();
    return;
  }

  if (!state.placesService) {
    showStatus("Initializing Google Places...", "info");
    initializeGooglePlaces();
    if (!state.placesService) {
      showStatus("Google Places API not loaded. Please check your API key.", "error");
      return;
    }
  }

  state.loading = true;
  showStatus("Searching for local businesses...", "info");

  // Build search request
  const request = {
    query: getSearchQuery(),
    fields: ['name', 'formatted_address', 'formatted_phone_number', 'rating', 'user_ratings_total', 'types', 'place_id', 'geometry'],
    locationBias: typeof location === 'string' ? undefined : new google.maps.LatLng(location.latitude, location.longitude)
  };

  // If location is a string, use it as query
  if (typeof location === 'string') {
    request.query = `${getSearchQuery()} in ${location}`;
  }

  state.placesService.textSearch(request, (results, status) => {
    if (status === google.maps.places.PlacesServiceStatus.OK && results) {
      // Transform Google Places data to our format
      state.businesses = results.map(place => ({
        id: place.place_id,
        name: place.name,
        category: mapGoogleCategory(place.types),
        address: place.formatted_address || 'Address not available',
        phone: place.formatted_phone_number || 'No phone listed',
        description: place.types ? place.types.slice(0, 3).join(', ') : '',
        rating: place.rating || 0,
        review_count: place.user_ratings_total || 0,
        latitude: place.geometry?.location?.lat(),
        longitude: place.geometry?.location?.lng(),
        deals: [], // Users can add deals
        reviews: [] // We'll use Google's review count, but store our own reviews
      }));

      showStatus(`Found ${state.businesses.length} businesses!`, "success");
      buildCategories();
      render();
      state.loading = false;
    } else if (status === google.maps.places.PlacesServiceStatus.ZERO_RESULTS) {
      showStatus("No businesses found. Try a different location.", "error");
      state.businesses = sampleBusinesses;
      buildCategories();
      render();
      state.loading = false;
    } else {
      console.error("Places API error:", status);
      showStatus(`Error: ${status}. Using sample data.`, "error");
      state.businesses = sampleBusinesses;
      buildCategories();
      render();
      state.loading = false;
    }
  });
}

function getSearchQuery() {
  // Build search query based on category filter
  const categoryMap = {
    'food': 'restaurant cafe food',
    'retail': 'store shop retail',
    'services': 'service business'
  };
  
  if (state.filters.category && categoryMap[state.filters.category]) {
    return categoryMap[state.filters.category];
  }
  
  return 'local business small business';
}

function mapGoogleCategory(types) {
  if (!types || types.length === 0) return 'services';
  
  const typeStr = types.join(' ').toLowerCase();
  
  if (typeStr.includes('restaurant') || typeStr.includes('food') || 
      typeStr.includes('cafe') || typeStr.includes('meal') ||
      typeStr.includes('bakery') || typeStr.includes('bar')) {
    return 'food';
  }
  if (typeStr.includes('store') || typeStr.includes('shop') ||
      typeStr.includes('retail') || typeStr.includes('market') ||
      typeStr.includes('shopping')) {
    return 'retail';
  }
  return 'services';
}

function showStatus(message, type = 'info') {
  const statusEl = qs("locationStatus");
  statusEl.textContent = message;
  statusEl.className = `location-status status-${type}`;
  
  if (type === 'success') {
    setTimeout(() => {
      statusEl.textContent = '';
      statusEl.className = 'location-status';
    }, 3000);
  }
}

function loadState() {
  const stored = localStorage.getItem("bsbb-data");
  if (stored) {
    try {
      const parsed = JSON.parse(stored);
      state.businesses = parsed.businesses || [];
      state.favorites = new Set(parsed.favorites || []);
    } catch (e) {
      console.warn("Failed to parse stored data", e);
    }
  }
  
  // If no businesses loaded and we have location, search
  if (state.businesses.length === 0 && state.currentLocation) {
    // Wait a bit for Google Maps to load
    setTimeout(() => {
      if (state.placesService) {
        searchBusinesses(state.currentLocation);
      }
    }, 1000);
  } else if (state.businesses.length === 0) {
    state.businesses = sampleBusinesses;
  }
}

function saveState() {
  localStorage.setItem(
    "bsbb-data",
    JSON.stringify({ businesses: state.businesses, favorites: Array.from(state.favorites) })
  );
}

function averageRating(biz) {
  // Use Google rating if available, otherwise calculate from reviews
  if (biz.rating !== undefined) {
    return biz.rating;
  }
  if (!biz.reviews || !biz.reviews.length) return 0;
  return biz.reviews.reduce((a, r) => a + (r.rating || 0), 0) / biz.reviews.length;
}

function totalReviews(biz) {
  // Use Google review count if available
  if (biz.review_count !== undefined) {
    return biz.review_count + (biz.reviews?.length || 0);
  }
  return biz.reviews?.length || 0;
}

function renderStats() {
  qs("statBusinesses").textContent = state.businesses.length;
  const allReviews = state.businesses.reduce((a, b) => a + totalReviews(b), 0);
  qs("statReviews").textContent = allReviews;
  const rated = state.businesses.filter(b => totalReviews(b) > 0);
  const avg = rated.length === 0 ? 0 : rated.reduce((a, b) => a + averageRating(b), 0) / rated.length;
  qs("statRating").textContent = avg.toFixed(1);
}

function buildCategories() {
  const select = qs("category");
  const pills = qs("categoryPills");
  select.innerHTML = `<option value="">All Categories</option>`;
  pills.innerHTML = "";
  const cats = Array.from(new Set(state.businesses.map(b => b.category))).sort();
  cats.forEach(cat => {
    const opt = document.createElement("option");
    opt.value = cat;
    opt.textContent = cat[0].toUpperCase() + cat.slice(1);
    select.appendChild(opt);

    const pill = document.createElement("button");
    pill.className = "pill";
    pill.dataset.cat = cat;
    pill.textContent = opt.textContent;
    pill.addEventListener("click", () => {
      state.filters.category = state.filters.category === cat ? "" : cat;
      updateFiltersUI();
      render();
      // Re-search if we have a location
      if (state.currentLocation) {
        searchBusinesses(state.currentLocation);
      }
    });
    pills.appendChild(pill);
  });
}

function updateFiltersUI() {
  qs("search").value = state.filters.search;
  qs("category").value = state.filters.category;
  qs("sort").value = state.filters.sort;
  document.querySelectorAll(".pill").forEach(p => {
    p.classList.toggle("active", p.dataset.cat === state.filters.category);
  });
}

function filteredBusinesses() {
  let list = [...state.businesses];
  const { search, category, sort } = state.filters;

  if (category) list = list.filter(b => b.category === category);

  if (search) {
    const term = search.toLowerCase();
    list = list.filter(
      b =>
        b.name.toLowerCase().includes(term) ||
        b.address.toLowerCase().includes(term) ||
        b.category.toLowerCase().includes(term)
    );
  }

  if (sort === "rating") {
    list.sort((a, b) => averageRating(b) - averageRating(a));
  } else if (sort === "reviews") {
    list.sort((a, b) => totalReviews(b) - totalReviews(a));
  } else {
    list.sort((a, b) => a.name.localeCompare(b.name));
  }

  return list;
}

function render() {
  renderStats();
  updateFiltersUI();
  const list = qs("businessList");
  list.innerHTML = "";
  
  if (state.loading) {
    list.innerHTML = `<div class="empty"><i class="fas fa-spinner fa-spin"></i> Loading businesses...</div>`;
    return;
  }
  
  const data = filteredBusinesses();
  if (!data.length) {
    list.innerHTML = `<div class="empty">No businesses found. ${state.apiKey ? 'Try another search or location.' : 'Enter your Google Places API key to search for real businesses.'}</div>`;
    return;
  }
  data.forEach(biz => list.appendChild(cardForBusiness(biz)));
}

function cardForBusiness(biz) {
  const tpl = document.getElementById("businessCardTemplate").content.cloneNode(true);
  tpl.querySelector(".card-title").textContent = biz.name;
  const badge = tpl.querySelector(".category-badge");
  badge.textContent = biz.category;
  badge.classList.add(`category-${biz.category}`);
  tpl.querySelector(".address").textContent = biz.address;
  tpl.querySelector(".phone").textContent = biz.phone || "No phone listed";
  tpl.querySelector(".description").textContent = biz.description || "";

  const rating = averageRating(biz);
  const rc = totalReviews(biz);
  tpl.querySelector(".rating-row").innerHTML = `
    <span class="stars">${"★".repeat(Math.round(rating))}${"☆".repeat(5 - Math.round(rating))}</span>
    <span>${rating.toFixed(1)} / 5 (${rc} review${rc === 1 ? "" : "s"})</span>
  `;

  const dealRow = tpl.querySelector(".deal-row");
  if (biz.deals?.length) {
    biz.deals.forEach(d => {
      const pill = document.getElementById("dealTemplate").content.cloneNode(true);
      pill.querySelector(".deal-text").textContent = `${d.title} • ${d.description}`;
      dealRow.appendChild(pill);
    });
  }

  const favBtn = tpl.querySelector(".favorite-btn");
  const icon = favBtn.querySelector("i");
  const syncFav = () => {
    const isFav = state.favorites.has(biz.id);
    icon.className = isFav ? "fas fa-heart" : "far fa-heart";
    favBtn.classList.toggle("active", isFav);
  };
  favBtn.addEventListener("click", () => {
    if (state.favorites.has(biz.id)) state.favorites.delete(biz.id);
    else state.favorites.add(biz.id);
    saveState();
    syncFav();
  });
  syncFav();

  tpl.querySelector(".details-btn").addEventListener("click", () => openDetails(biz.id));

  return tpl;
}

function openDetails(id) {
  const biz = state.businesses.find(b => b.id === id);
  if (!biz) return;
  const modal = qs("modal");
  const content = qs("modalContent");
  content.innerHTML = `
    <button class="modal-close" id="modalClose">&times;</button>
    <div class="detail-header">
      <div>
        <div class="pill-inline category-${biz.category}">${biz.category}</div>
        <h2>${biz.name}</h2>
        <div class="rating-row">
          <span class="stars">${"★".repeat(Math.round(averageRating(biz)))}${"☆".repeat(5 - Math.round(averageRating(biz)))}</span>
          <span>${averageRating(biz).toFixed(1)} / 5 (${totalReviews(biz)} reviews)</span>
        </div>
      </div>
      <button class="btn ghost" id="favToggle"><i class="fas fa-heart"></i> ${
        state.favorites.has(biz.id) ? "Remove Favorite" : "Add to Favorites"
      }</button>
    </div>
    <div class="detail-meta">
      <div><i class="fas fa-map-marker-alt"></i> ${biz.address}</div>
      <div><i class="fas fa-phone"></i> ${biz.phone || "No phone listed"}</div>
      ${biz.latitude && biz.longitude ? `<div><i class="fas fa-map"></i> <a href="https://www.google.com/maps/search/?api=1&query=${biz.latitude},${biz.longitude}" target="_blank">View on Google Maps</a></div>` : ""}
    </div>
    <p>${biz.description || ""}</p>
    ${biz.deals?.length ? "<h3>Deals & Coupons</h3>" : ""}
    <div class="deal-list">
      ${biz.deals
        ?.map(
          d =>
            `<div class="deal-card"><strong>${d.title}</strong><div class="helper">${d.description}${
              d.expires ? ` • Expires: ${d.expires}` : ""
            }</div></div>`
        )
        .join("") || ""}
    </div>
    <h3>Reviews</h3>
    <div class="reviews">
      ${
        biz.reviews && biz.reviews.length
          ? biz.reviews
              .slice()
              .reverse()
              .map(
                r =>
                  `<div class="review">
                    <div class="rating-row"><span class="stars">${"★".repeat(r.rating)}${"☆".repeat(
                    5 - r.rating
                  )}</span> <strong>${r.user_name}</strong></div>
                    <p>${r.comment}</p>
                    <div class="helper">${r.date || ""}</div>
                  </div>`
              )
              .join("")
          : `<div class="empty">No reviews yet. Be the first to review!</div>`
      }
    </div>
    <h3>Add a Review</h3>
    <div class="form" id="reviewForm">
      <div class="row">
        <label>Name</label>
        <input id="rName" type="text" placeholder="Your name" required />
      </div>
      <div class="row">
        <label>Rating</label>
        <select id="rRating">
          <option value="5">5 - Excellent</option>
          <option value="4">4 - Good</option>
          <option value="3">3 - Okay</option>
          <option value="2">2 - Poor</option>
          <option value="1">1 - Terrible</option>
        </select>
      </div>
      <div class="row">
        <label>Comment</label>
        <textarea id="rComment" rows="3" placeholder="Share your experience"></textarea>
      </div>
      <div class="row">
        <label id="captchaLabel"></label>
        <input id="rCaptcha" type="text" placeholder="Answer to verify" />
      </div>
      <button class="btn primary" id="rSubmit"><i class="fas fa-paper-plane"></i> Submit Review</button>
    </div>
  `;

  const closeBtn = content.querySelector("#modalClose");
  closeBtn.addEventListener("click", closeModal);
  modal.classList.add("open");

  const favToggle = content.querySelector("#favToggle");
  const syncFavBtn = () => {
    favToggle.innerHTML = `<i class="fas fa-heart"></i> ${
      state.favorites.has(biz.id) ? "Remove Favorite" : "Add to Favorites"
    }`;
  };
  favToggle.addEventListener("click", () => {
    if (state.favorites.has(biz.id)) state.favorites.delete(biz.id);
    else state.favorites.add(biz.id);
    saveState();
    syncFavBtn();
    render();
  });
  syncFavBtn();

  // Verification
  const a = Math.floor(Math.random() * 10) + 1;
  const b = Math.floor(Math.random() * 10) + 1;
  const answer = a + b;
  content.querySelector("#captchaLabel").textContent = `Verification: ${a} + ${b} = ?`;

  content.querySelector("#rSubmit").addEventListener("click", () => {
    const name = content.querySelector("#rName").value.trim() || "Anonymous";
    const rating = parseInt(content.querySelector("#rRating").value, 10);
    const comment = content.querySelector("#rComment").value.trim() || "Great place!";
    const cap = content.querySelector("#rCaptcha").value.trim();
    if (String(answer) !== cap) {
      alert("Verification failed. Please try again.");
      return;
    }
    if (!biz.reviews) biz.reviews = [];
    biz.reviews.push({
      user_name: name,
      rating,
      comment,
      date: new Date().toISOString().split("T")[0]
    });
    saveState();
    openDetails(biz.id);
    render();
  });
}

function closeModal() {
  qs("modal").classList.remove("open");
}

function showFavorites() {
  state.filters.category = "";
  state.filters.search = "";
  state.filters.sort = "name";
  const favIds = state.favorites;
  const list = state.businesses.filter(b => favIds.has(b.id));
  const container = qs("businessList");
  container.innerHTML = "";
  if (!list.length) {
    container.innerHTML = `<div class="empty">No favorites yet. Click the heart on a business to add it.</div>`;
  } else {
    list.forEach(b => container.appendChild(cardForBusiness(b)));
  }
}

function addBusinessFlow() {
  const name = prompt("Business name:");
  if (!name) return;
  const category = prompt("Category (food/retail/services):", "food") || "food";
  const address = prompt("Address:", "123 Main St");
  const phone = prompt("Phone (optional):", "");
  const description = prompt("Description (optional):", "");
  const dealTitle = prompt("Add a deal title? (optional)", "");
  const dealDesc = dealTitle ? prompt("Deal description:", "") : "";
  const dealExpires = dealTitle ? prompt("Deal expires (YYYY-MM-DD):", "") : "";
  const a = Math.floor(Math.random() * 10) + 1;
  const b = Math.floor(Math.random() * 10) + 1;
  const answer = prompt(`Verification: What is ${a} + ${b}?`);
  if (String(a + b) !== String(answer)) {
    alert("Verification failed.");
    return;
  }
  const newBiz = {
    id: `biz_${Date.now()}`,
    name,
    category: category.toLowerCase(),
    address,
    phone,
    description,
    deals: dealTitle ? [{ title: dealTitle, description: dealDesc, expires: dealExpires }] : [],
    reviews: []
  };
  state.businesses.push(newBiz);
  saveState();
  buildCategories();
  render();
}

function bindEvents() {
  qs("applyFilters").addEventListener("click", () => {
    state.filters.search = qs("search").value.trim();
    state.filters.category = qs("category").value;
    state.filters.sort = qs("sort").value;
    render();
  });

  qs("topRatedBtn").addEventListener("click", () => {
    state.filters.sort = "rating";
    render();
  });

  qs("mostReviewedBtn").addEventListener("click", () => {
    state.filters.sort = "reviews";
    render();
  });

  qs("favoritesBtn").addEventListener("click", showFavorites);
  qs("addBtn").addEventListener("click", addBusinessFlow);
  qs("modal").addEventListener("click", e => {
    if (e.target.id === "modal") closeModal();
  });

  // Location events
  qs("useCurrentLocation").addEventListener("click", getCurrentLocation);
  qs("searchLocation").addEventListener("click", searchByLocationText);
  qs("locationInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      searchByLocationText();
    }
  });

  // API Key events
  qs("enterApiKey")?.addEventListener("click", showApiKeyModal);
  qs("showApiKeyHelp")?.addEventListener("click", (e) => {
    e.preventDefault();
    window.open("https://developers.google.com/maps/documentation/places/web-service/get-api-key", "_blank");
  });
  qs("saveApiKey")?.addEventListener("click", () => {
    const key = qs("apiKeyInput").value.trim();
    if (key) {
      saveApiKey(key);
    }
  });
  qs("cancelApiKey")?.addEventListener("click", hideApiKeyModal);
}

function init() {
  els.list = qs("businessList");
  loadApiKey();
  loadState();
  buildCategories();
  bindEvents();
  render();
}

document.addEventListener("DOMContentLoaded", init);
