(function () {
    var knowledge = [
    {
      keywords: ["add business", "add a business", "new business", "submit business", "create business", "list a business"],
      question: "How do I add a business?",
      answer: "Click <strong>Add Business</strong> in the nav (or go to the Add Business page). Fill in the name, category (food, retail, or services), address, phone, and optional description. You can add a deal or coupon too. Solve the simple math verification to submit. New businesses appear in the directory right away and are saved on your device."
    },
    {
      keywords: ["favorite", "favourites", "heart", "save business", "bookmark", "saved list"],
      question: "How do favorites work?",
      answer: "Click the <strong>heart</strong> on any business card or on its detail page to add it to your Favorites. Open <strong>Favorites</strong> from the nav to see your saved list. Your favorites are stored on this device (browser)."
    },
    {
      keywords: ["leave a review", "write review", "post review", "rating", "star", "comment on"],
      question: "How do I leave a review?",
      answer: "Open a business (click <strong>Details</strong>), scroll to <strong>Add a Review</strong>, enter your name, pick a rating (1–5 stars), write a comment, and solve the quick math verification. Reviews are saved locally and, if you set a backend URL under Shared Reviews, they can be synced across users."
    },
    {
      keywords: ["shared reviews", "sync reviews", "backend url", "reviews across", "other users reviews"],
      question: "What are Shared Reviews?",
      answer: "Shared Reviews let you sync reviews with other users. Click <strong>Shared Reviews</strong> in the nav and enter your backend URL (e.g. your deployed Chrysalis Connect Flask app). Once set, reviews you submit are sent to that server and other users can see them when they load the directory."
    },
    {
      keywords: ["map", "business map", "markers", "where is business", "location map"],
      question: "How does the map work?",
      answer: "Click <strong>Map</strong> in the nav to open the Business Map page. Businesses that have location data (e.g. from a location search or added with an address) appear as markers. Click a marker to see details and <strong>View Details</strong> to open the full business page."
    },
    {
      keywords: ["recommendations", "recommended", "top rated", "trending", "best reviewed", "discover best"],
      question: "What are Recommendations?",
      answer: "Recommendations show you top-rated and trending businesses from your current list. Click <strong>Recommendations</strong> in the nav to see them. The list is sorted by rating so you can discover the best-reviewed places."
    },
    {
      keywords: ["verification", "captcha", "math check", "robot", "bot", "spam"],
      question: "Why is there a verification when I add a review or business?",
      answer: "The quick math verification (e.g. “What is 3 + 5?”) helps reduce spam and bot submissions. It’s a simple step to keep reviews and new business listings cleaner for everyone."
    },
    {
      keywords: ["filter by category", "category filter", "food retail services", "category dropdown", "filter businesses"],
      question: "How do I filter by category?",
      answer: "Use the <strong>Category</strong> dropdown or the category pills (Food, Retail, Services) above the business list. Choose a category and click <strong>Apply</strong> to filter. You can also combine this with search and sort (name, rating, most reviewed)."
    },
    {
      keywords: ["search businesses", "find business", "location search", "city address zip", "use my location", "openstreetmap"],
      question: "How do I search for businesses?",
      answer: "Enter a city, address, or zip code in the location box and click <strong>Search</strong> or <strong>Use My Location</strong>. Results come from OpenStreetMap and are free. You can also use the text search box to filter by name, category, or address after loading businesses."
    },
    {
      keywords: ["reports", "statistics", "analyze data", "report summary", "print report", "download report"],
      question: "Where can I see reports or statistics?",
      answer: "Open <strong>Reports</strong> from the nav (or the Reports page) to see a summary of your data: total businesses, reviews, ratings, and top businesses. You can customize filters and print or download the report."
    },
    {
      keywords: ["help", "how to use", "guide", "get help"],
      question: "Where can I get more help?",
      answer: "On the main page, click <strong>Help</strong> in the nav to open the “How to Use Chrysalis Connect” guide. You can also ask questions here in Q&A for quick answers."
    },
    {
      keywords: ["what is chrysalis", "chrysalis connect", "what is this app"],
      question: "What is Chrysalis Connect?",
      answer: "Chrysalis Connect is a local business discovery app. You can search and browse businesses by location, add new businesses, leave reviews, save favorites, view a map, see recommendations, and run reports on your data."
    },
    {
      keywords: ["deal", "coupon", "discount", "special offer"],
      question: "How do deals or coupons work?",
      answer: "When you <strong>Add a Business</strong>, you can optionally add a deal or coupon (e.g. \"10% off\"). Deals show on the business card and detail page so others can see current offers."
    },
    {
      keywords: ["edit business", "change business", "update listing", "modify business"],
      question: "Can I edit or remove a business?",
      answer: "Businesses are stored on your device. Right now you can add and view them; editing or removing from the in-app list would require that feature to be added. For data you control, you can clear site data in your browser to reset."
    },
    {
      keywords: ["sort", "order by", "sort by name", "sort by rating", "most reviewed"],
      question: "How do I sort the business list?",
      answer: "Use the <strong>Sort</strong> dropdown above the business list. You can sort by <strong>Name</strong>, <strong>Rating</strong>, or <strong>Most Reviewed</strong>. Combine with category filter and search to narrow results."
    },
    {
      keywords: ["contact", "support", "email", "feedback"],
      question: "How do I contact support or give feedback?",
      answer: "Use the <strong>Help</strong> section on the main page for in-app guidance. For feedback or support, check the project repository or documentation linked from the app for contact details."
    }
  ];

    function normalize(s) {
    return (s || "").toLowerCase().trim().replace(/\s+/g, " ");
  }

    function scoreMatch(input, item) {
    var n = normalize(input);
    var q = normalize(item.question);
    var score = 0;
    if (n === q || q.indexOf(n) !== -1 || n.indexOf(q) !== -1) score += 50;
    var inputWords = n.split(/\s+/).filter(Boolean);
    var questionWords = q.replace(/[?!.]/g, "").split(/\s+/).filter(Boolean);
    var phraseOverlap = 0;
    for (var i = 0; i < questionWords.length; i++) {
      if (questionWords[i].length < 2) continue;
      if (n.indexOf(questionWords[i]) !== -1) phraseOverlap += 2;
    }
    if (phraseOverlap >= 4) score += 20;
    var keyStr = item.keywords.join(" ").toLowerCase();
    for (var j = 0; j < item.keywords.length; j++) {
      var kw = item.keywords[j].toLowerCase();
      if (kw.length < 2) continue;
      if (n.indexOf(kw) !== -1) score += kw.indexOf(" ") !== -1 ? 5 : 1;
    }
    for (var k = 0; k < inputWords.length; k++) {
      if (inputWords[k].length < 2) continue;
      if (keyStr.indexOf(inputWords[k]) !== -1) score += 1;
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

    if (suggestedEl) {
    var suggested = knowledge.slice(0, 8);
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
