#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright==1.56.0"]
# ///
"""Browser tests for the theme switch: assets/theme.js and its CSS.

tools/check.py proves the switch is wired into every page correctly. This
proves it *behaves*: the right theme in the first frame, the choice kept
across pages and forgotten when it matches the OS again, the OS followed
otherwise, print always light, and nothing lost with JavaScript off or
storage blocked.

Like the checker, this is NOT a build step and never runs at serve time. Its
one dependency is declared inline above, so uv fetches it into a throwaway
environment and nothing is added to the repository:

    uv run tools/test_theme.py
    uv run tools/test_theme.py -k print      # one test, by name

First time on a new machine, install the browser Playwright drives:

    uvx --from playwright==1.56.0 playwright install chromium
"""

from __future__ import annotations

import functools
import threading
import unittest
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import Browser, Page, sync_playwright

ROOT = Path(__file__).resolve().parent.parent
KEY = "understudy-theme"

# Computed colours of the tokens the tests look at.
LIGHT_PAPER = "rgb(250, 251, 254)"   # --paper, light   #fafbfe
DARK_PAPER = "rgb(20, 24, 32)"       # --paper, dark    #141820
DARK_ACCENT = "rgb(141, 183, 255)"   # --accent, dark   #8db7ff
PRINT_PAPER = "rgb(255, 255, 255)"   # print --paper    #fff
PRINT_INK = "rgb(17, 17, 17)"        # print --ink      #111

PART = "books/surfing-uncertainty/03-precision-and-attention.html"
PAGES = sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob("*.html")
               if ".git" not in p.parts)

# Records whether data-theme was already set when the parser had not yet
# reached <body>. MutationObserver callbacks run at the microtask checkpoint
# after each parser-blocking script, so the first one to see the attribute
# fires before <body> exists only if theme.js ran synchronously in <head>.
FIRST_FRAME_PROBE = """
window.__themeBeforeBody = null;
new MutationObserver(() => {
  const root = document.documentElement;
  if (window.__themeBeforeBody === null && root && root.hasAttribute("data-theme")) {
    window.__themeBeforeBody = document.body === null;
  }
}).observe(document, { childList: true, subtree: true,
                       attributes: true, attributeFilter: ["data-theme"] });
"""

# Records the switch's state the moment the parser inserts it, which is before
# DOMContentLoaded and so before theme.js has removed `hidden`. Only the CSS
# can be showing it at that point.
SWITCH_PROBE = """
window.__switchOnInsert = null;
new MutationObserver((_, observer) => {
  const toggle = document.querySelector(".theme-toggle");
  if (toggle) {
    window.__switchOnInsert = [toggle.hidden, getComputedStyle(toggle).display];
    observer.disconnect();
  }
}).observe(document, { childList: true, subtree: true });
"""

# Storage that throws on every access, as in some private windows and file://.
BLOCKED_STORAGE = """
Object.defineProperty(window, "localStorage", {
  get() { throw new DOMException("blocked", "SecurityError"); },
});
"""


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args) -> None:  # keep test output readable
        pass


