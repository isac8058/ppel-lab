# PPEL+ · Material Mischief

Five 30-second research films for the PPEL+ homepage. **The cherry-blossom card now uses the action comedy short in [v3](v3/README.md)** (720p/24fps); the other four still use the original 1080p/24fps films. A Blender remake of the cherry film is at the concept stage in [v4](v4/README.md) (storyboard, shot list and a proof-of-concept render; no footage yet). All have JPEG posters and English/Korean WebVTT captions. Original v1 files remain here for provenance; the renderer below is the legacy 2D pipeline and does not rebuild the new anime footage.

| Film | Featured paper |
|---|---|
| The paper saw everything | [Mulberry-paper TENGs and AI healthcare, Cellulose (2025)](https://doi.org/10.1007/s10570-025-06542-7) |
| The pencil changed jobs | [Tree-like graphene and wireless 5hmC sensing, ACS Nano (2025)](https://doi.org/10.1021/acsnano.4c18646) |
| Electrons take a shortcut | [Carbon-based resistive-switching materials: a review, Carbon (2024)](https://doi.org/10.1016/j.carbon.2024.119320) |
| No oxygen on the guest list | [Oxidation-resistant MXene inks, Advanced Composites and Hybrid Materials (2026)](https://doi.org/10.1007/s42114-026-01862-z) |
| Under the cherry tree, with tweezers (v2 anime) | [Cherry-blossom TENG gesture recognition, Nano Energy (2026)](https://doi.org/10.1016/j.nanoen.2025.111687) |

The characters and jokes are fictional analogies. The scientific sequences are explanatory drawings, not experimental footage or measured traces. In particular, the paper-receipt gag is imaginary; the foot-health study uses machine learning on sensor signals. The memory film introduces a review, not a single device. Cherry-blossom sensing is illustrated with an assembled sensor and separate electronics. No diagnostic, unlimited-power, single-molecule, or bending-cycle claims are made.

## Production

The original v1 films used editable Canvas scenes and synthesized audio. The new cherry-blossom film uses a Claude-authored script, an original ImageGen character reference and Gemini-generated moving footage/audio; see its [production record](v2/README.md). No publisher figures or existing franchise characters are included.

The early clay-style Gemini trials are not included. The later anime footage was successfully retrieved through Gemini's public video-sharing page. No new paid plan or credits were purchased.

## Rebuild

Dependencies: Node.js, `@napi-rs/canvas`, FFmpeg, and the Arial fonts used by the Windows workstation. Set `NODE_PATH` to a directory containing the Canvas dependency and `FFMPEG_PATH` to FFmpeg (or use the default local `.video-work/tools` path).

```text
node scripts/render-research-films.cjs --native
node scripts/finish-research-media.cjs
```

Use a film ID after `--native` to render only that film. `--frames` exports representative frames for visual review. Source scripts and paper metadata are in `scripts/`; temporary renders and tools stay in the ignored `.video-work/` directory.

The homepage defers video sources until a visitor clicks play, pauses other films when one starts, synchronizes captions with the language switch, and provides a direct MP4 link if playback fails.

Captions render in a dedicated dark panel **below** the image. WebVTT tracks run in hidden mode, so their cues remain timed without covering the film. The panel's fullscreen button expands the video and caption panel together. Claude has written all five adult-character replacements; one is complete and four await new footage.

To check the player, serve the repository with HTTP byte-range support and run `node tests/research-captions.cjs` with Playwright installed. `TEST_URL` selects the server and `CHROME_PATH` optionally selects a local Chromium executable. This checks all five films, Korean/English cue changes, seeking, caption placement, fullscreen, mobile layout, and normal/reduced-motion hero behavior.

## Verification

- All five exports decoded without errors: 720 frames each, exactly 30 seconds, 1080p/24 fps. Combined MP4 size is approximately 6.5 MB; posters are approximately 29–42 KB each.
- Browser checks covered keyboard playback, 390-pixel mobile layout, language switching, seven parsed cues per language, exclusive playback, and a deliberately missing source that displayed the fallback link.
- The existing hero code was preserved. Its self-heal path was exercised with a simulated reduced-motion media result and a deliberately frozen CSS animation; JavaScript motion recovered and film playback remained available.
- Claude reviewed the player and scientific wording. Source-error handling and per-player caption initialization were improved. Subscript glyph rendering was corrected, and the cherry-sensor schematic explicitly distinguishes one and two signal peaks.
- The pencil-graphite precursor was rechecked against the [ACS publisher abstract](https://pubs.acs.org/doi/10.1021/acsnano.4c18646). The traffic joke intentionally illustrates resistance generally, without attributing a single switching mechanism to every material in the review.
