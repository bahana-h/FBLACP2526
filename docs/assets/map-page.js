(function () {
  function getBusinesses() {
    try {
      const raw = localStorage.getItem("cc-data");
      if (!raw) return [];
      const data = JSON.parse(raw);
      return data.businesses || [];
    } catch (e) {
      return [];
    }
  }

  function averageRating(biz) {
    if (typeof biz.rating === "number" && biz.rating > 0) return biz.rating;
    if (!biz.reviews || !biz.reviews.length) return 0;
    return biz.reviews.reduce(function (sum, r) {
      return sum + (r.rating || 0);
    }, 0) / biz.reviews.length;
  }

  function totalReviews(biz) {
    if (biz.review_count !== undefined) return (biz.review_count || 0) + (biz.reviews && biz.reviews.length || 0);
    return (biz.reviews && biz.reviews.length) || 0;
  }

  function escapeHtml(s) {
    var div = document.createElement("div");
    div.textContent = s;
    return div.innerHTML;
  }

  function hasLoadedBusinesses() {
    return businesses.length > 0;
  }

  function showLoadBusinessesPopup(actionLabel) {
    alert("Please load local businesses on the directory first before using " + actionLabel + ".");
  }

  var container = document.getElementById("businessMap");
  var emptyMsg = document.getElementById("mapEmptyMsg");
  if (!container) return;

  var businesses = getBusinesses();
  var withLocation = businesses.filter(function (b) {
    return b.latitude != null && b.longitude != null &&
      Number.isFinite(b.latitude) && Number.isFinite(b.longitude);
  });

  var guardedLinks = [
    { id: "mapTopRatedLink", label: "Top Rated" },
    { id: "mapMostReviewedLink", label: "Most Reviewed" },
    { id: "mapFavoritesLink", label: "Favorites" }
  ];

  guardedLinks.forEach(function (item) {
    var link = document.getElementById(item.id);
    if (!link) return;
    link.addEventListener("click", function (event) {
      if (!hasLoadedBusinesses()) {
        event.preventDefault();
        showLoadBusinessesPopup(item.label);
      }
    });
  });

  if (emptyMsg) emptyMsg.style.display = withLocation.length === 0 ? "block" : "none";

  if (withLocation.length === 0) return;

  if (typeof L === "undefined") return;

  var defaultCenter = withLocation.length === 1
    ? [withLocation[0].latitude, withLocation[0].longitude]
    : [37.7749, -122.4194];
  var zoom = withLocation.length === 1 ? 14 : 12;

  var map = L.map("businessMap").setView(defaultCenter, zoom);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap</a>"
  }).addTo(map);

  var categoryColors = { food: "#92400e", retail: "#1e40af", services: "#065f46" };
  var categoryIcons = { food: "fa-utensils", retail: "fa-shopping-bag", services: "fa-tools" };
  var bounds = L.latLngBounds();

  withLocation.forEach(function (biz) {
    var color = categoryColors[biz.category] || "#6366f1";
    var icon = L.divIcon({
      className: "custom-marker",
      html: "<div class=\"marker-pin\" style=\"background:" + color + "\"><i class=\"fas " + (categoryIcons[biz.category] || "fa-store") + "\"></i></div>",
      iconSize: [36, 36],
      iconAnchor: [18, 36]
    });
    var marker = L.marker([biz.latitude, biz.longitude], { icon: icon }).addTo(map);
    bounds.extend([biz.latitude, biz.longitude]);

    var rating = averageRating(biz);
    var reviewCount = totalReviews(biz);
    var detailUrl = "index.html#detail=" + encodeURIComponent(biz.id);
    var popupContent = "<div class=\"map-popup\">" +
      "<strong>" + escapeHtml(biz.name) + "</strong>" +
      "<p class=\"map-popup-address\"><i class=\"fas fa-map-marker-alt\"></i> " + escapeHtml(biz.address) + "</p>" +
      (reviewCount > 0 ? "<p class=\"map-popup-rating\"><i class=\"fas fa-star\"></i> " + rating.toFixed(1) + " (" + reviewCount + " reviews)</p>" : "") +
      "<a href=\"" + detailUrl + "\" class=\"btn primary btn-sm map-popup-btn\">View Details</a>" +
      "</div>";
    marker.bindPopup(popupContent);
  });

  if (withLocation.length > 1) map.fitBounds(bounds, { padding: [40, 40] });
})();
