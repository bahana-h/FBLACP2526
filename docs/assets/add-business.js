// Add Business page: form submit writes to localStorage (cc-data) and redirects to index
(function () {
  var form = document.getElementById("addBusinessForm");
  var captchaLabel = document.getElementById("captchaLabel");
  var captchaInput = document.getElementById("captchaInput");
  var formError = document.getElementById("formError");

  var captchaA = Math.floor(Math.random() * 10) + 1;
  var captchaB = Math.floor(Math.random() * 10) + 1;
  var captchaAnswer = String(captchaA + captchaB);

  if (captchaLabel) captchaLabel.textContent = "Verification: What is " + captchaA + " + " + captchaB + "? *";

  function getStored() {
    try {
      var raw = localStorage.getItem("cc-data");
      if (!raw) return { businesses: [], favorites: [] };
      var data = JSON.parse(raw);
      return { businesses: data.businesses || [], favorites: data.favorites || [] };
    } catch (e) {
      return { businesses: [], favorites: [] };
    }
  }

  function setStored(data) {
    localStorage.setItem("cc-data", JSON.stringify(data));
  }

  function showError(msg) {
    if (formError) {
      formError.textContent = msg || "";
      formError.style.display = msg ? "block" : "none";
    }
  }

  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      showError("");

      var name = document.getElementById("bizName").value.trim();
      var category = (document.getElementById("bizCategory").value || "food").toLowerCase();
      var address = document.getElementById("bizAddress").value.trim();
      var phone = (document.getElementById("bizPhone").value || "").trim();
      var description = (document.getElementById("bizDescription").value || "").trim();
      var dealTitle = (document.getElementById("dealTitle").value || "").trim();
      var dealDesc = (document.getElementById("dealDesc").value || "").trim();
      var dealExpires = (document.getElementById("dealExpires").value || "").trim();
      var userCaptcha = (captchaInput && captchaInput.value || "").trim();

      if (!name) {
        showError("Please enter a business name.");
        return;
      }
      if (!address) {
        showError("Please enter an address.");
        return;
      }
      if (userCaptcha !== captchaAnswer) {
        showError("Verification failed. Please try again.");
        return;
      }

      var deals = [];
      if (dealTitle) {
        deals.push({ title: dealTitle, description: dealDesc, expires: dealExpires });
      }

      var newBiz = {
        id: "biz_" + Date.now(),
        name: name,
        category: category,
        address: address,
        phone: phone || "No phone listed",
        description: description || "",
        deals: deals,
        reviews: []
      };

      var stored = getStored();
      stored.businesses.push(newBiz);
      setStored(stored);

      window.location.href = "index.html#directory";
    });
  }
})();
