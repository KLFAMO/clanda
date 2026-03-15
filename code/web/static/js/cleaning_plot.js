import { CanvasPlot } from "/static/lib/tsplot/dist/index.js";

const $ = (id) => document.getElementById(id);

window.addEventListener("DOMContentLoaded", () => {
  const canvas = $("plot");
  if (!canvas) return;

  // create plot via helper
  const plot = CanvasPlot.create(canvas);
  window._plot = plot;

  const btn = $("btnPlot");
  const statusEl = $("status");
  const form = $("dataForm");

  if (btn && form) {
    btn.addEventListener("click", async () => {
      const name = form.querySelector('[name="dataset"]')?.value || "";
      const mjd = form.querySelector('[name="mjd"]')?.value || "";
      if (!name || !mjd) {
        if (statusEl) statusEl.textContent = "Nie wybrano dataset lub mjd.";
        return;
      }
      const url = `/timeseries/api/plot_mts/?name=${encodeURIComponent(name)}&mjd=${encodeURIComponent(mjd)}`;
      try {
        if (statusEl) statusEl.textContent = "Loading…";
        await plot.loadFromUrl(url);
        if (statusEl) statusEl.textContent = `Ploted: ${name} (MJD ${mjd})`;
      } catch (err) {
        if (statusEl) statusEl.textContent = "Error: " + (err?.message || String(err));
        console.error(err);
      }
    });
  }
});
