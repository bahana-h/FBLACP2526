
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
  loading: false,
  view: "" // "", "favorites", "recommendations"
};

const els = {};
const OVERPASS_PRIMARY_RADIUS = 1200;
const OVERPASS_FALLBACK_RADIUS = 700;
const OVERPASS_TIMEOUT_SEC = 18;
const OVERPASS_REQUEST_TIMEOUT_MS = 20000;
const MAX_OSM_RESULTS = 120;

function qs(id) {
  return document.getElementById(id);
}

function clamp(n, min, max) {
  return Math.max(min, Math.min(max, n));
}

function starMeterHTML(rating) {
  const r = clamp(Number(rating) || 0, 0, 5);
  return `<span class="stars-meter" style="--rating:${r.toFixed(2)}" aria-label="${r.toFixed(
    1
  )} out of 5 stars"></span>`;
}

function mergeLocalReviewsInto(newBusinesses) {
  const oldById = new Map((state.businesses || []).map(b => [b.id, b]));
  return newBusinesses.map(b => {
    const old = oldById.get(b.id);
    if (old && Array.isArray(old.reviews) && old.reviews.length) {
      b.reviews = Array.isArray(b.reviews) ? b.reviews : [];
      const seen = new Set(b.reviews.map(r => `${r.user_name}|${r.rating}|${r.comment}|${r.date || ""}`));
      for (const r of old.reviews) {
        const key = `${r.user_name}|${r.rating}|${r.comment}|${r.date || ""}`;
        if (!seen.has(key)) {
          b.reviews.push(r);
          seen.add(key);
        }
      }
    }
    return b;
  });
}

const BACKEND_URL_KEY = "cc-backend-url";

function getBackendBaseUrl() {
  const url = (localStorage.getItem(BACKEND_URL_KEY) || "").trim();
  return url.replace(/\/+$/, "");
}

function setBackendBaseUrl(url) {
  localStorage.setItem(BACKEND_URL_KEY, (url || "").trim());
}

async function backendHealthOk(baseUrl) {
  try {
    const resp = await fetch(`${baseUrl}/api/health`, { method: "GET" });
    if (!resp.ok) return false;
    const data = await resp.json();
    return Boolean(data && data.ok);
  } catch {
    return false;
  }
}

async function fetchSharedReviewsForBusinesses(businessIds) {
  const baseUrl = getBackendBaseUrl();
  if (!baseUrl) return null;

  const ok = await backendHealthOk(baseUrl);
  if (!ok) return null;

  const resp = await fetch(`${baseUrl}/api/shared-reviews/bulk`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ business_ids: businessIds })
  });
  if (!resp.ok) return null;
  return await resp.json(); // { reviews_by_id: { ... } }
}

async function postSharedReview({ business_id, user_name, rating, comment }) {
  const baseUrl = getBackendBaseUrl();
  if (!baseUrl) return { ok: false, error: "Backend URL not set." };

  const ok = await backendHealthOk(baseUrl);
  if (!ok) return { ok: false, error: "Backend not reachable." };

  const resp = await fetch(`${baseUrl}/api/shared-reviews`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ business_id, user_name, rating, comment, verified: true })
  });

  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) return { ok: false, error: data.error || "Failed to save review." };
  return data;
}

async function syncSharedReviewsIntoState() {
  const baseUrl = getBackendBaseUrl();
  if (!baseUrl) return;

  const ids = state.businesses.map(b => b.id).filter(Boolean);
  if (!ids.length) return;

  const payload = await fetchSharedReviewsForBusinesses(ids);
  if (!payload || !payload.reviews_by_id) return;

  for (const biz of state.businesses) {
    const shared = payload.reviews_by_id[biz.id] || [];
    if (!Array.isArray(shared) || shared.length === 0) continue;

    biz.reviews = Array.isArray(biz.reviews) ? biz.reviews : [];
    const seen = new Set(biz.reviews.map(r => `${r.user_name}|${r.rating}|${r.comment}`));

    for (const r of shared) {
      const key = `${r.user_name}|${r.rating}|${r.comment}`;
      if (!seen.has(key)) {
        biz.reviews.push(r);
        seen.add(key);
      }
    }
  }
}

