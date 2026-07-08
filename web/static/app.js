/* ── Estado ──────────────────────────────────────────────────────────────── */
let currentPage = "dashboard";
let sse = null;
let logsDatas = [];

// Páginas que exibem o terminal compartilhado
const TERMINAL_PAGES = new Set(["logs","scraper","amaweb","relatorio"]);

/* ── Navegação ───────────────────────────────────────────────────────────── */
function navigate(page) {
  document.querySelectorAll(".nav-item").forEach(el => {
    el.classList.toggle("active", el.dataset.page === page);
  });
  document.querySelectorAll(".page").forEach(el => {
    el.classList.toggle("active", el.id === "page-" + page);
  });

  // Mostra/oculta terminal compartilhado
  const termWrapper = document.getElementById("shared-terminal");
  termWrapper.style.display = TERMINAL_PAGES.has(page) ? "flex" : "none";

  const meta = {
    dashboard:  ["📊  Dashboard",             "Visão geral"],
    logs:       ["📋  Analisador de Logs",     "XML → Erros via SSH"],
    scraper:    ["🗂️  Scraper de Imagens",     "Extração Web"],
    amaweb:     ["🕵️  AMAWeb",                "Acessibilidade"],
    relatorio:  ["📄  Relatório Consolidado",  "Exporta todos os dados"],
    historico:  ["📜  Histórico",              "Execuções anteriores"],
  };
  const [title, badge] = meta[page] || [page, ""];
  document.getElementById("topbar-title").textContent = title;
  document.getElementById("topbar-badge").textContent = badge;

  currentPage = page;
  if (page === "dashboard") loadDashboard();
  if (page === "historico") loadHistorico();
}

/* ── Terminal ────────────────────────────────────────────────────────────── */
function term() { return document.getElementById("terminal"); }

function termAppend(text, tag) {
  const span = document.createElement("span");
  span.className = "t-" + (tag || "normal");
  span.textContent = text;
  term().appendChild(span);
  term().scrollTop = term().scrollHeight;
}

function termClear() {
  term().innerHTML = "";
}

function termHeader() {
  const ts = new Date().toLocaleTimeString("pt-BR");
  termAppend("\n" + "─".repeat(58) + "\n", "dim");
  termAppend("  Iniciado em " + ts + "\n", "dim");
  termAppend("─".repeat(58) + "\n\n", "dim");
}

function termFooter() {
  const ts = new Date().toLocaleTimeString("pt-BR");
  termAppend("\n" + "─".repeat(58) + "\n", "dim");
  termAppend("  Finalizado em " + ts + "\n", "dim");
  termAppend("─".repeat(58) + "\n", "dim");
}

/* ── Barra de progresso ──────────────────────────────────────────────────── */
function setProgress(pct) {
  const el = document.getElementById("progress-fill");
  if (el) el.style.width = (Math.min(pct, 1) * 100) + "%";
}

/* ── Status bar ──────────────────────────────────────────────────────────── */
function setStatus(text, state) {
  document.getElementById("status-dot").className = "status-dot " + (state || "ok");
  document.getElementById("status-text").textContent = text;
}

/* ── SSE ─────────────────────────────────────────────────────────────────── */
function connectSSE() {
  if (sse) { sse.close(); sse = null; }
  sse = new EventSource("/stream");
  sse.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    if (msg.tag === "ping") return;
    if (msg.tag === "DONE") {
      termFooter();
      setStatus("Concluído", "ok");
      setProgress(1);
      setRunning(false);
      sse.close(); sse = null;
      return;
    }
    if (msg.tag === "PROGRESS") { setProgress(msg.value); return; }
    termAppend(msg.text || "", msg.tag);
  };
  sse.onerror = () => { if (sse) { sse.close(); sse = null; } };
}

/* ── Controle de botões ──────────────────────────────────────────────────── */
function setRunning(running) {
  document.querySelectorAll(".btn-run").forEach(b => b.disabled = running);
  document.querySelectorAll(".btn-stop").forEach(b => b.disabled = !running);
  document.querySelectorAll(".spinner").forEach(s => s.classList.toggle("active", running));
}

/* ── Start genérico ──────────────────────────────────────────────────────── */
async function startModule(module, payload) {
  clearErrors();
  termClear();
  termHeader();
  setProgress(0);
  setStatus("Executando " + module + "...", "busy");
  setRunning(true);
  connectSSE();

  const res = await fetch("/run/" + module, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!data.ok) {
    if (sse) { sse.close(); sse = null; }
    setRunning(false);
    setStatus("Erro", "error");
    termAppend("  [ERRO] " + data.error + "\n", "error");
    showError(data.error);
  }
}

async function stopModule() {
  await fetch("/stop", { method: "POST" });
  setStatus("Parando...", "busy");
}

function clearErrors() {
  document.querySelectorAll(".error-msg").forEach(el => el.textContent = "");
}
function showError(msg) {
  document.querySelectorAll(".error-msg").forEach(el => el.textContent = msg);
}

