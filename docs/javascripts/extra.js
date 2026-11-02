// Clicking a heading's "#" permalink copies the full section URL to the
// clipboard (and still jumps to the section), then shows a short toast.
(function () {
  "use strict";

  function toast(message) {
    var el = document.querySelector(".px-toast");
    if (!el) {
      el = document.createElement("div");
      el.className = "px-toast";
      el.setAttribute("role", "status");
      el.setAttribute("aria-live", "polite");
      document.body.appendChild(el);
    }
    el.textContent = message;
    el.classList.add("is-visible");
    clearTimeout(el._timer);
    el._timer = setTimeout(function () { el.classList.remove("is-visible"); }, 1800);
  }

  document.addEventListener("click", function (event) {
    var link = event.target.closest && event.target.closest("a.headerlink");
    if (!link || !navigator.clipboard) return;
    var url = new URL(link.getAttribute("href"), window.location.href).href;
    navigator.clipboard.writeText(url).then(
      function () { toast("Link to section copied"); },
      function () { /* clipboard blocked: the link still navigates */ }
    );
  });

  // Wide tables scroll sideways on small screens; make each scroll area
  // reachable by keyboard (WCAG 2.1.1) and give it a name.
  function focusableTables() {
    document.querySelectorAll(".md-typeset__scrollwrap").forEach(function (wrap) {
      if (wrap.hasAttribute("tabindex")) return;
      wrap.setAttribute("tabindex", "0");
      wrap.setAttribute("role", "region");
      wrap.setAttribute("aria-label", "Table (scrolls sideways)");
    });
  }
  if (window.document$) window.document$.subscribe(focusableTables);
  else document.addEventListener("DOMContentLoaded", focusableTables);
})();
