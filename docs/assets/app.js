// Static client-side app for Byte-Sized Business Boost

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
  },
  {
    id: "greenthumb",
    name: "Green Thumb Garden Center",
    category: "retail",
    address: "456 Oak Ave, Garden District",
    phone: "555-0102",
    description: "Family-owned garden center with expert advice and quality plants.",
    deals: [{ title: "20% Off All Seeds", description: "Valid this month", expires: "2024-12-31" }],
    reviews: [{ user_name: "Noah", rating: 5, comment: "Healthy plants and helpful staff!", date: "2024-03-08" }]
  },
  {
    id: "quickfix",
    name: "Quick Fix Auto Repair",
    category: "services",
    address: "789 Industrial Blvd",
    phone: "555-0103",
    description: "Honest and reliable auto repair service with fair pricing.",
    deals: [{ title: "Free Oil Change", description: "With any major service", expires: "2024-12-31" }],
    reviews: []
  },
  {
    id: "mamaskitchen",
    name: "Mama's Italian Kitchen",
    category: "food",
    address: "321 Elm St, Little Italy",
    phone: "555-0104",
    description: "Authentic Italian cuisine made with love and fresh ingredients.",
    deals: [{ title: "10% Off Dinner", description: "Monday-Thursday", expires: "2024-12-31" }],
    reviews: [{ user_name: "Sophia", rating: 5, comment: "Incredible pasta and warm hospitality!", date: "2024-04-21" }]
  },
  {
    id: "booknook",
    name: "The Book Nook",
    category: "retail",
    address: "654 Pine St, Arts Quarter",
    phone: "555-0105",
    description: "Independent bookstore with a curated selection of new and used books.",
    deals: [{ title: "Buy 2 Get 1 Free", description: "All paperback books", expires: "2024-12-31" }],
    reviews: []
  }
];

const state = {
  businesses: [],
  favorites: new Set(),
  filters: { search: "", category: "", sort: "name" }
};

const els = {};

function qs(id) {
  return document.getElementById(id);
}

function loadState() {
  const stored = localStorage.getItem("bsbb-data");
  if (stored) {
    try {
      const parsed = JSON.parse(stored);
      state.businesses = parsed.businesses || sampleBusinesses;
      state.favorites = new Set(parsed.favorites || []);
      return;
    } catch (e) {
      console.warn("Failed to parse stored data, using samples", e);
    }
  }
  state.businesses = sampleBusinesses;
}

function saveState() {
  localStorage.setItem(
    "bsbb-data",
    JSON.stringify({ businesses: state.businesses, favorites: Array.from(state.favorites) })
  );
}

function averageRating(biz) {
  if (!biz.reviews.length) return 0;
  return biz.reviews.reduce((a, r) => a + (r.rating || 0), 0) / biz.reviews.length;
}

function totalReviews(biz) {
  return biz.reviews.length;
}

function renderStats() {
  qs("statBusinesses").textContent = state.businesses.length;
  const allReviews = state.businesses.reduce((a, b) => a + b.reviews.length, 0);
  qs("statReviews").textContent = allReviews;
  const rated = state.businesses.filter(b => b.reviews.length);
  const avg =
    rated.length === 0 ? 0 : rated.reduce((a, b) => a + averageRating(b), 0) / rated.length;
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
  const data = filteredBusinesses();
  if (!data.length) {
    list.innerHTML = `<div class="empty">No businesses found. Try another search.</div>`;
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
        biz.reviews.length
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
          : `<div class="empty">No reviews yet.</div>`
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
    biz.reviews.push({
      user_name: name,
      rating,
      comment,
      date: new Date().toISOString().split("T")[0]
    });
    saveState();
    openDetails(biz.id); // re-render modal
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
  const captcha = Math.floor(Math.random() * 10) + Math.floor(Math.random() * 10);
  const answer = prompt(`Verification: What is ${captcha}?`);
  if (String(captcha) !== String(answer)) {
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
}

function init() {
  els.list = qs("businessList");
  loadState();
  buildCategories();
  bindEvents();
  render();
}

document.addEventListener("DOMContentLoaded", init);