/* ── Módulo: Logs ────────────────────────────────────────────────────────── */
function addDate() {
  const inp = document.getElementById("log-date-input");
  const val = inp.value.trim();
  const err = document.getElementById("log-date-error");
  if (!/^\d{2}\/\d{2}\/\d{4}$/.test(val)) {
    err.textContent = "Data inválida. Use dd/mm/aaaa."; return;
  }
  if (logsDatas.includes(val)) {
    err.textContent = "Data já adicionada."; return;
  }
  err.textContent = "";
  logsDatas.push(val);
  renderDateList();
  inp.value = "";
}

function removeDate(val) {
  logsDatas = logsDatas.filter(d => d !== val);
  renderDateList();
}

function renderDateList() {
  const container = document.getElementById("date-list");
  if (!logsDatas.length) {
    container.innerHTML = '<span class="t-dim" style="font-size:11px">Nenhuma data adicionada</span>';
    return;
  }
  container.innerHTML = "";
  logsDatas.forEach(d => {
    const tag = document.createElement("span");
    tag.className = "date-tag";
    tag.innerHTML = `${d} <span class="rm" onclick="removeDate('${d}')">✕</span>`;
    container.appendChild(tag);
  });
}

function runLogs() {
  const elastic = [...document.querySelectorAll(".chk-elastic:checked")].map(c => c.value);
  const liferay = [...document.querySelectorAll(".chk-liferay:checked")].map(c => c.value);
  if (!logsDatas.length) { showError("Adicione ao menos uma data."); return; }
  startModule("logs", { datas: logsDatas, elastic, liferay });
}

/* ── Outros módulos ──────────────────────────────────────────────────────── */
function runScraper() {
  startModule("scraper", {
    links:  document.getElementById("scraper-links").value,
    output: document.getElementById("scraper-output").value,
  });
}

function runAmaweb() {
  startModule("amaweb", {
    urls:      document.getElementById("ama-urls").value,
    result:    document.getElementById("ama-result").value,
    threshold: parseFloat(document.getElementById("ama-threshold").value) || 5.0,
  });
}

function runRelatorio() {
  startModule("relatorio", {
    output: document.getElementById("rel-output").value,
  });
}

/* ── Dashboard ───────────────────────────────────────────────────────────── */
async function loadDashboard() {
  const res = await fetch("/historico");
  const entries = await res.json();

  ["logs","scraper","amaweb"].forEach(m => {
    const card = document.getElementById("dash-" + m);
    if (!card) return;
    const entry = entries.find(e => e.modulo === m);
    const sEl = card.querySelector(".dash-status");
    const dEl = card.querySelector(".dash-detail");
    if (entry) {
      const ok = entry.status === "sucesso";
      sEl.innerHTML = `<span style="color:${ok ? "var(--green)" : "var(--red)"}">● ${entry.status.toUpperCase()}</span>&nbsp;&nbsp;<span style="color:var(--text3)">${entry.data}</span>`;
      dEl.textContent = entry.detalhes || "";
    } else {
      sEl.textContent = "Nenhuma execução registrada";
      dEl.textContent = "";
    }
  });

  const hist = document.getElementById("dash-hist");
  if (!hist) return;
  hist.innerHTML = "";
  if (!entries.length) {
    hist.innerHTML = '<span class="t-dim">  Nenhum registro ainda.\n</span>';
    return;
  }
  entries.slice(0, 30).forEach(e => {
    const ok = e.status === "sucesso";
    const row = document.createElement("div");
    row.style.cssText = "display:flex;gap:8px;font-size:12px;padding:2px 0";
    row.innerHTML =
      `<span class="t-dim" style="min-width:155px">${e.data}</span>` +
      `<span class="t-dim" style="min-width:105px">[${e.modulo.toUpperCase()}]</span>` +
      `<span class="${ok ? "tag-sucesso" : "tag-erro"}" style="min-width:85px">${e.status}</span>` +
      `<span class="t-dim">${e.detalhes || ""}</span>`;
    hist.appendChild(row);
  });
}

/* ── Histórico ───────────────────────────────────────────────────────────── */
async function loadHistorico() {
  const res = await fetch("/historico");
  const entries = await res.json();
  const tbody = document.getElementById("hist-tbody");
  if (!tbody) return;
  tbody.innerHTML = "";
  entries.forEach(e => {
    const ok = e.status === "sucesso";
    const tr = document.createElement("tr");
    tr.innerHTML =
      `<td>${e.data}</td><td>${e.modulo.toUpperCase()}</td>` +
      `<td class="${ok ? "tag-sucesso" : "tag-erro"}">${e.status}</td>` +
      `<td>${e.detalhes || ""}</td>`;
    tbody.appendChild(tr);
  });
  if (!entries.length) {
    tbody.innerHTML = '<tr><td colspan="4" style="color:var(--text3);text-align:center;padding:20px">Nenhum registro encontrado.</td></tr>';
  }
}

/* ── Relógio ─────────────────────────────────────────────────────────────── */
function tickClock() {
  const el = document.getElementById("clock");
  if (el) el.textContent = new Date().toLocaleString("pt-BR");
}
setInterval(tickClock, 1000);
tickClock();

/* ── Init ────────────────────────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  const inp = document.getElementById("log-date-input");
  if (inp) inp.addEventListener("keydown", e => { if (e.key === "Enter") addDate(); });
  navigate("dashboard");
});
