/* Make mermaid diagrams clickable — opens full-size SVG in new tab */
document.addEventListener("click", function (e) {
  /* Walk up from click target to find an SVG inside a mermaid container */
  var el = e.target;
  var svg = null;
  while (el && el !== document.body) {
    if (el.tagName === "svg" || el.tagName === "SVG") {
      svg = el;
    }
    if (
      el.classList &&
      (el.classList.contains("mermaid") || el.hasAttribute("data-processed"))
    ) {
      /* Found a mermaid container — use the SVG we found */
      if (svg) {
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
        return;
      }
    }
    el = el.parentElement;
  }
});

/* Add pointer cursor to rendered mermaid diagrams */
(function () {
  function addCursor() {
    var containers = document.querySelectorAll(
      "pre.mermaid, .mermaid[data-processed], [data-processed]"
    );
    containers.forEach(function (c) {
      if (c.querySelector("svg")) {
        c.style.cursor = "pointer";
      }
    });
    return containers.length > 0;
  }

  var attempts = 0;
  var timer = setInterval(function () {
    if (addCursor() || ++attempts > 50) clearInterval(timer);
  }, 200);

  new MutationObserver(function () {
    addCursor();
  }).observe(document.body || document.documentElement, {
    childList: true,
    subtree: true,
  });
})();
