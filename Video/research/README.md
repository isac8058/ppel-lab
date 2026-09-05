# PPEL+ · Material Mischief

Five original 30-second research comedies, made for the Research cards on the PPEL+ homepage. Each MP4 is 1920 × 1080, 24 fps, H.264/AAC, with a JPEG poster and English/Korean WebVTT captions.

| Film | Featured paper |
|---|---|
| The paper saw everything | [Mulberry-paper TENGs and AI healthcare, Cellulose (2025)](https://doi.org/10.1007/s10570-025-06542-7) |
| The pencil changed jobs | [Tree-like graphene and wireless 5hmC sensing, ACS Nano (2025)](https://doi.org/10.1021/acsnano.4c18646) |
| Electrons take a shortcut | [Carbon-based resistive-switching materials: a review, Carbon (2024)](https://doi.org/10.1016/j.carbon.2024.119320) |
| No oxygen on the guest list | [Oxidation-resistant MXene inks, Advanced Composites and Hybrid Materials (2026)](https://doi.org/10.1007/s42114-026-01862-z) |
| The cleaner found a beat | [Cherry-blossom TENG gesture recognition, Nano Energy (2026)](https://doi.org/10.1016/j.nanoen.2025.111687) |

The characters and jokes are fictional analogies. The scientific sequences are explanatory drawings, not experimental footage or measured traces. In particular, the paper-receipt gag is imaginary; the foot-health study uses machine learning on sensor signals. The memory film introduces a review, not a single device. Cherry-blossom sensing is illustrated with an assembled sensor and separate electronics. No diagnostic, unlimited-power, single-molecule, or bending-cycle claims are made.

## Production

All distributed artwork, motion, music, and sound effects were created specifically for these films using editable Canvas scenes and synthesized audio. No publisher figures, stock footage, commercial music, or other artists' characters are included.

Gemini was tested for two clay-style scenes. Its interface reported generation complete, but the browser encountered a Google authentication redirect loop when retrieving the media. Those clips are not included in these exports. The deliverables use the original 2D animation pipeline; no new paid plan or credits were purchased.

## Rebuild

Dependencies: Node.js, `@napi-rs/canvas`, FFmpeg, and the Arial fonts used by the Windows workstation. Set `NODE_PATH` to a directory containing the Canvas dependency and `FFMPEG_PATH` to FFmpeg (or use the default local `.video-work/tools` path).

```text
node scripts/render-research-films.cjs --native
node scripts/finish-research-media.cjs
```

Use a film ID after `--native` to render only that film. `--frames` exports representative frames for visual review. Source scripts and paper metadata are in `scripts/`; temporary renders and tools stay in the ignored `.video-work/` directory.

The homepage defers video sources until a visitor clicks play, pauses other films when one starts, synchronizes captions with the language switch, and provides a direct MP4 link if playback fails.

Captions now render in a dedicated dark panel **below** the image. WebVTT tracks run in hidden mode, so their cues remain timed without covering the film. The panel's fullscreen button expands the video and caption panel together. The original MP4 files remain unchanged; an adult-character comedy rewrite is being produced separately.

To check the player, serve the repository with HTTP byte-range support and run `node tests/research-captions.cjs` with Playwright installed. `TEST_URL` selects the server and `CHROME_PATH` optionally selects a local Chromium executable. This checks all five films, Korean/English cue changes, seeking, caption placement, fullscreen, mobile layout, and normal/reduced-motion hero behavior.

## Verification

- All five exports decoded without errors: 720 frames each, exactly 30 seconds, 1080p/24 fps. Combined MP4 size is approximately 6.5 MB; posters are approximately 29–42 KB each.
- Browser checks covered keyboard playback, 390-pixel mobile layout, language switching, seven parsed cues per language, exclusive playback, and a deliberately missing source that displayed the fallback link.
- The existing hero code was preserved. Its self-heal path was exercised with a simulated reduced-motion media result and a deliberately frozen CSS animation; JavaScript motion recovered and film playback remained available.
- Claude reviewed the player and scientific wording. Source-error handling and per-player caption initialization were improved. Subscript glyph rendering was corrected, and the cherry-sensor schematic explicitly distinguishes one and two signal peaks.
- The pencil-graphite precursor was rechecked against the [ACS publisher abstract](https://pubs.acs.org/doi/10.1021/acsnano.4c18646). The traffic joke intentionally illustrates resistance generally, without attributing a single switching mechanism to every material in the review.
