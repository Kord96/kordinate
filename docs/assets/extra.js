/* Make mermaid diagrams clickable — opens full-size SVG in new tab */
(function () {
  function makeClickable() {
    var svgs = document.querySelectorAll("pre.mermaid svg, .mermaid svg, [data-mermaid-id] svg");
    var found = false;
    svgs.forEach(function (svg) {
      if (svg.dataset.zoomReady) return;
      svg.dataset.zoomReady = "true";
      svg.style.cursor = "pointer";
      svg.addEventListener("click", function () {
        var clone = svg.cloneNode(true);
        clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
        delete clone.dataset.zoomReady;
        clone.style.cursor = "";
        var style = document.createElementNS("http://www.w3.org/2000/svg", "style");
        style.textContent = "svg { background: #1e1e2e; padding: 2rem; }";
        clone.insertBefore(style, clone.firstChild);
        var data = new XMLSerializer().serializeToString(clone);
        var blob = new Blob([data], { type: "image/svg+xml;charset=utf-8" });
        window.open(URL.createObjectURL(blob), "_blank");
      });
      found = true;
    });
    return found;
  }

  /* Poll until mermaid has rendered */
  var attempts = 0;
  var timer = setInterval(function () {
    if (makeClickable() || ++attempts > 50) clearInterval(timer);
  }, 200);

  /* Re-run on Material instant navigation */
  new MutationObserver(function () {
    attempts = 0;
    makeClickable();
  }).observe(document.body || document.documentElement, {
    childList: true,
    subtree: true,
  });
})();
