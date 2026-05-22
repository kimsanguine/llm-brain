// 전역 상태
const state = {
  query: "",
  results: [],
  expanded: false,
  basicTotal: 0,
  selectedSlug: null,
  pageData: null,
};

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const els = {
  meta: $("#meta"),
  viewEmpty: $("#view-empty"),
  viewResults: $("#view-results"),
  viewEmptyResults: $("#view-empty-results"),
  searchForm: $("#search-form"),
  searchInput: $("#search-input"),
  searchForm2: $("#search-form-2"),
  searchInput2: $("#search-input-2"),
  resultsMeta: $("#results-meta"),
  resultsList: $("#results-list"),
  pageView: $("#page-view"),
  emptyTitle: $("#empty-title"),
  emptySub: $("#empty-sub"),
  aiCtaLarge: $("#ai-cta-large"),
};

// --- 초기 로드 ---
async function init() {
  // 메타 정보
  try {
    const r = await fetch("/api/index");
    const data = await r.json();
    els.meta.textContent = `${data.total_pages} pages · ${data.total_links} links`;
  } catch (e) {
    els.meta.textContent = "오프라인";
  }

  // suggestion 버튼
  $$(".suggestion").forEach(b => {
    b.addEventListener("click", () => {
      const q = b.dataset.q || "";
      els.searchInput.value = q;
      doSearch(q);
    });
  });

  // 검색 폼
  els.searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    doSearch(els.searchInput.value);
  });
  els.searchForm2.addEventListener("submit", (e) => {
    e.preventDefault();
    doSearch(els.searchInput2.value);
  });

  // empty state AI CTA
  els.aiCtaLarge.addEventListener("click", () => callAI(state.query, []));

  // hashchange 처리 (Task 11에서 페이지 로드)
  window.addEventListener("hashchange", handleHash);
  handleHash();
}

// --- 검색 ---
async function doSearch(query) {
  query = (query || "").trim();
  state.query = query;
  if (!query) {
    showEmpty();
    return;
  }
  const r = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
  const data = await r.json();
  state.results = data.results;
  state.expanded = data.expanded || false;
  state.basicTotal = data.basic_total || data.total;

  // URL hash 갱신
  setHash({ q: query, page: null });

  if (data.total === 0) {
    showEmptyResults(query);
  } else {
    showResults();
  }
}

function showEmpty() {
  els.viewEmpty.classList.remove("hidden");
  els.viewResults.classList.add("hidden");
  els.viewEmptyResults.classList.add("hidden");
}

function showResults() {
  els.viewEmpty.classList.add("hidden");
  els.viewResults.classList.remove("hidden");
  els.viewEmptyResults.classList.add("hidden");
  els.searchInput2.value = state.query;

  const metaText = state.expanded
    ? `${state.results.length}개 (본문 grep까지 확장)`
    : `${state.results.length}개 매칭`;
  els.resultsMeta.textContent = metaText;

  renderResultList();

  // 첫 카드 자동 선택
  if (state.results.length > 0) {
    selectPage(state.results[0].slug);
  }
}

function showEmptyResults(query) {
  els.viewEmpty.classList.add("hidden");
  els.viewResults.classList.add("hidden");
  els.viewEmptyResults.classList.remove("hidden");
  els.emptyTitle.textContent = "wiki에 직접 매칭되는 페이지가 없어요";
  els.emptySub.textContent = `"${query}" — AI가 wiki 전체에서 관련 페이지를 찾아 답변할 수 있어요.`;
}

function renderResultList() {
  const html = [];
  if (state.expanded) {
    html.push(`<div class="expansion-notice">🔍 결과가 적어 본문까지 자동 검색 — ${state.results.length - state.basicTotal}개 추가</div>`);
  }
  for (const r of state.results) {
    const isActive = r.slug === state.selectedSlug ? "active" : "";
    const snippet = r.snippet
      ? `<div class="result-card-snippet">${highlight(r.snippet, state.query)}</div>`
      : "";
    html.push(`
      <div class="result-card ${isActive}" data-slug="${r.slug}">
        <div class="result-card-title">${r.slug}</div>
        <div class="result-card-desc">${escapeHtml(r.description || "")}</div>
        <div class="result-card-meta">${r.category} · degree ${r.degree} · ${r.match_type}</div>
        ${snippet}
      </div>
    `);
  }
  els.resultsList.innerHTML = html.join("");
  els.resultsList.querySelectorAll(".result-card").forEach(card => {
    card.addEventListener("click", () => selectPage(card.dataset.slug));
  });
}

function highlight(text, query) {
  const escaped = escapeHtml(text);
  if (!query) return escaped;
  const re = new RegExp(`(${query.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&')})`, 'gi');
  return escaped.replace(re, '<mark>$1</mark>');
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}

// --- URL hash ---
function setHash({ q, page }) {
  const parts = [];
  if (q) parts.push(`q=${encodeURIComponent(q)}`);
  if (page) parts.push(`page=${encodeURIComponent(page)}`);
  const newHash = parts.length ? "#" + parts.join("&") : "";
  if (location.hash !== newHash) history.pushState(null, "", newHash || location.pathname);
}

function readHash() {
  const h = location.hash.slice(1);
  const out = {};
  for (const pair of h.split("&")) {
    const [k, v] = pair.split("=");
    if (k) out[k] = decodeURIComponent(v || "");
  }
  return out;
}

async function handleHash() {
  const { q, page } = readHash();
  if (q && q !== state.query) {
    els.searchInput.value = q;
    els.searchInput2.value = q;
    await doSearch(q);
  }
  if (page && page !== state.selectedSlug) {
    await selectPage(page);
  }
}

// --- 페이지 선택 (Task 11에서 구현) ---
async function selectPage(slug) {
  state.selectedSlug = slug;
  setHash({ q: state.query, page: slug });
  renderResultList();
  // TODO Task 11: 페이지 fetch + 렌더
  els.pageView.innerHTML = `<div class="page-loading">페이지 로드 중: ${slug}</div>`;
}

// --- AI 호출 (Task 12에서 구현) ---
async function callAI(question, contextSlugs) {
  // TODO Task 12: 백엔드 호출 + 응답 표시
  alert(`AI 호출 (stub): ${question}`);
}

init();
