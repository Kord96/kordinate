/* Initialize mermaid manually and make diagrams clickable */
(function () {
  function initMermaid() {
    /* Find unprocessed mermaid elements */
    var elements = document.querySelectorAll("pre.mermaid code");
    if (elements.length === 0) return false;

    elements.forEach(function (code) {
      var pre = code.parentElement;
      /* Create a div with the diagram text for mermaid to process */
      var div = document.createElement("div");
      div.className = "mermaid";
      div.textContent = code.textContent;
      pre.parentElement.insertBefore(div, pre);
      pre.remove();
    });

    /* Initialize mermaid if loaded */
    if (typeof mermaid !== "undefined") {
      mermaid.initialize({ startOnLoad: false, theme: "dark" });
      mermaid.run();
    } else {
      /* Load mermaid ourselves */
      var script = document.createElement("script");
      script.src = "https://unpkg.com/mermaid@11/dist/mermaid.min.js";
      script.onload = function () {
        mermaid.initialize({ startOnLoad: false, theme: "dark" });
        mermaid.run();
      };
      document.head.appendChild(script);
    }
    return true;
  }

  function makeClickable() {
    document.querySelectorAll(".mermaid svg, [data-processed] svg").forEach(
      function (svg) {
        if (svg.dataset.clickReady) return;
        svg.dataset.clickReady = "true";
        svg.style.cursor = "pointer";
        svg.addEventListener("click", function () {
          var clone = svg.cloneNode(true);
          clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
          delete clone.dataset.clickReady;
          clone.style.cursor = "";
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
      }
    );
  }

  /* Wait for DOM, then init mermaid + click handling */
  var attempts = 0;
  var mermaidInited = false;
  var timer = setInterval(function () {
    if (!mermaidInited) mermaidInited = initMermaid();
    makeClickable();
    if (++attempts > 100) clearInterval(timer);
  }, 200);

  /* Re-run on Material instant navigation */
  new MutationObserver(function () {
    attempts = 0;
    initMermaid();
    makeClickable();
  }).observe(document.body || document.documentElement, {
    childList: true,
    subtree: true,
  });
})();