function showBackendStatus() {
  const baseUrl = getBackendBaseUrl();
  if (!baseUrl) {
    showStatus("Shared reviews: OFF (set backend URL in Shared Reviews).", "info");
    return;
  }
  showStatus(`Shared reviews: ON (${baseUrl})`, "success");
}



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

async function searchBusinesses(location) {
  state.loading = true;
  showStatus("Searching for local businesses...", "info");

  try {
    let lat, lon;

    if (typeof location === 'string') {
      const coords = await geocodeLocation(location);
      if (!coords) {
        throw new Error("Could not find location. Please try a more specific address.");
      }
      lat = coords.lat;
      lon = coords.lon;
    } else {
      lat = location.latitude;
      lon = location.longitude;
    }

    const categoryTags = getOSMCategoryTags();
    let data;
    try {
      data = await fetchOverpassData(categoryTags, lat, lon, OVERPASS_PRIMARY_RADIUS);
    } catch (firstError) {
      showStatus("API is busy. Retrying with a smaller search area...", "info");
      data = await fetchOverpassData(categoryTags, lat, lon, OVERPASS_FALLBACK_RADIUS);
    }

    if (!data.elements || data.elements.length === 0) {
      showStatus("No businesses found. Try a different location or add businesses manually!", "info");
      state.businesses = mergeLocalReviewsInto(sampleBusinesses.map(b => ({ ...b })));
      await syncSharedReviewsIntoState();
      buildCategories();
      render();
      state.loading = false;
      return;
    }

    const seenIds = new Set();
    const nextBusinesses = data.elements
      .filter(element => element.tags && element.tags.name) // Only include named places
      .map(element => {
        const center = element.center || { lat: element.lat, lon: element.lon };
        return {
          id: `osm_${element.type}_${element.id}`,
          name: element.tags.name || 'Unnamed Business',
          category: mapOSMCategory(element.tags),
          address: formatOSMAddress(element.tags, center),
          phone: element.tags['phone'] || element.tags['contact:phone'] || 'No phone listed',
          description: buildOSMDescription(element.tags),
          rating: undefined,
          review_count: 0,
          latitude: center.lat,
          longitude: center.lon,
          website: element.tags['website'] || element.tags['contact:website'] || null,
          opening_hours: element.tags['opening_hours'] || null,
          deals: [],
          reviews: []
        };
      })
      .filter(biz => {
        if (seenIds.has(biz.id)) return false;
        seenIds.add(biz.id);
        return true;
      })
      .slice(0, MAX_OSM_RESULTS);

    state.businesses = mergeLocalReviewsInto(nextBusinesses);
    showStatus(`Found ${state.businesses.length} businesses from OpenStreetMap!`, "success");
    await syncSharedReviewsIntoState();
    saveState();
    buildCategories();
    render();
    state.loading = false;

  } catch (error) {
    console.error("Error fetching businesses:", error);
    showStatus(`Error: ${error.message}. Using sample data.`, "error");
    state.businesses = mergeLocalReviewsInto(sampleBusinesses.map(b => ({ ...b })));
    await syncSharedReviewsIntoState();
    saveState();
    buildCategories();
    render();
    state.loading = false;
  }
}

function buildOverpassQuery(categoryTags, lat, lon, radius) {
  return `
    [out:json][timeout:${OVERPASS_TIMEOUT_SEC}];
    (
      node["shop"~"${categoryTags.shop}"](around:${radius},${lat},${lon});
      node["amenity"~"${categoryTags.amenity}"](around:${radius},${lat},${lon});
      way["shop"~"${categoryTags.shop}"](around:${radius},${lat},${lon});
      way["amenity"~"${categoryTags.amenity}"](around:${radius},${lat},${lon});
    );
    out center tags;
  `;
}

