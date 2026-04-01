/**
 * Web Scraper Frontend Application
 * Handles all UI interactions and API calls
 */

// API Base URL
const API_BASE = "/api";

// DOM Elements
const elements = {
  // Navigation
  navBtns: document.querySelectorAll(".nav-btn"),
  tabContents: document.querySelectorAll(".tab-content"),

  // Scraper Tab
  scrapeForm: document.getElementById("scrape-form"),
  urlInput: document.getElementById("url-input"),
  scrapeBtn: document.getElementById("scrape-btn"),
  resultsSection: document.getElementById("results-section"),
  resultsCount: document.getElementById("results-count"),
  articlesGrid: document.getElementById("articles-grid"),
  errorMessage: document.getElementById("error-message"),
  errorText: document.getElementById("error-text"),
  exportJsonBtn: document.getElementById("export-json-btn"),
  exportCsvBtn: document.getElementById("export-csv-btn"),

  // History Tab
  historyTbody: document.getElementById("history-tbody"),
  historyEmpty: document.getElementById("history-empty"),
  refreshHistoryBtn: document.getElementById("refresh-history-btn"),
  exportAllJson: document.getElementById("export-all-json"),
  exportAllCsv: document.getElementById("export-all-csv"),

  // Toast
  toast: document.getElementById("toast"),
  toastMessage: document.getElementById("toast-message"),
};

// Current scrape result ID for exports
let currentScrapeId = null;

/**
 * Initialize the application
 */
function init() {
  // Tab navigation
  elements.navBtns.forEach((btn) => {
    btn.addEventListener("click", () => switchTab(btn.dataset.tab));
  });

  // Scrape form
  elements.scrapeForm.addEventListener("submit", handleScrape);

  // Export buttons
  elements.exportJsonBtn.addEventListener("click", () =>
    exportData("json", currentScrapeId),
  );
  elements.exportCsvBtn.addEventListener("click", () =>
    exportData("csv", currentScrapeId),
  );
  elements.exportAllJson.addEventListener("click", () => exportData("json"));
  elements.exportAllCsv.addEventListener("click", () => exportData("csv"));

  // History refresh
  elements.refreshHistoryBtn.addEventListener("click", loadHistory);

  // Load initial history
  loadHistory();
}

/**
 * Switch between tabs
 */
function switchTab(tabName) {
  // Update nav buttons
  elements.navBtns.forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.tab === tabName);
  });

  // Update tab contents
  elements.tabContents.forEach((content) => {
    content.classList.toggle("active", content.id === `${tabName}-tab`);
  });

  // Reload history if switching to history tab
  if (tabName === "history") {
    loadHistory();
  }
}

/**
 * Handle scrape form submission
 */
async function handleScrape(e) {
  e.preventDefault();

  const url = elements.urlInput.value.trim();
  if (!url) return;

  // Get form options
  const extractArticles = elements.scrapeForm.querySelector(
    '[name="extract_articles"]',
  ).checked;
  const extractLinks = elements.scrapeForm.querySelector(
    '[name="extract_links"]',
  ).checked;

  // Show loading state
  setLoading(true);
  hideError();
  hideResults();

  try {
    const response = await fetch(`${API_BASE}/scrape`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        url,
        extract_articles: extractArticles,
        extract_links: extractLinks,
      }),
    });

    const data = await response.json();

    if (data.success) {
      currentScrapeId = data.data.id;
      displayResults(data.data);
      showToast("Scraping completed successfully!", "success");
    } else {
      showError(data.message || "Scraping failed");
      showToast("Scraping failed", "error");
    }
  } catch (error) {
    showError(`Request failed: ${error.message}`);
    showToast("Request failed", "error");
  } finally {
    setLoading(false);
  }
}

/**
 * Display scraping results
 */
function displayResults(data) {
  const articles = data.articles || [];

  elements.resultsCount.textContent = articles.length;
  elements.articlesGrid.innerHTML = "";

  if (articles.length === 0) {
    elements.articlesGrid.innerHTML = `
            <div class="empty-state">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="12" y1="8" x2="12" y2="12"/>
                    <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <p>No articles found</p>
                <span>Try a different URL or check if the page has article content</span>
            </div>
        `;
  } else {
    articles.forEach((article) => {
      const card = createArticleCard(article);
      elements.articlesGrid.appendChild(card);
    });
  }

  elements.resultsSection.classList.remove("hidden");
}

/**
 * Create an article card element
 */
