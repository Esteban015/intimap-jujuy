// IntiMap Jujuy — landing: menú móvil accesible y navegación sólida al hacer scroll. Sin dependencias.
(function () {
  "use strict";
  var nav = document.getElementById("nav");
  var toggle = nav && nav.querySelector(".nav__toggle");
  var menu = document.getElementById("nav-menu");

  function setOpen(open) {
    toggle.setAttribute("aria-expanded", String(open));
    menu.classList.toggle("is-open", open);
    toggle.querySelector(".im-sr-only").textContent = open ? "Cerrar menú" : "Abrir menú";
  }

  if (toggle && menu) {
    toggle.addEventListener("click", function () { setOpen(toggle.getAttribute("aria-expanded") !== "true"); });
    menu.addEventListener("click", function (e) { if (e.target.closest("a")) setOpen(false); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") { setOpen(false); toggle.focus(); }
    });
  }

  function onScroll() { if (nav) nav.classList.toggle("is-solid", window.scrollY > 24); }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
})();