class ThemeSwitch(unittest.TestCase):
    browser: Browser
    base: str

    @classmethod
    def setUpClass(cls) -> None:
        handler = functools.partial(QuietHandler, directory=str(ROOT))
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}/"
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.pw.stop()
        cls.server.shutdown()

    # --- helpers ----------------------------------------------------------

    def open(self, path: str = "index.html", *, scheme: str = "light",
             js: bool = True, init: str | None = None,
             width: int = 1280) -> Page:
        """A page in a fresh context, so storage never leaks between tests."""
        context = self.browser.new_context(
            color_scheme=scheme, java_script_enabled=js,
            viewport={"width": width, "height": 800})
        self.addCleanup(context.close)
        if init:
            context.add_init_script(init)
        page = context.new_page()
        errors: list[str] = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        self.addCleanup(lambda: self.assertEqual(errors, [], "page threw"))
        page.goto(self.base + path)
        return page

    @staticmethod
    def theme(page: Page) -> str | None:
        return page.evaluate("document.documentElement.dataset.theme ?? null")

    @staticmethod
    def paper(page: Page) -> str:
        return page.evaluate("getComputedStyle(document.body).backgroundColor")

    @staticmethod
    def saved(page: Page) -> str | None:
        return page.evaluate(f"localStorage.getItem('{KEY}')")

    @staticmethod
    def switch(page: Page):
        return page.get_by_role("switch", name="Dark theme")

    # --- without JavaScript -----------------------------------------------

    def test_without_js_the_os_decides_and_the_switch_is_absent(self) -> None:
        for scheme, paper in (("light", LIGHT_PAPER), ("dark", DARK_PAPER)):
            with self.subTest(scheme=scheme):
                page = self.open(PART, scheme=scheme, js=False)
                self.assertEqual(self.paper(page), paper)
                self.assertFalse(page.locator(".theme-toggle").is_visible())

    # --- first frame --------------------------------------------------------

    def test_theme_is_set_before_the_body_is_parsed(self) -> None:
        page = self.open(PART, init=FIRST_FRAME_PROBE)
        self.assertIs(page.evaluate("window.__themeBeforeBody"), True)

    def test_switch_is_shown_from_the_first_frame(self) -> None:
        # Still `hidden` (not yet wired), yet displayed: the CSS is doing it,
        # so the switch never pops in after load and shifts the header.
        page = self.open(PART, init=SWITCH_PROBE)
        hidden, display = page.evaluate("window.__switchOnInsert")
        self.assertTrue(hidden, "probe ran after wiring; it proves nothing")
        self.assertNotEqual(display, "none")   # "flex": a flex item is blockified

    def test_saved_choice_is_applied_before_the_body_is_parsed(self) -> None:
        page = self.open(init=FIRST_FRAME_PROBE)
        self.switch(page).click()                       # light OS -> dark
        page.goto(self.base + PART)
        self.assertIs(page.evaluate("window.__themeBeforeBody"), True)
        self.assertEqual(self.theme(page), "dark")

    # --- following the OS -------------------------------------------------

    def test_follows_the_os_when_nothing_is_saved(self) -> None:
        for scheme, paper in (("light", LIGHT_PAPER), ("dark", DARK_PAPER)):
            with self.subTest(scheme=scheme):
                page = self.open(scheme=scheme)
                self.assertEqual(self.theme(page), scheme)
                self.assertEqual(self.paper(page), paper)
                expect_on = "true" if scheme == "dark" else "false"
                self.assertEqual(self.switch(page).get_attribute("aria-checked"), expect_on)
                self.assertEqual(page.evaluate(
                    "document.querySelector('.theme-toggle').hidden"), False)

    def test_an_os_change_is_followed_when_nothing_is_saved(self) -> None:
        page = self.open()
        page.emulate_media(color_scheme="dark")
        page.wait_for_function("document.documentElement.dataset.theme === 'dark'")
        self.assertEqual(self.switch(page).get_attribute("aria-checked"), "true")

    def test_an_os_change_is_ignored_once_the_reader_has_chosen(self) -> None:
        page = self.open()
        self.switch(page).click()                       # choose dark on a light OS
        for scheme in ("dark", "light"):
            page.emulate_media(color_scheme=scheme)
            self.assertEqual(self.theme(page), "dark")
        self.assertEqual(self.saved(page), "dark")

    def test_an_unrecognised_saved_value_is_ignored(self) -> None:
        page = self.open(scheme="dark")
        page.evaluate(f"localStorage.setItem('{KEY}', 'sepia')")
        page.reload()
        self.assertEqual(self.theme(page), "dark")

    # --- the switch -------------------------------------------------------

    def test_choosing_dark_on_a_light_os_is_saved_and_kept(self) -> None:
        page = self.open()
        self.switch(page).click()
        self.assertEqual(self.theme(page), "dark")
        self.assertEqual(self.paper(page), DARK_PAPER)
        self.assertEqual(self.saved(page), "dark")
        self.assertEqual(self.switch(page).get_attribute("aria-checked"), "true")
        page.goto(self.base + PART)
        self.assertEqual(self.theme(page), "dark")
        self.assertEqual(self.paper(page), DARK_PAPER)

    def test_choosing_light_on_a_dark_os_beats_the_media_query(self) -> None:
        page = self.open(scheme="dark")
        self.switch(page).click()
        self.assertEqual(self.theme(page), "light")
        self.assertEqual(self.paper(page), LIGHT_PAPER)
        self.assertEqual(self.saved(page), "light")
        self.assertEqual(page.evaluate(
            "getComputedStyle(document.documentElement).colorScheme"), "light")

    def test_flipping_back_to_match_the_os_forgets_the_choice(self) -> None:
        page = self.open()
        self.switch(page).click()
        self.switch(page).click()
        self.assertEqual(self.theme(page), "light")
        self.assertIsNone(self.saved(page))
        # Forgotten means the OS is in charge again.
        page.emulate_media(color_scheme="dark")
        page.wait_for_function("document.documentElement.dataset.theme === 'dark'")

    def test_switch_is_drawn_from_the_theme(self) -> None:
        page = self.open(scheme="dark")
        track = page.evaluate(
            "getComputedStyle(document.querySelector('.theme-switch')).backgroundColor")
        self.assertEqual(track, DARK_ACCENT)

    def test_keyboard_reaches_and_operates_the_switch(self) -> None:
        page = self.open(PART)
        for _ in range(12):
            page.keyboard.press("Tab")
            if page.evaluate(
                    "document.activeElement.classList.contains('theme-toggle')"):
                break
        else:
            self.fail("Tab never reached the switch")
        outline = page.evaluate("getComputedStyle(document.activeElement).outlineStyle")
        self.assertEqual(outline, "solid", "focus ring not visible")
        page.keyboard.press("Space")
        self.assertEqual(self.theme(page), "dark")
        page.keyboard.press("Enter")
        self.assertEqual(self.theme(page), "light")

    def test_another_tab_follows_the_switch(self) -> None:
        page = self.open()
        other = page.context.new_page()
        other.goto(self.base + PART)
        self.switch(page).click()
        other.wait_for_function("document.documentElement.dataset.theme === 'dark'")
        self.assertEqual(self.switch(other).get_attribute("aria-checked"), "true")

    def test_blocked_storage_still_switches_for_this_page(self) -> None:
        page = self.open(scheme="dark", init=BLOCKED_STORAGE)
        self.assertEqual(self.theme(page), "dark")
        self.switch(page).click()
        self.assertEqual(self.theme(page), "light")
        self.assertEqual(self.paper(page), LIGHT_PAPER)

    # --- print ------------------------------------------------------------

    def test_print_is_light_whatever_the_screen_theme(self) -> None:
        for scheme, flip in (("dark", False), ("light", True)):
            with self.subTest(scheme=scheme, chosen=flip):
                page = self.open(PART, scheme=scheme)
                if flip:
                    self.switch(page).click()           # chosen dark on light OS
                self.assertEqual(self.theme(page), "dark")
                page.emulate_media(media="print")
                # The tokens, not body: print hard-codes body's colours, so
                # only the tokens show whether the dark blocks leaked in.
                tokens = page.evaluate("""() => {
                    const s = getComputedStyle(document.documentElement);
                    return ["--paper", "--ink", "--ink-soft", "--ink-faint"]
                        .map(t => s.getPropertyValue(t).trim());
                }""")
                self.assertEqual(tokens, ["#fff", "#111", "#333", "#555"])
                self.assertEqual(self.paper(page), PRINT_PAPER)
                self.assertEqual(page.evaluate(
                    "getComputedStyle(document.body).color"), PRINT_INK)
                self.assertFalse(page.locator(".theme-toggle").is_visible())

    # --- surfaces and layout ----------------------------------------------

    def test_file_urls_keep_the_choice_across_pages(self) -> None:
        context = self.browser.new_context(color_scheme="light")
        self.addCleanup(context.close)
        page = context.new_page()
        page.goto((ROOT / "index.html").as_uri())
        self.switch(page).click()
        page.goto((ROOT / PART).as_uri())
        self.assertEqual(self.theme(page), "dark")

    def test_switch_does_not_grow_the_header(self) -> None:
        for path in ("index.html", PART):
            with self.subTest(path=path):
                heights = [self.open(path, js=js).evaluate(
                    "document.querySelector('header.site').getBoundingClientRect().height")
                    for js in (False, True)]
                self.assertAlmostEqual(heights[0], heights[1], delta=0.5)

    def test_every_page_has_the_switch_and_stays_local(self) -> None:
        for path in PAGES:
            with self.subTest(path=path):
                context = self.browser.new_context(color_scheme="light")
                remote: list[str] = []
                page = context.new_page()
                page.on("request", lambda r: r.url.startswith(self.base)
                        or remote.append(r.url))
                page.goto(self.base + path)
                self.assertTrue(self.switch(page).is_visible())
                self.assertEqual(remote, [])
                context.close()

    def test_no_sideways_scroll_at_360px(self) -> None:
        for path in PAGES:
            with self.subTest(path=path):
                page = self.open(path, width=360)
                self.assertLessEqual(page.evaluate(
                    "document.documentElement.scrollWidth - "
                    "document.documentElement.clientWidth"), 0)
                box = self.switch(page).bounding_box()
                self.assertGreaterEqual(box["x"], 0)
                self.assertLessEqual(box["x"] + box["width"], 360)
                self.assertGreaterEqual(box["height"], 24, "target under 24px")


if __name__ == "__main__":
    unittest.main(verbosity=2)
