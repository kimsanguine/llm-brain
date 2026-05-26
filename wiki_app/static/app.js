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

// --- 페이지 선택 ---
async function selectPage(slug) {
  state.selectedSlug = slug;
  setHash({ q: state.query, page: slug });
  renderResultList();

  els.pageView.innerHTML = `<div class="page-loading">로드 중…</div>`;
  try {
    const r = await fetch(`/api/page/${slug}`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    state.pageData = await r.json();
    renderPage();
  } catch (e) {
    els.pageView.innerHTML = `<div class="page-loading">오류: ${e.message}</div>`;
  }
}

function renderPage() {
  const p = state.pageData;
  if (!p) return;
  const tags = (p.frontmatter.tags || []).map(t => `<span class="result-card-meta">#${t}</span>`).join(" ");
  els.pageView.innerHTML = `
    <div class="ai-toggle-row">
      <button class="ai-toggle" id="ai-toggle-btn">✨ AI 답변</button>
    </div>
    <h1>${escapeHtml(p.title)}</h1>
    <div class="page-meta">
      ${p.category} · in ${p.inbound} / out ${p.outbound} · access ${p.frontmatter.access_count || 0} · ${tags}
    </div>
    <div class="page-content">${p.html}</div>
    ${maybeAiCtaBox()}
  `;
  // wikilink 클릭 위임
  els.pageView.querySelectorAll("a[data-link]").forEach(a => {
    a.addEventListener("click", (e) => {
      e.preventDefault();
      selectPage(a.dataset.link);
    });
  });
  // AI 토글 (Task 12)
  const aiBtn = $("#ai-toggle-btn");
  if (aiBtn) {
    aiBtn.addEventListener("click", () => {
      const slugs = state.results.map(r => r.slug).slice(0, 5);
      callAI(state.query || p.title, slugs);
    });
  }
  // AI CTA box (결과 부족 시)
  const ctaBtn = $("#ai-cta-box-btn");
  if (ctaBtn) {
    ctaBtn.addEventListener("click", () => {
      const slugs = state.results.map(r => r.slug);
      callAI(state.query, slugs);
    });
  }
}

function maybeAiCtaBox() {
  // 결과 < 3개일 때만 결과 영역 아래에 큰 박스 CTA
  if (state.results.length > 0 && state.results.length < 3) {
    return `
      <div class="ai-cta-box">
        <div class="ai-cta-box-title">✨ 결과가 충분하지 않으신가요?</div>
        <div class="ai-cta-box-desc">위 ${state.results.length}개 페이지를 컨텍스트로 AI가 직접 답변해드릴 수 있어요.</div>
        <button id="ai-cta-box-btn" class="ai-cta-box-btn">"${escapeHtml(state.query)}" — AI에게 물어보기 →</button>
      </div>
    `;
  }
  return "";
}

// --- AI 호출 ---
async function callAI(question, contextSlugs) {
  const modal = ensureAiModal();
  modal.classList.remove("hidden");
  modal.querySelector(".ai-modal-body").innerHTML = `
    <div class="ai-modal-question">Q: ${escapeHtml(question)}</div>
    <div class="ai-modal-loading">
      AI 답변 생성 중<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>
    </div>
    <div class="ai-modal-answer" id="ai-stream-output" style="display:none"></div>
    <div class="ai-modal-context" id="ai-stream-sources" style="display:none"></div>
  `;

  try {
    const r = await fetch("/api/ai-answer/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, context_slugs: contextSlugs }),
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);

    const reader = r.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";
    const out = modal.querySelector("#ai-stream-output");
    const sourcesEl = modal.querySelector("#ai-stream-sources");
    let answerSoFar = "";
    let gotFirstChunk = false;

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      // SSE events parsed by `\n\n` separator
      const events = buffer.split("\n\n");
      buffer = events.pop() || "";
      for (const evt of events) {
        const ev = parseSseEvent(evt);
        if (!ev) continue;
        if (ev.event === "meta") {
          const slugs = ev.data.context_slugs || [];
          if (slugs.length) {
            sourcesEl.style.display = "block";
            sourcesEl.innerHTML = `<strong>참고한 wiki 페이지:</strong> ${slugs.map(s => `<a href="#page=${encodeURIComponent(s)}" onclick="document.getElementById('ai-modal').classList.add('hidden')"><code>${s}</code></a>`).join(", ")}`;
          }
        } else if (ev.event === "chunk") {
          if (!gotFirstChunk) {
            modal.querySelector(".ai-modal-loading").style.display = "none";
            out.style.display = "block";
            gotFirstChunk = true;
          }
          answerSoFar += ev.data.text || "";
          out.innerHTML = escapeHtml(answerSoFar).replace(/\n/g, "<br>");
          out.scrollTop = out.scrollHeight;
        } else if (ev.event === "done") {
          modal.querySelector(".ai-modal-loading").style.display = "none";
          if (!gotFirstChunk) {
            out.style.display = "block";
            out.innerHTML = "<em>(빈 응답)</em>";
          }
        } else if (ev.event === "error") {
          modal.querySelector(".ai-modal-loading").style.display = "none";
          out.style.display = "block";
          out.innerHTML = `<span style="color:#dc2626">오류: ${escapeHtml(ev.data.message || "unknown")}</span>`;
        }
      }
    }
  } catch (e) {
    modal.querySelector(".ai-modal-body").innerHTML =
      `<div class="ai-modal-status">네트워크 오류: ${escapeHtml(e.message)}</div>`;
  }
}

function parseSseEvent(raw) {
  const lines = raw.split("\n").filter(l => l.trim());
  if (!lines.length) return null;
  const out = { event: "message", data: null };
  for (const line of lines) {
    if (line.startsWith("event:")) out.event = line.slice(6).trim();
    else if (line.startsWith("data:")) {
      try { out.data = JSON.parse(line.slice(5).trim()); }
      catch { out.data = line.slice(5).trim(); }
    }
  }
  return out;
}

function ensureAiModal() {
  let modal = document.getElementById("ai-modal");
  if (modal) return modal;
  modal = document.createElement("div");
  modal.id = "ai-modal";
  modal.className = "ai-modal hidden";
  modal.innerHTML = `
    <div class="ai-modal-card">
      <button class="ai-modal-close" aria-label="닫기">×</button>
      <h3>✨ AI 답변</h3>
      <div class="ai-modal-body"></div>
    </div>
  `;
  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.classList.add("hidden");
  });
  modal.querySelector(".ai-modal-close").addEventListener("click", () => modal.classList.add("hidden"));
  window.addEventListener("hashchange", () => modal.classList.add("hidden"));
  // ESC key support
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !modal.classList.contains("hidden")) {
      modal.classList.add("hidden");
    }
  });
  document.body.appendChild(modal);
  return modal;
}

init();
