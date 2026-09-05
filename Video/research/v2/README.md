# Research films v2 — adult anime comedy

Status: **one completed 30-second anime film (cherry-blossom)**, five Claude-authored screenplays, and five exact paper end cards. The homepage's cherry-blossom section uses the new film; the other four sections still use their v1 footage. Captions are below the picture, including fullscreen.

The owner rejected the cute material-character films and explicitly assigned screenwriting to Claude. Actual Claude Code wrote `CLAUDE_SCREENPLAY.md` on 2026-09-06, then authored `CLAUDE_PRODUCTION_LOCK.md` after editorial feedback on scientific fidelity, reading time and the pilot's romantic misdirection. The production lock overrides conflicting details in the first draft, including the incorrect furnace scene, absolute oxidation/retention claims and overly long captions.

The five 30-second scripts feature original adult characters:

| Topic | Claude's premise |
|---|---|
| Paper + AI | A researcher forgets how to walk normally when the professor watches. |
| Biosensor | A treasured lucky pencil is commandeered for a graphene experiment. |
| Carbon memory review | A professor's resistance to approvals changes with coffee; a decaf mistake is remembered after lights-out. |
| Energy storage | The protected ink survives the night better than the exhausted researcher. |
| Cherry petals | A romantic gesture turns out to be petal sampling; later, his adoration is for the sensor trace. |

Pilot: **Under the cherry tree, with tweezers**. `cherry-pilot-first-frame.png` is an original anime still made with built-in Codex ImageGen from Claude's adult-character design and the romantic setup. It is not animated footage. `cherry-pilot-video-prompt.txt` contains Claude's locked eight-second action with an image-reference and sound brief added for Gemini. The exact still prompt is saved separately for reproducibility. No existing franchise characters or artist names are used.

The first frame is for image-to-video generation, not a replacement poster for the old film. The film's joke requires the subsequent tweezers reveal and the woman's reaction. Do not present a still, a pan over it, or a loop of it as a completed new film.

All dialogue/science captions belong in the dedicated panel below the image. The science caption gets five seconds (23–28), with no competing dialogue. The memory film must still identify its source as a **review** on the paper card. Exact device performance numbers and procedures remain in the linked papers rather than the joke.

Gemini's signed-in interface resumed generation after **2026-09-06 08:36 KST**. The first-frame image and an adaptation of Claude's locked pilot prompt were submitted through its landscape video mode. The authenticated conversation could not play or export its returned resource, but Gemini's **public video-sharing page** exposed a working video. That supported page asset export succeeded; no credentials were copied or authentication checks bypassed.

- [Generation conversation](https://gemini.google.com/app/378350ef6690e5d3)
- [Shared pilot video](https://share.gemini.google/OX0Xkk8bQ2S1)
- Local original: `cherry-pilot.mp4` — 10.0078 seconds, 1280×720, 24fps H.264, stereo AAC. Gemini returned ten seconds despite the eight-second prompt.
- Verified: moving adult characters, tweezers reveal, specimen bag, woman's disappointed reaction; no in-picture captions. This is actual generated footage, not a pan over a still.
- [Shared continuation](https://share.gemini.google/2AxKAsg6Vahv): `cherry-lab.mp4`, 20.01 seconds. Gemini included the prior ten-second opening followed by a new ten-second lab scene. The edit uses only the new segment, so the opening never repeats. The production adaptation makes the scientist physically embrace the scope to clarify Claude's joke about loving the trace instead of the date.

No new subscription or paid credits were purchased.

Final export: `cherry-blossom-30s.mp4`, exactly 30 seconds, 1280×720, constant 24fps H.264/AAC; corresponding JPEG poster and KO/EN WebVTT tracks. `scripts/assemble-cherry-anime.cjs` assembles 23 seconds of unique scene action, gently retimed, a five-second final-reaction hold for the science caption, and a two-second paper end card. It preserves Gemini's native mark and does not burn captions into the picture. All five exact paper end cards were exported using `scripts/render-anime-endcards.cjs`.

Checks: complete FFmpeg decode without warnings; all five homepage players, duration, Korean/English captions, seeking, separate caption bounds, fullscreen, 390px mobile layout and normal/reduced-motion hero animation. The science caption was visually inspected on the new anime frame.

**Still outstanding:** animated scenes, edits and replacement of the other four films. After the two new generations, Gemini explicitly reported no more video generation until **2026-09-06 13:36 KST**. The website does not imply those four replacements are complete. The owner watched the opening and said it was funny; the adult anime treatment is the accepted direction.