async function fetchOverpassData(categoryTags, lat, lon, radius) {
  const query = buildOverpassQuery(categoryTags, lat, lon, radius);
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), OVERPASS_REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch('https://overpass-api.de/api/interpreter', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `data=${encodeURIComponent(query)}`,
      signal: controller.signal
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    if (error && error.name === 'AbortError') {
      throw new Error('API timeout');
    }
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

async function geocodeLocation(locationString) {
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(locationString)}&limit=1`,
      {
        headers: {
          'User-Agent': 'BusinessBoost/1.0' // Required by Nominatim
        }
      }
    );

    if (!response.ok) return null;

    const data = await response.json();
    if (data.length > 0) {
      return {
        lat: parseFloat(data[0].lat),
        lon: parseFloat(data[0].lon)
      };
    }
    return null;
  } catch (error) {
    console.error("Geocoding error:", error);
    return null;
  }
}

function getOSMCategoryTags() {
  const category = state.filters.category;

  if (category === 'food') {
    return {
      shop: 'supermarket|bakery|butcher|confectionery|convenience',
      amenity: 'restaurant|cafe|fast_food|bar|pub|food_court|ice_cream'
    };
  } else if (category === 'retail') {
    return {
      shop: 'supermarket|convenience|clothes|shoes|electronics|mobile_phone|hardware|books|gift|florist|beauty|jewelry|department_store',
      amenity: 'marketplace|vending_machine'
    };
  } else if (category === 'services') {
    return {
      shop: 'hairdresser|beauty|laundry|dry_cleaning|car_repair|car_wash',
      amenity: 'bank|pharmacy|post_office|library|community_centre|dentist|doctors|veterinary'
    };
  } else {
    return {
      shop: 'supermarket|convenience|bakery|clothes|shoes|electronics|mobile_phone|hardware|books|gift|florist|beauty|jewelry|department_store|hairdresser|laundry|car_repair',
      amenity: 'restaurant|cafe|fast_food|bar|pub|bank|pharmacy|post_office|library|marketplace'
    };
  }
}

function mapOSMCategory(tags) {
  const shop = tags.shop || '';
  const amenity = tags.amenity || '';
  const combined = `${shop} ${amenity}`.toLowerCase();

  if (combined.includes('restaurant') || combined.includes('cafe') ||
    combined.includes('food') || combined.includes('bar') ||
    combined.includes('pub') || combined.includes('bakery') ||
    combined.includes('fast_food') || combined.includes('ice_cream')) {
    return 'food';
  }
  if (combined.includes('shop') || combined.includes('store') ||
    combined.includes('market') || combined.includes('supermarket') ||
    combined.includes('retail') || combined.includes('mall')) {
    return 'retail';
  }
  return 'services';
}

function formatOSMAddress(tags, coords) {
  const parts = [];
  if (tags['addr:housenumber']) parts.push(tags['addr:housenumber']);
  if (tags['addr:street']) parts.push(tags['addr:street']);
  if (tags['addr:city']) parts.push(tags['addr:city']);
  if (tags['addr:postcode']) parts.push(tags['addr:postcode']);

  if (parts.length > 0) {
    return parts.join(' ');
  }

  return `Near ${coords.lat.toFixed(4)}, ${coords.lon.toFixed(4)}`;
}

function buildOSMDescription(tags) {
  const parts = [];
  if (tags.shop) parts.push(tags.shop);
  if (tags.amenity) parts.push(tags.amenity);
  if (tags.cuisine) parts.push(`${tags.cuisine} cuisine`);
  if (tags.brand) parts.push(tags.brand);

  return parts.length > 0 ? parts.join(', ') : 'Local business';
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
  const stored = localStorage.getItem("cc-data");
  if (stored) {
    try {
      const parsed = JSON.parse(stored);
      state.businesses = parsed.businesses || [];
      state.favorites = new Set(parsed.favorites || []);
    } catch (e) {
      console.warn("Failed to parse stored data", e);
    }
  }

  if (state.businesses.length === 0 && state.currentLocation) {
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
    "cc-data",
    JSON.stringify({ businesses: state.businesses, favorites: Array.from(state.favorites) })
  );
}

function averageRating(biz) {
  if (typeof biz.rating === "number" && biz.rating > 0) return biz.rating;
  if (!biz.reviews || !biz.reviews.length) return 0;
  return biz.reviews.reduce((a, r) => a + (r.rating || 0), 0) / biz.reviews.length;
}

function totalReviews(biz) {
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

function getSimilarBusinesses(biz, limit) {
  limit = limit || 3;
  return state.businesses
    .filter(b => b.id !== biz.id && b.category === biz.category)
    .sort((a, b) => averageRating(b) - averageRating(a))
    .slice(0, limit);
}

function setViewTitle(text) {
  const el = qs("viewTitle");
  if (!el) return;
  el.textContent = text || "";
  el.style.display = text ? "block" : "none";
}

function render() {
  renderStats();
  updateFiltersUI();
  const list = qs("businessList");
  list.innerHTML = "";

  if (state.view === "favorites") {
    setViewTitle("Favorites");
    const favIds = state.favorites;
    const data = state.businesses.filter(b => favIds.has(b.id));
    if (!data.length) {
      list.innerHTML = `<div class="empty">No favorites yet. Click the heart on a business to add it.</div>`;
      return;
    }
    data.forEach(biz => list.appendChild(cardForBusiness(biz)));
    return;
  }

  if (state.view === "recommendations") {
    setViewTitle("Recommendations — top rated and trending");
    state.filters.sort = "rating";
    updateFiltersUI();
  } else {
    setViewTitle("");
  }

  if (state.loading) {
    list.innerHTML = `<div class="empty"><i class="fas fa-spinner fa-spin"></i> Loading businesses...</div>`;
    return;
  }

  const data = filteredBusinesses();
  if (!data.length) {
    list.innerHTML = `<div class="empty">No businesses found. Try another search or location, or add businesses manually!</div>`;
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
    ${starMeterHTML(rating)}
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
  const similar = getSimilarBusinesses(biz, 3);
  const modal = qs("modal");
  const content = qs("modalContent");
  content.innerHTML = `
    <button class="modal-close" id="modalClose">&times;</button>
    <div class="detail-header">
      <div>
        <div class="pill-inline category-${biz.category}">${biz.category}</div>
        <h2>${biz.name}</h2>
        <div class="rating-row">
          ${starMeterHTML(averageRating(biz))}
          <span>${averageRating(biz).toFixed(1)} / 5 (${totalReviews(biz)} reviews)</span>
        </div>
      </div>
      <button class="btn ghost" id="favToggle"><i class="fas fa-heart"></i> ${state.favorites.has(biz.id) ? "Remove Favorite" : "Add to Favorites"
    }</button>
    </div>
    <div class="detail-meta">
      <div><i class="fas fa-map-marker-alt"></i> ${biz.address}</div>
      <div><i class="fas fa-phone"></i> ${biz.phone || "No phone listed"}</div>
      ${biz.latitude && biz.longitude ? `<div><i class="fas fa-map"></i> <a href="https://www.openstreetmap.org/?mlat=${biz.latitude}&mlon=${biz.longitude}&zoom=15" target="_blank">View on OpenStreetMap</a></div>` : ""}
      ${biz.website ? `<div><i class="fas fa-globe"></i> <a href="${biz.website}" target="_blank">Visit Website</a></div>` : ""}
      ${biz.opening_hours ? `<div><i class="fas fa-clock"></i> ${biz.opening_hours}</div>` : ""}
    </div>
    <p>${biz.description || ""}</p>
    ${biz.deals?.length ? "<h3>Deals & Coupons</h3>" : ""}
    <div class="deal-list">
      ${biz.deals
      ?.map(
        d =>
          `<div class="deal-card"><strong>${d.title}</strong><div class="helper">${d.description}${d.expires ? ` • Expires: ${d.expires}` : ""
          }</div></div>`
      )
      .join("") || ""}
    </div>
    ${similar.length ? `<h3>Similar businesses</h3><div class="similar-list" id="similarList">${similar.map(s => `<button type="button" class="similar-item" data-id="${s.id}"><strong>${s.name}</strong> · ${averageRating(s).toFixed(1)} ★ (${totalReviews(s)} reviews)</button>`).join("")}</div>` : ""}
    <h3>Reviews</h3>
    <div class="reviews">
      ${biz.reviews && biz.reviews.length
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

  const similarList = content.querySelector("#similarList");
  if (similarList) {
    similarList.querySelectorAll(".similar-item").forEach(btn => {
      btn.addEventListener("click", () => {
        const sid = btn.getAttribute("data-id");
        if (sid) openDetails(sid);
      });
    });
  }

  const favToggle = content.querySelector("#favToggle");
  const syncFavBtn = () => {
    favToggle.innerHTML = `<i class="fas fa-heart"></i> ${state.favorites.has(biz.id) ? "Remove Favorite" : "Add to Favorites"
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
    const newReview = {
      user_name: name,
      rating,
      comment,
      date: new Date().toISOString().split("T")[0]
    };
    biz.reviews.push(newReview);
    saveState();
    postSharedReview({
      business_id: biz.id,
      user_name: newReview.user_name,
      rating: newReview.rating,
      comment: newReview.comment
    }).then(result => {
      if (result && result.ok === false) {
        console.warn("Shared review save failed:", result.error);
      }
    });
    openDetails(biz.id);
    render();
  });
}

function closeModal() {
  qs("modal").classList.remove("open");
}

function showFavorites() {
  state.view = "favorites";
  state.filters.category = "";
  state.filters.search = "";
  state.filters.sort = "name";
  scrollToDirectory();
  render();
}

function showRecommendations() {
  state.view = "recommendations";
  state.filters.sort = "rating";
  state.filters.category = "";
  state.filters.search = "";
  scrollToDirectory();
  render();
}

function scrollToDirectory() {
  const el = document.getElementById("directory");
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
}

function openHelpModal() {
  const el = qs("helpModal");
  if (el) {
    el.classList.add("open");
    el.setAttribute("aria-hidden", "false");
  }
}

function closeHelpModal() {
  const el = qs("helpModal");
  if (el) {
    el.classList.remove("open");
    el.setAttribute("aria-hidden", "true");
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
    state.view = "";
    state.filters.search = qs("search").value.trim();
    state.filters.category = qs("category").value;
    state.filters.sort = qs("sort").value;
    render();
  });

  const navRec = qs("navRecommendations");
  if (navRec) navRec.addEventListener("click", showRecommendations);

  const topRatedBtn = qs("topRatedBtn");
  if (topRatedBtn) {
    topRatedBtn.addEventListener("click", () => {
      state.view = "";
      state.filters.sort = "rating";
      render();
    });
  }
  const mostReviewedBtn = qs("mostReviewedBtn");
  if (mostReviewedBtn) {
    mostReviewedBtn.addEventListener("click", () => {
      state.view = "";
      state.filters.sort = "reviews";
      render();
    });
  }

  const settingsBtn = qs("settingsBtn");
  if (settingsBtn) {
    settingsBtn.addEventListener("click", async () => {
      const current = getBackendBaseUrl();
      const next = prompt(
        "Shared Reviews backend URL (example: https://your-backend.onrender.com)\n\nLeave blank to disable shared reviews.",
        current
      );
      if (next === null) return;
      setBackendBaseUrl(next);
      showBackendStatus();
      await syncSharedReviewsIntoState();
      saveState();
      render();
    });
  }

  qs("favoritesBtn").addEventListener("click", showFavorites);

  const navHelp = qs("navHelp");
  if (navHelp) navHelp.addEventListener("click", openHelpModal);
  const helpModalClose = qs("helpModalClose");
  if (helpModalClose) helpModalClose.addEventListener("click", closeHelpModal);
  const helpModal = qs("helpModal");
  if (helpModal) {
    helpModal.addEventListener("click", e => {
      if (e.target.id === "helpModal") closeHelpModal();
    });
  }

  qs("modal").addEventListener("click", e => {
    if (e.target.id === "modal") closeModal();
  });

  qs("useCurrentLocation").addEventListener("click", getCurrentLocation);
  qs("searchLocation").addEventListener("click", searchByLocationText);
  qs("locationInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      searchByLocationText();
    }
  });

}

function init() {
  els.list = qs("businessList");
  qs("apiKeyBanner").style.display = "none";
  showBackendStatus();
  loadState();
  buildCategories();
  bindEvents();
  render();

  syncSharedReviewsIntoState().then(() => {
    saveState();
    render();
  });

  const landingBtn = qs("landingScrollBtn");
  if (landingBtn) {
    landingBtn.addEventListener("click", () => {
      const el = document.getElementById("directory");
      if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
      setTimeout(() => getCurrentLocation(), 350);
    });
  }

  const hash = window.location.hash;
  const detailMatch = hash && hash.match(/^#detail=(.+)$/);
  if (detailMatch) {
    const id = decodeURIComponent(detailMatch[1]);
    setTimeout(() => {
      if (state.businesses.some(b => b.id === id)) openDetails(id);
    }, 200);
  }
}

document.addEventListener("DOMContentLoaded", init);