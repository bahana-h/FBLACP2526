// Intelligent Q&A: keyword-based matching with a knowledge base
(function () {
  var knowledge = [
    {
      keywords: ["add", "business", "new", "list", "submit", "create"],
      question: "How do I add a business?",
      answer: "Click <strong>Add Business</strong> in the nav (or go to the Add Business page). Fill in the name, category (food, retail, or services), address, phone, and optional description. You can add a deal or coupon too. Solve the simple math verification to submit. New businesses appear in the directory right away and are saved on your device."
    },
    {
      keywords: ["favorite", "favourites", "heart", "save", "bookmark"],
      question: "How do favorites work?",
      answer: "Click the <strong>heart</strong> on any business card or on its detail page to add it to your Favorites. Open <strong>Favorites</strong> from the nav to see your saved list. Your favorites are stored on this device (browser)."
    },
    {
      keywords: ["review", "rating", "star", "comment", "leave"],
      question: "How do I leave a review?",
      answer: "Open a business (click <strong>Details</strong>), scroll to <strong>Add a Review</strong>, enter your name, pick a rating (1–5 stars), write a comment, and solve the quick math verification. Reviews are saved locally and, if you set a backend URL under Shared Reviews, they can be synced across users."
    },
    {
      keywords: ["shared", "reviews", "sync", "backend", "url", "across", "device"],
      question: "What are Shared Reviews?",
      answer: "Shared Reviews let you sync reviews with other users. Click <strong>Shared Reviews</strong> in the nav and enter your backend URL (e.g. your deployed Chrysalis Connect Flask app). Once set, reviews you submit are sent to that server and other users can see them when they load the directory."
    },
    {
      keywords: ["map", "location", "marker", "where"],
      question: "How does the map work?",
      answer: "Click <strong>Map</strong> in the nav to open the Business Map page. Businesses that have location data (e.g. from a location search or added with an address) appear as markers. Click a marker to see details and <strong>View Details</strong> to open the full business page."
    },
    {
      keywords: ["recommendation", "recommended", "top", "rated", "trending"],
      question: "What are Recommendations?",
      answer: "Recommendations show you top-rated and trending businesses from your current list. Click <strong>Recommendations</strong> in the nav to see them. The list is sorted by rating so you can discover the best-reviewed places."
    },
    {
      keywords: ["verification", "captcha", "math", "robot", "bot"],
      question: "Why is there a verification when I add a review or business?",
      answer: "The quick math verification (e.g. “What is 3 + 5?”) helps reduce spam and bot submissions. It’s a simple step to keep reviews and new business listings cleaner for everyone."
    },
    {
      keywords: ["category", "food", "retail", "services", "filter"],
      question: "How do I filter by category?",
      answer: "Use the <strong>Category</strong> dropdown or the category pills (Food, Retail, Services) above the business list. Choose a category and click <strong>Apply</strong> to filter. You can also combine this with search and sort (name, rating, most reviewed)."
    },
    {
      keywords: ["search", "find", "look", "location", "city", "address"],
      question: "How do I search for businesses?",
      answer: "Enter a city, address, or zip code in the location box and click <strong>Search</strong> or <strong>Use My Location</strong>. Results come from OpenStreetMap and are free. You can also use the text search box to filter by name, category, or address after loading businesses."
    },
    {
      keywords: ["report", "analyze", "stat", "summary", "data"],
      question: "Where can I see reports or statistics?",
      answer: "Open <strong>Reports</strong> from the nav (or the Reports page) to see a summary of your data: total businesses, reviews, ratings, and top businesses. You can customize filters and print or download the report."
    },
    {
      keywords: ["help", "how", "what", "why", "where", "when"],
      question: "Where can I get more help?",
      answer: "On the main page, click <strong>Help</strong> in the nav to open the “How to Use Chrysalis Connect” guide. You can also ask questions here in Q&A for quick answers."
    }
  ];

  function normalize(s) {
    return (s || "").toLowerCase().trim().replace(/\s+/g, " ");
  }

  function scoreMatch(input, item) {
    var words = normalize(input).split(/\s+/).filter(Boolean);
    var score = 0;
    var keyStr = item.keywords.join(" ") + " " + normalize(item.question);
    for (var i = 0; i < words.length; i++) {
      if (words[i].length < 2) continue;
      if (keyStr.indexOf(words[i]) !== -1) score += 1;
    }
    return score;
  }

  function getAnswers(input) {
    if (!input || normalize(input).length < 2) return [];
    var scored = knowledge.map(function (item) {
    return { item: item, score: scoreMatch(input, item) };
    }).filter(function (x) { return x.score > 0; });
    scored.sort(function (a, b) { return b.score - a.score; });
    return scored.slice(0, 3).map(function (x) { return x.item; });
  }

  function renderResults(items) {
    if (!items.length) {
      return "<div class=\"qa-result-card qa-no-match\">" +
        "<p>I couldn't find a direct match. Try rephrasing or use one of the suggested questions below. You can also open <strong>Help</strong> on the main page for a full guide.</p>" +
        "</div>";
    }
    return items.map(function (item) {
      return "<div class=\"qa-result-card\">" +
        "<h3 class=\"qa-result-q\">" + escapeHtml(item.question) + "</h3>" +
        "<div class=\"qa-result-a\">" + item.answer + "</div>" +
        "</div>";
    }).join("");
  }

  function escapeHtml(s) {
    var div = document.createElement("div");
    div.textContent = s;
    return div.innerHTML;
  }

  var inputEl = document.getElementById("qaInput");
  var submitBtn = document.getElementById("qaSubmit");
  var placeholder = document.getElementById("qaPlaceholder");
  var resultsEl = document.getElementById("qaResults");
  var suggestedEl = document.getElementById("qaSuggested");

  if (!inputEl || !resultsEl) return;

  function showResults(html) {
    placeholder.style.display = "none";
    resultsEl.hidden = false;
    resultsEl.innerHTML = html;
  }

  function showPlaceholder() {
    placeholder.style.display = "block";
    resultsEl.hidden = true;
    resultsEl.innerHTML = "";
  }

  function ask() {
    var q = inputEl.value.trim();
    if (!q) {
      showPlaceholder();
      return;
    }
    var items = getAnswers(q);
    showResults(renderResults(items));
  }

  if (submitBtn) submitBtn.addEventListener("click", ask);
  inputEl.addEventListener("keypress", function (e) {
    if (e.key === "Enter") ask();
  });

  // Suggested questions (first 6 from knowledge)
  if (suggestedEl) {
    var suggested = knowledge.slice(0, 6);
    suggestedEl.innerHTML = suggested.map(function (item) {
      return "<button type=\"button\" class=\"qa-suggested-btn\">" + escapeHtml(item.question) + "</button>";
    }).join("");
    suggestedEl.querySelectorAll(".qa-suggested-btn").forEach(function (btn, i) {
      btn.addEventListener("click", function () {
        inputEl.value = suggested[i].question;
        ask();
      });
    });
  }
})();
