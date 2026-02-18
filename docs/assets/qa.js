// Intelligent Q&A: phrase + keyword matching for accurate answers
(function () {
  var knowledge = [
    {
      keywords: ["add", "business", "new", "list", "submit", "create"],
      phrases: ["how do i add a business", "add a business", "submit a business", "create a listing", "list my business"],
      question: "How do I add a business?",
      answer: "Click <strong>Add Business</strong> in the nav (or go to the Add Business page). Fill in the name, category (food, retail, or services), address, phone, and optional description. You can add a deal or coupon too. Solve the simple math verification to submit. New businesses appear in the directory right away and are saved on your device."
    },
    {
      keywords: ["favorite", "favourites", "heart", "save", "bookmark"],
      phrases: ["how do favorites work", "how do i save", "add to favorites", "remove favorite", "delete favorite", "where are my favorites"],
      question: "How do favorites work?",
      answer: "Click the <strong>heart</strong> on any business card or on its detail page to add it to your Favorites. Open <strong>Favorites</strong> from the nav to see your saved list. To remove one, open Favorites and click the heart again to unfavorite. Your favorites are stored on this device (browser)."
    },
    {
      keywords: ["review", "rating", "star", "comment", "leave"],
      phrases: ["how do i leave a review", "leave a review", "write a review", "rate a business", "add review"],
      question: "How do I leave a review?",
      answer: "Open a business (click <strong>Details</strong>), scroll to <strong>Add a Review</strong>, enter your name, pick a rating (1–5 stars), write a comment, and solve the quick math verification. Reviews are saved locally and, if you set a backend URL under Shared Reviews, they can be synced across users."
    },
    {
      keywords: ["shared", "reviews", "sync", "backend", "url", "across", "device"],
      phrases: ["what are shared reviews", "shared reviews", "sync reviews", "backend url", "reviews across devices"],
      question: "What are Shared Reviews?",
      answer: "Shared Reviews let you sync reviews with other users. Click <strong>Shared Reviews</strong> in the nav and enter your backend URL (e.g. your deployed Chrysalis Connect Flask app). Once set, reviews you submit are sent to that server and other users can see them when they load the directory."
    },
    {
      keywords: ["map", "location", "marker", "where"],
      phrases: ["how does the map work", "business map", "where is the map", "see businesses on map"],
      question: "How does the map work?",
      answer: "Click <strong>Map</strong> in the nav to open the Business Map page. Businesses that have location data (e.g. from a location search or added with an address) appear as markers. Click a marker to see details and <strong>View Details</strong> to open the full business page."
    },
    {
      keywords: ["recommendation", "recommended", "top", "rated", "trending"],
      phrases: ["what are recommendations", "recommendations", "top rated", "best businesses"],
      question: "What are Recommendations?",
      answer: "Recommendations show you top-rated and trending businesses from your current list. Click <strong>Recommendations</strong> in the nav to see them. The list is sorted by rating so you can discover the best-reviewed places."
    },
    {
      keywords: ["verification", "captcha", "math", "robot", "bot"],
      phrases: ["why verification", "why math verification", "captcha", "robot check"],
      question: "Why is there a verification when I add a review or business?",
      answer: "The quick math verification (e.g. “What is 3 + 5?”) helps reduce spam and bot submissions. It’s a simple step to keep reviews and new business listings cleaner for everyone."
    },
    {
      keywords: ["category", "food", "retail", "services", "filter"],
      phrases: ["how do i filter by category", "filter by category", "what categories", "food retail services"],
      question: "How do I filter by category?",
      answer: "Use the <strong>Category</strong> dropdown or the category pills (Food, Retail, Services) above the business list. Choose a category and click <strong>Apply</strong> to filter. You can also combine this with search and sort (name, rating, most reviewed)."
    },
    {
      keywords: ["search", "find", "look", "location", "city", "address"],
      phrases: ["how do i search", "search for businesses", "find businesses", "search by location", "use my location"],
      question: "How do I search for businesses?",
      answer: "Enter a city, address, or zip code in the location box and click <strong>Search</strong> or <strong>Use My Location</strong>. Results come from OpenStreetMap and are free. You can also use the text search box to filter by name, category, or address after loading businesses."
    },
    {
      keywords: ["report", "analyze", "stat", "summary", "data"],
      phrases: ["where can i see reports", "reports", "statistics", "print report", "download report"],
      question: "Where can I see reports or statistics?",
      answer: "Open <strong>Reports</strong> from the nav (or the Reports page) to see a summary of your data: total businesses, reviews, ratings, and top businesses. You can customize filters and print or download the report."
    },
    {
      keywords: ["help", "how", "what", "why", "where", "when"],
      phrases: ["where can i get help", "more help", "how to use", "help guide"],
      question: "Where can I get more help?",
      answer: "On the main page, click <strong>Help</strong> in the nav to open the “How to Use Chrysalis Connect” guide. You can also ask questions here in Q&A for quick answers."
    },
    {
      keywords: ["chrysalis", "connect", "what is", "app", "this"],
      phrases: ["what is chrysalis connect", "what is this app", "what is this site"],
      question: "What is Chrysalis Connect?",
      answer: "Chrysalis Connect is a local business discovery app. You can search for businesses by location, browse by category (Food, Retail, Services), save favorites, leave reviews, view businesses on a map, and add new businesses. Data can be loaded from OpenStreetMap or stored locally; reviews can be synced via a backend if you set one under Shared Reviews."
    },
    {
      keywords: ["edit", "change", "update", "business", "details"],
      phrases: ["can i edit a business", "edit a business", "change business info", "update listing"],
      question: "Can I edit or delete a business?",
      answer: "Businesses you add locally can be managed from your device; the app does not support in-page edit/delete of individual listings in this version. To change or remove a business you added, you would need to clear local data or use the same Add Business flow to add a corrected entry. For data loaded from a backend or OpenStreetMap, the listing is read-only here."
    },
    {
      keywords: ["contact", "phone", "call", "email", "address"],
      phrases: ["how do i contact a business", "contact business", "phone number", "business address"],
      question: "How do I contact a business?",
      answer: "On a business’s detail page you’ll see its address and phone (if provided). Use that info to call or visit. Some listings may also show a description or website if the person who added them included it."
    },
    {
      keywords: ["data", "where", "from", "openstreetmap", "stored"],
      phrases: ["where does the data come from", "where is data stored", "openstreetmap"],
      question: "Where does the business data come from?",
      answer: "Businesses can come from two places: (1) <strong>OpenStreetMap</strong> — when you search by location or use “Use My Location,” results are fetched from OSM and are free to use. (2) <strong>Local or backend</strong> — businesses you add are saved on your device; if you use a backend URL under Shared Reviews, reviews (and sometimes business data) can be synced with that server."
    },
    {
      keywords: ["deal", "coupon", "discount", "offer"],
      phrases: ["how do i add a deal", "deals", "coupons", "discounts"],
      question: "How do deals or coupons work?",
      answer: "When you <strong>Add a Business</strong>, you can optionally enter a deal or coupon (e.g. “10% off”). That text is shown on the business’s detail page. There’s no separate deals list; deals are part of each business listing."
    }
  ];

  function normalize(s) {
    return (s || "").toLowerCase().trim().replace(/\s+/g, " ");
  }

  function phraseMatchScore(normInput, item) {
    var q = normalize(item.question);
    if (normInput === q) return 100;
    if (q.indexOf(normInput) !== -1 || normInput.indexOf(q) !== -1) return 80;
    var phrases = item.phrases || [];
    for (var i = 0; i < phrases.length; i++) {
      var p = normalize(phrases[i]);
      if (normInput === p) return 90;
      if (p.indexOf(normInput) !== -1) return 70;
      if (normInput.indexOf(p) !== -1) return 70;
    }
    return 0;
  }

  function scoreMatch(input, item) {
    var normInput = normalize(input);
    var score = phraseMatchScore(normInput, item);
    var words = normInput.split(/\s+/).filter(Boolean);
    var keyStr = item.keywords.join(" ") + " " + normalize(item.question);
    if (item.phrases) keyStr += " " + item.phrases.map(normalize).join(" ");
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
