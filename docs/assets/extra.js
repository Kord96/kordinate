/* Click any mermaid diagram to open full-size SVG in new tab.
   Does NOT initialize mermaid — Material for MkDocs handles that. */
(function () {
  function makeClickable() {
    document.querySelectorAll(".mermaid").forEach(function (container) {
      var svg = container.querySelector("svg");
      if (!svg || container.dataset.clickReady) return;
      container.dataset.clickReady = "true";
      container.style.cursor = "pointer";
      container.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        var clone = svg.cloneNode(true);
        clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
        var style = document.createElementNS(
          "http://www.w3.org/2000/svg",
          "style"
        );
        style.textContent = "svg { background: #1e1e2e; padding: 2rem; }";
        clone.insertBefore(style, clone.firstChild);
        var data = new XMLSerializer().serializeToString(clone);
        var blob = new Blob([data], { type: "image/svg+xml;charset=utf-8" });
        window.open(URL.createObjectURL(blob), "_blank");
      });
    });
  }

  var timer = setInterval(function () { makeClickable(); }, 500);
  setTimeout(function () { clearInterval(timer); }, 30000);
})();