function createArticleCard(article) {
  const card = document.createElement("div");
  card.className = "article-card";

  let imageHtml = "";
  if (article.image_url) {
    imageHtml = `<img src="${escapeHtml(article.image_url)}" alt="" class="article-image" onerror="this.style.display='none'">`;
  }

  let categoryHtml = "";
  if (article.category) {
    categoryHtml = `<span class="article-category">${escapeHtml(article.category)}</span>`;
  }

  let titleHtml = escapeHtml(article.title || "Untitled");
  if (article.url) {
    titleHtml = `<a href="${escapeHtml(article.url)}" target="_blank" rel="noopener">${titleHtml}</a>`;
  }

  card.innerHTML = `
        ${imageHtml}
        ${categoryHtml}
        <h4 class="article-title">${titleHtml}</h4>
        <p class="article-excerpt">${escapeHtml(article.excerpt || article.content || "No content available").substring(0, 200)}...</p>
        <div class="article-meta">
            <span>${escapeHtml(article.author || "Unknown author")}</span>
            <span>${escapeHtml(article.date || "")}</span>
        </div>
    `;

  return card;
}

/**
 * Load scraping history
 */
async function loadHistory() {
  try {
    const response = await fetch(`${API_BASE}/history?limit=50`);
    const data = await response.json();

    if (data.success) {
      displayHistory(data.items);
    }
  } catch (error) {
    console.error("Failed to load history:", error);
  }
}

/**
 * Display history in table
 */
function displayHistory(items) {
  elements.historyTbody.innerHTML = "";

  if (items.length === 0) {
    elements.historyEmpty.classList.remove("hidden");
    document.getElementById("history-table-container").classList.add("hidden");
    return;
  }

  elements.historyEmpty.classList.add("hidden");
  document.getElementById("history-table-container").classList.remove("hidden");

  items.forEach((item) => {
    const row = document.createElement("tr");

    const statusClass =
      item.status === "success"
        ? "success"
        : item.status === "failed"
          ? "failed"
          : "pending";

    const date = new Date(item.scraped_at).toLocaleString();

    row.innerHTML = `
            <td>${item.id}</td>
            <td class="url-cell" title="${escapeHtml(item.url)}">${escapeHtml(item.url)}</td>
            <td><span class="status-badge ${statusClass}">${escapeHtml(item.status)}</span></td>
            <td>${item.article_count}</td>
            <td>${date}</td>
            <td>
                <div class="action-btns">
                    <button class="action-btn view" onclick="viewRecord(${item.id})" title="View">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                            <circle cx="12" cy="12" r="3"/>
                        </svg>
                    </button>
                    <button class="action-btn delete" onclick="deleteRecord(${item.id})" title="Delete">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="3 6 5 6 21 6"/>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                        </svg>
                    </button>
                </div>
            </td>
        `;

    elements.historyTbody.appendChild(row);
  });
}

/**
 * View a specific record
 */
async function viewRecord(id) {
  try {
    const response = await fetch(`${API_BASE}/history/${id}`);
    const data = await response.json();

    if (data.success) {
      // Switch to scraper tab and display results
      switchTab("scraper");
      currentScrapeId = data.data.id;
      elements.urlInput.value = data.data.url;
      displayResults(data.data);
    }
  } catch (error) {
    showToast("Failed to load record", "error");
  }
}

/**
 * Delete a record
 */
async function deleteRecord(id) {
  if (!confirm("Are you sure you want to delete this record?")) return;

  try {
    const response = await fetch(`${API_BASE}/history/${id}`, {
      method: "DELETE",
    });

    const data = await response.json();

    if (data.success) {
      showToast("Record deleted", "success");
      loadHistory();
    } else {
      showToast("Failed to delete record", "error");
    }
  } catch (error) {
    showToast("Failed to delete record", "error");
  }
}

/**
 * Export data
 */
function exportData(format, id = null) {
  let url = `${API_BASE}/export/${format}`;
  if (id) {
    url += `?ids=${id}`;
  }

  // Create download link
  const a = document.createElement("a");
  a.href = url;
  a.download = `scrape_export.${format}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);

  showToast(`Exporting as ${format.toUpperCase()}...`, "success");
}

/**
 * Show/hide loading state
 */
function setLoading(loading) {
  elements.scrapeBtn.disabled = loading;
  elements.scrapeBtn.classList.toggle("loading", loading);
}

/**
 * Show error message
 */
function showError(message) {
  elements.errorText.textContent = message;
  elements.errorMessage.classList.remove("hidden");
}

/**
 * Hide error message
 */
function hideError() {
  elements.errorMessage.classList.add("hidden");
}

/**
 * Hide results section
 */
function hideResults() {
  elements.resultsSection.classList.add("hidden");
}

/**
 * Show toast notification
 */
function showToast(message, type = "success") {
  elements.toastMessage.textContent = message;
  elements.toast.className = `toast ${type}`;
  elements.toast.classList.add("show");

  setTimeout(() => {
    elements.toast.classList.remove("show");
  }, 3000);
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Initialize app when DOM is ready
document.addEventListener("DOMContentLoaded", init);
