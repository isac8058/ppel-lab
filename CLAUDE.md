# CLAUDE.md — PPEL Lab Website

Single-page lab website (`index.html`, all CSS/JS inline) served by GitHub Pages at
https://isac8058.github.io/ppel-lab/. Merges to `main` auto-deploy in ~1 minute.

## Critical: the owner's device reports reduced motion

The site owner's Windows/Chrome reports `prefers-reduced-motion: reduce` (OS "show
animations" is off, likely unknowingly). Any animation gated only on that media query
or on the JS `REDUCED` flag will look **completely frozen** on their machine, and they
will report the effect as "not working". This caused a long debugging saga (PRs #29–#37).

Rules that must survive future edits:

- The hero keeps a **self-heal detector** (end of the hero script): ~1s after load it
  samples the `.hero-sway` computed transform twice; if it hasn't advanced, it switches
  the sway to an interval-driven JS transform AND flips the mutable `ANIM` flag on,
  which revives the ink-canvas loop. Do not remove it, and do not re-gate hero motion
  purely on `REDUCED`/`prefers-reduced-motion`.
- Canvas/ink animation advances are gated on the mutable `let ANIM`, not the const
  `REDUCED`. Keep it that way.
- The ambient sway itself is a **compositor CSS animation** (`@keyframes heroSway` on
  `.hero-sway`), not rAF-driven — rAF gets throttled by battery/efficiency modes.
  JS applies only the pointer tilt (on `#heroTilt`) on top.

## Hero 3D architecture (index.html)

- `.hero--cover` carries `perspective`; `.hero-tilt` > `.hero-sway` are `preserve-3d`.
- Layer depths: `.hero-cover-bg` at `translateZ(-60px) scale(1.0545)` (scale exactly
  cancels the perspective shrink so it is pixel-true at rest — keep the pair in sync),
  ink canvas at z=0, `.hero-gloss` light sheet at `translateZ(70px)`.
- Rotation alone reads poorly on the soft watercolor artwork; the `translate3d` drift
  in the keyframes is what makes the motion legible. Coverage scale 1.12 (keyframes)
  × 1.08 (JS pointer tilt) keeps edges hidden at max tilt.
- Ink overlay tuning was softened in #32, then partially restored in #37 — don't crank
  it back to #30 levels or down to #32 levels without asking the owner.

## Conventions

- **Footer build stamp**: `vYYYY.MM.DD-N` next to the copyright. Bump it on every
  deploy that touches the page — it is how the owner distinguishes a cached copy from
  the live version (GitHub Pages caches HTML ~10 min; the owner often gets stale HTML).
- **Squash merges**: PRs are squash-merged, so before any follow-up work, restart the
  working branch from `origin/main` (`git checkout -B <branch> origin/main`) and
  cherry-pick/re-apply; otherwise the next PR hits merge conflicts.
- Verify changes in headless Chromium (`playwright-core` with
  `executablePath: '/opt/pw-browsers/chromium'`), testing **both** a normal context and
  `reducedMotion: 'reduce'` — the latter emulates the owner's machine. Useful checks:
  computed-transform sampling over time, canvas `toDataURL()` deltas, pixel-diff between
  timed screenshots.
- The owner communicates in Korean; reply in Korean.

## game.html (Ink Runner arcade)

- Standalone single-file canvas game linked from the footer `Navigate` column
  (`/ppel-lab/game.html`). It shares nothing with `index.html` except the colour tokens
  and the logo-mark SVG; editing it does not require the index build-stamp bump unless
  `index.html` itself changes.
- Its animation is a plain rAF loop that is **never gated on `prefers-reduced-motion`**
  (the owner's machine reports reduced motion, see above) — keep it that way.
- UI strings live in the `STR` table (ko/en); `localStorage` keys are prefixed
  `ppel-ink-runner:` (best score, language, mute).
- Smoke test: `node tests/game-smoke.mjs` (headless Chromium via Playwright; an in-page
  autopilot plays through the `window.__ink` debug hook, checks normal + reduced-motion
  contexts, touch, keyboard, mouse, pause, game over, and writes screenshots to
  `$OUT_DIR`).
