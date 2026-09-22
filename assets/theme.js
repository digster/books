/* ============================================================================
   The Understudy — assets/theme.js
   ----------------------------------------------------------------------------
   The site's only script: the light/dark switch in the header. It is
   strictly additive, as §2.4 of the brief requires. With JavaScript off,
   every page is complete, follows the OS setting through the stylesheet's
   prefers-color-scheme query, and the switch stays hidden.

   HOW IT FITS TOGETHER

     1. Every page loads this as a classic, synchronous <script> in <head>,
        straight after the stylesheet. It has to run before the body is
        parsed, so that the first frame is already in the right theme:
        `defer` or `async` would paint one frame in the OS theme and then
        flash. It also must NOT be a module, because Chrome refuses module
        scripts from file://, and the brief requires file:// to work.

     2. It sets data-theme="light"|"dark" on <html> to the EFFECTIVE theme:
        the reader's saved choice, else the OS setting. The stylesheet keys
        everything to that attribute, including showing the switch and
        drawing its on/off state, so both are right in the first frame
        without waiting for the DOM.

     3. On DOMContentLoaded it wires up every .theme-toggle in the page.

   WHAT IS REMEMBERED

   Only a DEVIATION from the OS. Flipping the switch away from the OS setting
   saves the choice. Flipping it back to match the OS forgets the choice, and
   the page follows the OS again, including an automatic switch at sunset. So
   a two-state switch still has a way back to "automatic" without a third
   state to explain.

   Storage can be missing or can throw: file:// in some browsers, private
   windows, blocked site data. Every access is guarded, and the fallback is
   that a choice lasts only for the current page.

   Never fetch(). It breaks file://, and the brief forbids it outright.
   tools/check.py fails if any script under assets/ reaches for the network.
   ========================================================================= */

(() => {
  "use strict";

  const KEY = "understudy-theme";
  const root = document.documentElement;
  const osDark = window.matchMedia("(prefers-color-scheme: dark)");

  /** The OS setting, as a theme name. */
  const system = () => (osDark.matches ? "dark" : "light");

  /** The reader's saved choice, or null. Anything unrecognised is ignored. */
  const saved = () => {
    try {
      const value = localStorage.getItem(KEY);
      return value === "light" || value === "dark" ? value : null;
    } catch {
      return null;
    }
  };

  /** Save a choice, or forget it when `theme` is null. */
  const save = (theme) => {
    try {
      if (theme) localStorage.setItem(KEY, theme);
      else localStorage.removeItem(KEY);
    } catch {
      /* Storage unavailable: the choice lasts for this page only. */
    }
  };

  /** The theme the page should show right now. */
  const effective = () => saved() ?? system();

  /** The attribute drives every visual; aria-checked tells assistive tech. */
  const apply = (theme) => {
    root.dataset.theme = theme;
    for (const toggle of document.querySelectorAll(".theme-toggle")) {
      toggle.setAttribute("aria-checked", String(theme === "dark"));
    }
  };

  const flip = () => {
    const next = root.dataset.theme === "dark" ? "light" : "dark";
    // Matching the OS again means "follow the OS", so forget the choice.
    save(next === system() ? null : next);
    apply(next);
  };

  // Before first paint. This line is the reason the script sits in <head>.
  apply(effective());

  const wire = () => {
    for (const toggle of document.querySelectorAll(".theme-toggle")) {
      toggle.hidden = false;
      toggle.addEventListener("click", flip);
    }
    apply(root.dataset.theme); // the toggles exist now: sync aria-checked
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", wire, { once: true });
  } else {
    wire();
  }

  // The OS flipped (a settings change, a sunset schedule): follow it, unless
  // the reader has made a choice of their own.
  osDark.addEventListener("change", () => {
    if (!saved()) apply(system());
  });

  // The switch was flipped in another tab. Follow it, so that two open parts
  // of the same book never disagree. `key` is null when storage was cleared.
  window.addEventListener("storage", (event) => {
    if (event.key === KEY || event.key === null) apply(effective());
  });

  // The back/forward cache restores a frozen page with the theme it had when
  // the reader left it, which may be older than a switch flipped since.
  window.addEventListener("pageshow", (event) => {
    if (event.persisted) apply(effective());
  });
})();
