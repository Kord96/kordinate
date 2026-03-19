/* Open mermaid diagrams in a new tab for zoomed viewing */
(function () {
  function addZoomButtons() {
    document.querySelectorAll("pre.mermaid, div.mermaid").forEach(function (el) {
      var svg = el.querySelector("svg") || (el.tagName === "svg" ? el : null);
      if (!svg) return;

      /* Wrap in a positioned div if not already wrapped */
      var wrapper = el.closest(".mermaid-wrapper");
      if (!wrapper) {
        wrapper = document.createElement("div");
        wrapper.className = "mermaid-wrapper";
        el.parentNode.insertBefore(wrapper, el);
        wrapper.appendChild(el);
      }

      if (wrapper.querySelector(".mermaid-zoom")) return;

      var btn = document.createElement("button");
      btn.className = "mermaid-zoom";
      btn.title = "Open in new tab";
      btn.textContent = "\u26F6"; /* ⛶ maximize symbol */
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();

        var clone = svg.cloneNode(true);
        clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");

        /* Dark background for standalone viewing */
        var style = document.createElementNS("http://www.w3.org/2000/svg", "style");
        style.textContent = "svg { background: #1e1e2e; padding: 2rem; }";
        clone.insertBefore(style, clone.firstChild);

        var data = new XMLSerializer().serializeToString(clone);
        var blob = new Blob([data], { type: "image/svg+xml;charset=utf-8" });
        window.open(URL.createObjectURL(blob), "_blank");
      });

      wrapper.appendChild(btn);
    });
  }

  /* Mermaid renders async — observe for SVG insertion */
  var observer = new MutationObserver(function () {
    addZoomButtons();
  });

  /* Material for MkDocs uses instant loading — re-run on navigation */
  if (typeof document$ !== "undefined") {
    document$.subscribe(function () {
      addZoomButtons();
      observer.observe(document.body, { childList: true, subtree: true });
    });
  } else {
    document.addEventListener("DOMContentLoaded", function () {
      observer.observe(document.body, { childList: true, subtree: true });
      addZoomButtons();
    });
  }
})();
