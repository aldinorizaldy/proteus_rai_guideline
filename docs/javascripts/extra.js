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
})();
