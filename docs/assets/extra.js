/* Open mermaid diagrams in a new tab for zoomed viewing */
(function () {
  function addZoomButtons() {
    document.querySelectorAll(".mermaid svg").forEach(function (svg) {
      var container = svg.closest(".mermaid");
      if (!container || container.querySelector(".mermaid-zoom")) return;

      var btn = document.createElement("button");
      btn.className = "mermaid-zoom";
      btn.title = "Open in new tab";
      btn.textContent = "\u26F6"; /* ⛶ maximize symbol */
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();

        /* Clone SVG and set explicit dimensions + background for standalone viewing */
        var clone = svg.cloneNode(true);
        clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");

        /* Add a dark background style for standalone viewing */
        var style = document.createElementNS("http://www.w3.org/2000/svg", "style");
        style.textContent = "svg { background: #1e1e2e; padding: 2rem; }";
        clone.insertBefore(style, clone.firstChild);

        var data = new XMLSerializer().serializeToString(clone);
        var blob = new Blob([data], { type: "image/svg+xml;charset=utf-8" });
        window.open(URL.createObjectURL(blob), "_blank");
      });

      container.appendChild(btn);
    });
  }

  /* Mermaid renders async — observe for SVG insertion */
  var observer = new MutationObserver(function () {
    addZoomButtons();
  });

  document.addEventListener("DOMContentLoaded", function () {
    observer.observe(document.body, { childList: true, subtree: true });
    /* Also run once in case mermaid already rendered */
    addZoomButtons();
  });
})();
