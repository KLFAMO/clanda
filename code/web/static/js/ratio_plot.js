import { CanvasPlot } from "/static/lib/tsplot/dist/index.js";

let plot = null;

function $(id) {
  return document.getElementById(id);
}

function getFormValue(formId, name) {
  const form = $(formId);
  if (!form) return "";
  const el = form.querySelector(`[name="${name}"]`);
  return el ? el.value : "";
}

function syncCanvasSize() {
  const wrap = $("plotWrap");
  const canvas = $("plot");
  if (!wrap || !canvas) return;

  const w = wrap.clientWidth;
  const h = wrap.clientHeight;
  if (w <= 0 || h <= 0) return;

  if (canvas.width !== w) canvas.width = w;
  if (canvas.height !== h) canvas.height = h;
}

function ensurePlot() {
  const canvas = $("plot");
  if (!canvas) throw new Error("Brak <canvas id='plot'>.");
  syncCanvasSize();
  if (!plot) {
    plot = new CanvasPlot(canvas);
    window._plot = plot;
    console.log("CanvasPlot methods:", Object.getOwnPropertyNames(Object.getPrototypeOf(plot)));
  }
  return plot;
}

function applyDataViaSetOptions(x_tab, y_tab, meta) {
  const p = ensurePlot();

  // To jest NAJPROSTSZY możliwy wariant: setOptions przyjmuje wszystko.
  // Jeśli u Ciebie format danych jest inny, zmienimy TYLKO ten obiekt.
  const opts = {
    title: `ratio: ${meta && meta.start ? meta.start : ""} -> ${meta && meta.goal ? meta.goal : ""}`,
    x_tab: x_tab,
    y_tab: y_tab,
  };

  syncCanvasSize();
  p.setOptions(opts);
  p.render();

  // dodatkowy render po layout
  requestAnimationFrame(() => {
    syncCanvasSize();
    p.render();
  });
}

function extractXYFromTimandaMTS(data) {
  if (!data || data.schema !== "timanda-tsplot" || data.type !== "MTS") {
    return { x_tab: [], y_tab: [], seg0: null };
  }

  if (!Array.isArray(data.segments) || data.segments.length === 0) {
    return { x_tab: [], y_tab: [], seg0: null };
  }

  const seg0 = data.segments[0] || {};
  const x_tab = Array.isArray(seg0.mjd) ? seg0.mjd : [];
  const y_tab = Array.isArray(seg0.val) ? seg0.val : [];

  return { x_tab, y_tab, seg0 };
}



async function fetchRatioAndPlot() {
  const statusEl = $("status");
  const btn = $("btnCompute");

  const apiPath = btn.getAttribute("data-api");
  if (!apiPath) {
    statusEl.textContent = "Brak data-api na przycisku.";
    return;
  }

  const start = getFormValue("pathForm", "start");
  const goal  = getFormValue("pathForm", "goal");
  const fmjd  = getFormValue("pathForm", "fmjd");
  const tmjd  = getFormValue("pathForm", "tmjd");

  statusEl.textContent = "Liczenie…";
  console.log("fetchRatioAndPlot params:", { start, goal, fmjd, tmjd });

  const apiUrl = new URL(apiPath, window.location.origin);
  apiUrl.searchParams.set("start", start);
  apiUrl.searchParams.set("goal", goal);
  apiUrl.searchParams.set("fmjd", fmjd);
  apiUrl.searchParams.set("tmjd", tmjd);

  const resp = await fetch(apiUrl.toString());
  if (!resp.ok) {
    statusEl.textContent = "Błąd API: " + await resp.text();
    return;
  }

  const data = await resp.json();
  ensurePlot();
  plot.setData(data);
}

window.addEventListener("DOMContentLoaded", () => {
  ensurePlot();

  const btn = $("btnCompute");
  btn.addEventListener("click", fetchRatioAndPlot);

  // ResizeObserver = render bez F12
  const wrap = $("plotWrap");
  if (wrap && "ResizeObserver" in window) {
    const ro = new ResizeObserver(() => {
      if (!plot) return;
      syncCanvasSize();
      plot.render();
    });
    ro.observe(wrap);
  }

  window.addEventListener("resize", () => {
    if (!plot) return;
    syncCanvasSize();
    plot.render();
  });

  window.addEventListener("load", () => {
    if (!plot) return;
    syncCanvasSize();
    plot.render();
  });
});
