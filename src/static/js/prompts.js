(function () {
  // State
  var currentPage = 1;
  var loading = false;
  var hasNext = true;
  var activeCategories = new Set();
  var activeProviders = new Set();
  var searchQuery = "";
  var debounceTimer = null;
  var currentModalContent = "";

  var grid = document.getElementById("prompts-grid");
  var sentinel = document.getElementById("scroll-sentinel");
  var spinner = document.getElementById("loading-spinner");
  var emptyState = document.getElementById("empty-state");
  var cardTemplate = document.getElementById("card-template");
  var badgeTemplate = document.getElementById("badge-template");

  // Infinite Scroll Observer
  var observer = new IntersectionObserver(
    function (entries) {
      if (entries[0].isIntersecting && !loading && hasNext) {
        loadPrompts();
      }
    },
    { rootMargin: "200px" }
  );
  observer.observe(sentinel);

  // Filter Chips
  document.querySelectorAll(".filter-chip").forEach(function (chip) {
    chip.addEventListener("click", function () {
      var type = chip.dataset.filterType;
      var value = parseInt(chip.dataset.filterValue);
      var set = type === "category" ? activeCategories : activeProviders;

      if (set.has(value)) {
        set.delete(value);
        chip.classList.remove(
          "bg-indigo-600",
          "text-white",
          "border-indigo-600",
          "hover:bg-indigo-700"
        );
        chip.classList.add(
          "bg-white",
          "dark:bg-gray-800",
          "text-gray-700",
          "dark:text-gray-300",
          "border-gray-300",
          "dark:border-gray-600",
          "hover:bg-gray-100",
          "dark:hover:bg-gray-700"
        );
      } else {
        set.add(value);
        chip.classList.add(
          "bg-indigo-600",
          "text-white",
          "border-indigo-600",
          "hover:bg-indigo-700"
        );
        chip.classList.remove(
          "bg-white",
          "dark:bg-gray-800",
          "text-gray-700",
          "dark:text-gray-300",
          "border-gray-300",
          "dark:border-gray-600",
          "hover:bg-gray-100",
          "dark:hover:bg-gray-700"
        );
      }

      resetAndLoad();
    });
  });

  // Search
  document.getElementById("search-input").addEventListener("input", function (e) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(function () {
      searchQuery = e.target.value.trim();
      resetAndLoad();
    }, 300);
  });

  function resetAndLoad() {
    currentPage = 1;
    hasNext = true;
    grid.replaceChildren();
    emptyState.classList.add("hidden");
    loadPrompts();
  }

  function createBadge(name, colorClass) {
    var badge = badgeTemplate.content.cloneNode(true).querySelector("span");
    badge.textContent = name;
    badge.classList.add.apply(badge.classList, colorClass.split(" "));
    return badge;
  }

  function createCard(p) {
    var card = cardTemplate.content.cloneNode(true).querySelector("article");
    card.querySelector(".card-title").textContent = p.title;
    card.querySelector(".card-preview").textContent = p.preview;
    card.querySelector(".card-author").textContent = p.author;
    card.querySelector(".card-date").textContent = p.updated_at;

    var categoriesContainer = card.querySelector(".card-categories");
    if (p.categories.length) {
      categoriesContainer.classList.remove("hidden");
      categoriesContainer.classList.add("flex");
      p.categories.forEach(function (c) {
        categoriesContainer.appendChild(
          createBadge(c.name, "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200")
        );
      });
    }

    var providersContainer = card.querySelector(".card-providers");
    if (p.providers.length) {
      providersContainer.classList.remove("hidden");
      providersContainer.classList.add("flex");
      p.providers.forEach(function (pr) {
        providersContainer.appendChild(
          createBadge(pr.name, "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200")
        );
      });
    }

    card.addEventListener("click", function () {
      openModal(p.id);
    });

    var copyBtn = card.querySelector(".card-copy-btn");
    copyBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      copyFromCard(p.id, copyBtn);
    });

    return card;
  }

  function loadPrompts() {
    if (loading || !hasNext) return;
    loading = true;
    spinner.classList.remove("hidden");

    var params = new URLSearchParams();
    params.set("page", currentPage);
    if (searchQuery) params.set("search", searchQuery);
    if (activeCategories.size)
      params.set("categories", Array.from(activeCategories).join(","));
    if (activeProviders.size)
      params.set("providers", Array.from(activeProviders).join(","));

    fetch("/api/prompts/?" + params.toString())
      .then(function (resp) {
        return resp.json();
      })
      .then(function (data) {
        if (currentPage === 1 && data.prompts.length === 0) {
          emptyState.classList.remove("hidden");
        } else {
          emptyState.classList.add("hidden");
        }

        data.prompts.forEach(function (p) {
          grid.appendChild(createCard(p));
        });

        hasNext = data.has_next;
        currentPage++;
      })
      .catch(function (err) {
        console.error("Erro ao carregar prompts:", err);
      })
      .finally(function () {
        loading = false;
        spinner.classList.add("hidden");
      });
  }

  // Copy from card (fetches full content)
  function copyFromCard(promptId, btn) {
    fetch("/api/prompts/" + promptId + "/")
      .then(function (resp) {
        return resp.json();
      })
      .then(function (data) {
        return navigator.clipboard.writeText(data.content);
      })
      .then(function () {
        var svgContent = btn.querySelector("svg");
        var originalSvg = svgContent.cloneNode(true);
        btn.textContent = "";
        var span = document.createElement("span");
        span.className = "text-xs font-medium text-indigo-600 dark:text-indigo-400";
        span.textContent = "Copiado!";
        btn.appendChild(span);
        setTimeout(function () {
          btn.textContent = "";
          btn.appendChild(originalSvg);
        }, 2000);
      })
      .catch(function (err) {
        console.error("Erro ao copiar:", err);
      });
  }

  // Modal
  function openModal(promptId) {
    var modal = document.getElementById("prompt-modal");
    fetch("/api/prompts/" + promptId + "/")
      .then(function (resp) {
        return resp.json();
      })
      .then(function (data) {
        currentModalContent = data.content;

        document.getElementById("modal-title").textContent = data.title;
        document.getElementById("modal-author").textContent = "Por: " + data.author;
        document.getElementById("modal-date").textContent = "Atualizado em: " + data.updated_at;
        document.getElementById("modal-content").textContent = data.content;

        var modalCats = document.getElementById("modal-categories");
        var modalProvs = document.getElementById("modal-providers");
        // Keep the label span, remove old badges
        while (modalCats.children.length > 1) modalCats.removeChild(modalCats.lastChild);
        while (modalProvs.children.length > 1) modalProvs.removeChild(modalProvs.lastChild);

        if (data.categories.length) {
          modalCats.classList.remove("hidden");
          modalCats.classList.add("flex");
          data.categories.forEach(function (c) {
            modalCats.appendChild(
              createBadge(c.name, "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200")
            );
          });
        } else {
          modalCats.classList.add("hidden");
          modalCats.classList.remove("flex");
        }

        if (data.providers.length) {
          modalProvs.classList.remove("hidden");
          modalProvs.classList.add("flex");
          data.providers.forEach(function (pr) {
            modalProvs.appendChild(
              createBadge(
                pr.name,
                "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
              )
            );
          });
        } else {
          modalProvs.classList.add("hidden");
          modalProvs.classList.remove("flex");
        }

        modal.classList.remove("hidden");
        document.body.style.overflow = "hidden";
      })
      .catch(function (err) {
        console.error("Erro ao abrir modal:", err);
      });
  }

  function closeModal() {
    document.getElementById("prompt-modal").classList.add("hidden");
    document.body.style.overflow = "";
  }

  function copyModalContent() {
    var btn = document.getElementById("modal-copy-btn");
    var label = btn.querySelector(".copy-label");
    navigator.clipboard
      .writeText(currentModalContent)
      .then(function () {
        var originalText = label.textContent;
        label.textContent = "Copiado!";
        setTimeout(function () {
          label.textContent = originalText;
        }, 2000);
      })
      .catch(function (err) {
        console.error("Erro ao copiar:", err);
      });
  }

  // Close modal on Escape
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeModal();
  });

  // Expose to inline onclick handlers
  window.openModal = openModal;
  window.closeModal = closeModal;
  window.copyModalContent = copyModalContent;

  // Initial load
  loadPrompts();
})();
