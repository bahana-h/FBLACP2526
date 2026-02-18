/**
 * Reports page: reads businesses from localStorage (cc-data), computes summary stats,
 * and builds a filterable/sortable table. Supports print and download (HTML blob).
 */
(function () {
  /** Read and parse cc-data from localStorage; returns { businesses, favorites } or empty defaults. */
  function getStored() {
    try {
      var raw = localStorage.getItem("cc-data");
      if (!raw) return { businesses: [], favorites: [] };
      return JSON.parse(raw);
    } catch (e) {
      return { businesses: [], favorites: [] };
    }
  }

  /** Compute average rating from reviews, or use biz.rating if it is a positive number. */
  function averageRating(biz) {
    if (typeof biz.rating === "number" && biz.rating > 0) return biz.rating;
    if (!biz.reviews || !biz.reviews.length) return 0;
    return biz.reviews.reduce(function (s, r) { return s + (r.rating || 0); }, 0) / biz.reviews.length;
  }

  /** Total review count for a business (review_count if present, else reviews.length). */
  function totalReviews(biz) {
    if (biz.review_count !== undefined) return (biz.review_count || 0) + (biz.reviews && biz.reviews.length || 0);
    return (biz.reviews && biz.reviews.length) || 0;
  }

  /** Build the full report: apply category/sort from dropdowns, compute summary stats, fill summary boxes and table. */
  function buildReport() {
    var category = (document.getElementById("reportCategory") && document.getElementById("reportCategory").value) || "";
    var sort = (document.getElementById("reportSort") && document.getElementById("reportSort").value) || "name";
    var stored = getStored();
    var list = (stored.businesses || []).slice();

    if (category) list = list.filter(function (b) { return b.category === category; });
    if (sort === "rating") list.sort(function (a, b) { return averageRating(b) - averageRating(a); });
    else if (sort === "reviews") list.sort(function (a, b) { return totalReviews(b) - totalReviews(a); });
    else list.sort(function (a, b) { return (a.name || "").localeCompare(b.name || ""); });

    var totalBiz = (stored.businesses || []).length;
    var totalRev = (stored.businesses || []).reduce(function (s, b) { return s + totalReviews(b); }, 0);
    var withReviews = (stored.businesses || []).filter(function (b) { return totalReviews(b) > 0; });
    var avgRating = withReviews.length ? withReviews.reduce(function (s, b) { return s + averageRating(b); }, 0) / withReviews.length : 0;
    var byCat = {};
    (stored.businesses || []).forEach(function (b) {
      var c = b.category || "other";
      byCat[c] = (byCat[c] || 0) + 1;
    });

    var summaryEl = document.getElementById("reportSummary");
    if (summaryEl) {
      summaryEl.innerHTML =
        "<div class=\"stat-box\"><span class=\"num\">" + totalBiz + "</span><div class=\"label\">Total businesses</div></div>" +
        "<div class=\"stat-box\"><span class=\"num\">" + totalRev + "</span><div class=\"label\">Total reviews</div></div>" +
        "<div class=\"stat-box\"><span class=\"num\">" + avgRating.toFixed(1) + "</span><div class=\"label\">Avg rating</div></div>" +
        "<div class=\"stat-box\"><span class=\"num\">" + list.length + "</span><div class=\"label\">In this view</div></div>" +
        (Object.keys(byCat).length ? "<div class=\"stat-box\"><span class=\"num\">" + Object.keys(byCat).length + "</span><div class=\"label\">Categories</div></div>" : "");
    }

    var tableWrap = document.getElementById("reportTableWrap");
    if (!tableWrap) return;

    if (!list.length) {
      tableWrap.innerHTML = "<p class=\"empty\">No businesses to show. Change filters or add businesses from the directory.</p>";
      return;
    }

    var rows = list.map(function (b) {
      var r = averageRating(b);
      var tr = totalReviews(b);
      return "<tr><td>" + escapeHtml(b.name) + "</td><td>" + escapeHtml(b.category || "") + "</td><td>" + r.toFixed(1) + "</td><td>" + tr + "</td><td>" + escapeHtml(b.address || "") + "</td></tr>";
    }).join("");
    tableWrap.innerHTML =
      "<table class=\"report-table\">" +
      "<thead><tr><th>Business</th><th>Category</th><th>Rating</th><th>Reviews</th><th>Address</th></tr></thead>" +
      "<tbody>" + rows + "</tbody></table>";
  }

  /** Escape text for safe HTML insertion. */
  function escapeHtml(s) {
    var div = document.createElement("div");
    div.textContent = s;
    return div.innerHTML;
  }

  /** Open print dialog for #printArea (report summary + table); toolbar/nav hidden via print CSS. */
  function printReport() {
    window.print();
  }

  /** Build a tab-separated report with current filters and trigger download as .txt file. */
  function downloadReport() {
    var category = document.getElementById("reportCategory") && document.getElementById("reportCategory").value;
    var sort = document.getElementById("reportSort") && document.getElementById("reportSort").value;
    var stored = getStored();
    var list = (stored.businesses || []).slice();
    if (category) list = list.filter(function (b) { return b.category === category; });
    if (sort === "rating") list.sort(function (a, b) { return averageRating(b) - averageRating(a); });
    else if (sort === "reviews") list.sort(function (a, b) { return totalReviews(b) - totalReviews(a); });
    else list.sort(function (a, b) { return (a.name || "").localeCompare(b.name || ""); });

    var lines = [
      "Chrysalis Connect - Directory Report",
      "Generated: " + new Date().toLocaleString(),
      "Category filter: " + (category || "All") + " | Sort: " + sort,
      "",
      "Total businesses: " + list.length,
      "",
      "Business Name\tCategory\tRating\tReviews\tAddress"
    ];
    list.forEach(function (b) {
      lines.push(
        (b.name || "") + "\t" + (b.category || "") + "\t" + averageRating(b).toFixed(1) + "\t" + totalReviews(b) + "\t" + (b.address || "")
      );
    });
    var blob = new Blob([lines.join("\n")], { type: "text/plain;charset=utf-8" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "chrysalis-connect-report-" + new Date().toISOString().slice(0, 10) + ".txt";
    a.click();
    URL.revokeObjectURL(a.href);
  }

  buildReport();
  /* Wire filter/sort dropdowns and buttons to rebuild report or trigger print/download. */
  var refreshBtn = document.getElementById("reportRefresh");
  if (refreshBtn) refreshBtn.addEventListener("click", buildReport);
  var catSelect = document.getElementById("reportCategory");
  var sortSelect = document.getElementById("reportSort");
  if (catSelect) catSelect.addEventListener("change", buildReport);
  if (sortSelect) sortSelect.addEventListener("change", buildReport);
  var printBtn = document.getElementById("reportPrint");
  if (printBtn) printBtn.addEventListener("click", printReport);
  var downloadBtn = document.getElementById("reportDownload");
  if (downloadBtn) downloadBtn.addEventListener("click", downloadReport);
})();
