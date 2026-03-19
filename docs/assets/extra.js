/* Open mermaid diagrams in a new tab for zoomed viewing */
(function () {
  function addZoomButtons() {
    var diagrams = document.querySelectorAll("pre.mermaid svg, .mermaid svg");
    diagrams.forEach(function (svg) {
      var container = svg.parentElement;
      if (!container || container.querySelector(".mermaid-zoom")) return;

      var btn = document.createElement("button");
      btn.className = "mermaid-zoom";
      btn.title = "Open in new tab";
      btn.textContent = "\u26F6";
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();

        var clone = svg.cloneNode(true);
        clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");

        var style = document.createElementNS("http://www.w3.org/2000/svg", "style");
        style.textContent = "svg { background: #1e1e2e; padding: 2rem; }";
        clone.insertBefore(style, clone.firstChild);

        var data = new XMLSerializer().serializeToString(clone);
        var blob = new Blob([data], { type: "image/svg+xml;charset=utf-8" });
        window.open(URL.createObjectURL(blob), "_blank");
      });

      container.style.position = "relative";
      container.appendChild(btn);
    });
    return diagrams.length > 0;
  }

  /* Poll until mermaid has rendered — covers all loading strategies */
  var attempts = 0;
  var timer = setInterval(function () {
    var found = addZoomButtons();
    attempts++;
    if (found || attempts > 50) clearInterval(timer);
  }, 200);

  /* Also re-run on Material instant navigation */
  var observer = new MutationObserver(function () {
    attempts = 0;
    addZoomButtons();
  });
  observer.observe(document.body || document.documentElement, {
    childList: true,
    subtree: true,
  });
})();
