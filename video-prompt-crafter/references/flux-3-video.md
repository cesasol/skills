# FLUX 3 Video Prompting Guide

Applies to: Black Forest Labs **FLUX 3 Video**, the video capability of the multimodal FLUX 3 model,
on the BFL API (`POST /v1/flux-3-video`), BFL Playground, Runware (`bfl:flux@3-video`), and fal
(`blackforestlabs/flux-3/*`). Editing uses the separate **FLUX Video Edit** tool. **Closed weights:**
no local or ComfyUI video path. FLUX 3 Image is covered by image-prompt-crafter.

## Specs

| Parameter | Values |
| --------- | ------ |
| `mode` | `t2v`, `i2v` (keyframes), `v2v` (continue a video), `draft_enhance` |
| `duration` | 5-20 s integer, or `auto` (default; fits the brief). `v2v` adds at most 15 s |
| `aspect_ratio` | `auto` (default), `21:9`, `2:1`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16`, `9:21` |
| `resolution` | `hd` (default, 1280×704 at 16:9), `fhd`, `qhd`, `uhd`; above `hd` is the same shot upscaled |
| `generate_audio` | `true` (default): dialogue with lip-sync, voiceover, ambience, effects, music |
| `draft` | `true`: fast `hd` preview at about 1/3 cost; `draft_enhance` re-renders the same shot |
| Output | 24 fps |
| Negative prompt, seed | **No fields.** Negatives go in the prompt as short "No X" clauses |

- The prompt is always interpreted and expanded before generation (no toggle). It fills gaps; it
  does not override what you specify. Write the full prompt anyway.
- Dialogue languages: English and dialects, Chinese, Spanish, French, German, Japanese, Portuguese,
  Russian, Italian, Indonesian, Turkish, Hindi, Punjabi, and more.
- Reference images for identity ("Omni Reference") are not yet available. Describe a recurring
  subject in a fixed text block and repeat it word for word; use keyframes when a frame must match.

## Prompt Formats

Direct a scene, not a collection of objects. Use concrete nouns and verbs the camera can see. Long
prompts give control, but over-stuffing makes motion less coherent; past a few hundred words, later
clauses get dropped. Pick one of four official formats:

1. **Natural language (default)**: `[camera] shot of [subject] [action] in [environment].
   [supporting visual, motion, and sound details]`. Put the medium first when it must not read as
   live action ("1990s hand-drawn cel animation of...").
2. **Labeled fields**, to tune one lever at a time: `Camera shot:`, `Subject + action:`,
   `Depth of field:`, `Lighting + palette:`, `Motion:`, `Style:`, `Audio:`.
3. **Timesteps**, for action that must land on a mark. Two or three beats per 5 s; mark a hard cut
   where the angle changes:
   `0.0–1.5s — locked wide of a still harbor at dawn, boats motionless on glassy water`
   `1.5–3.0s — a slow push-in begins as gulls lift off the water`
   `3.0–5.0s — the sun breaks the horizon, warm light spreads and the camera settles`
4. **Prompt schema**, for multi-shot stories: `Core summary:` (one line: who, where, arc) →
   `Scene:` → `Subject description:` (held identical across shots) → `Dynamic narrative:` with
   `Shot 1 [0.0s-2.5s]: ...` (camera language goes here) → `Audio:` → `Style and color:`.

Official examples:

```flux-3-video
A red fox stalks across a wide snowfield at dawn, low winter light, a dark treeline fading into mist behind
it. It slows, crouches, then leaps high and pounces into the fresh snow. Telephoto lens, shallow depth of
field, locked-off camera panning gently to follow. Muffled paw steps and a soft breeze.
```

```flux-3-video
Medium close-up of a tired station attendant behind the glass. She looks toward the stranded passenger and
says, "The 6:10 is delayed again. They say ten minutes." Low, matter-of-fact delivery. Fluorescent room tone
and rain against the platform roof. No on-screen text or subtitles.
```

## Camera and Motion

- One framing term, one movement term, one clear subject action per shot. Without camera
  direction the model drifts slightly or animates the subject to compensate; write "camera holds
  locked at eye level" for a still frame.
- Count beats and name the physics: "Three keys strike, one after another. A pause. Then the
  carriage returns with a sharp bell ding." For several moving things, give the order.
- Single-shot order that works: opening frame → visible cause → physical response → one final
  state usable as an edit point → continuity ("same set, no cuts, no frozen or repeated frames") →
  sound.
- Budget about 5-7 s per beat or shot: 2 shots in 8-12 s, 3 shots in 12-18 s, 4 near 20 s.

## Multi-Shot

```flux-3-video
SHOT ONE: wide aerial of a desert highway at dawn, a single red car speeding through. HARD CUT. SHOT TWO:
interior close-up, the driver's hands drumming the wheel. HARD CUT. SHOT THREE: from the roadside, the car
shrinks into the heat haze. One music bed across all three shots.
```

- Write `SHOT ONE:`, `SHOT TWO:` and `HARD CUT.` in capitals with a period; a plain "cut" is ambiguous.
- Contrast consecutive shots strongly, by scale first (macro → wide → aerial), then angle,
  location, or time of day. Similar angles blur into one drifting take.
- Keep to 2-3 shots per generation; generate more as separate clips.
- Name the music bed once for the whole clip; naming it per shot restarts it. Name ambience per shot.
- To prevent cuts: `One continuous unbroken shot, constant motion, no freezing.`

## Dialogue and Sound

Official audio template:

```text
[Shot and action].
Dialogue or voiceover: [speaker and exact words].
Ambience: [place].
Effects: [visible actions].
Music: [style and role].
```

- Put exact words in double quotes and attach them to a **visible speaker**, or write "voiceover"
  or "narration". End with `No on-screen text, no subtitles.`; otherwise the line can render as
  burned-in text.
- Say each line once: `speaks exactly once, the complete sentence, no repetition and no other
  words`. Otherwise lines repeat or pick up filler.
- Non-English: `speaks entirely in French, every word in French, native accent, no English words.`
- Several speakers: identify each by a visible trait, give turns in order, write "no overlap".
- Voice direction: age, accent, register, recording ("close and dry", "phone microphone"), and a
  guardrail ("no announcer delivery"). Keep lines short; spell unusual names phonetically.
- Leave room: a line that must finish needs time. Shorten it or ask it to "finish by 8 seconds".
- Name sound sources ("distant traffic, rain ticking on a metal awning"); tie each effect to its
  cause. Instead of "quiet room tone", which can collapse into static, name a soft source.
  Set `generate_audio: false` for true silence.
- Music can appear unrequested; write "No music" or "only diegetic sound" when the user wants none.

## On-Screen Text

Describe the words and their placement: `Bold kinetic title card, the word "FLUX" assembling from
light streaks on a dark stage`. Short physical text works best. Exact logos, long copy, and small
type are post-production work; say so in the description sentence when they matter.

## Image-to-Video, Keyframes, Continuation

`keyframes` are pixel-exact on screen: one image = start frame; two = start and end (end frame is
experimental); 3-10 = an evenly spaced storyboard; `[seconds, image]` pairs pin frames to times
(needs an integer duration). Use the Inputs line to give the order.

- **Prompt the motion, not the scene.** Re-describing the frame invites the model to reimagine it.
  Opening that works: `The video begins exactly on the provided image, holding still for a beat.`
- Start and end frames: describe the stages of change in order and keep the camera still.
- A mid-clip keyframe is a deadline: say what the remaining seconds are for.
- Continuation (`v2v`): write from the ending: `Continue this video from its final frames: ...`.
  Name what the last frames show, carry momentum and sound across the seam, and do not recap.

Official I2V example:

```flux-3-video
The black horse bursts into a full gallop, mane and tail whipping in the wind, hooves kicking up huge plumes
of dust as the sports car chases close behind with headlights flaring. The camera races alongside at ground
level, shaking with speed. Thundering hoofbeats, roaring engine, rushing wind.
```

## Editing (FLUX Video Edit)

An edit prompt describes a change, not a shot; everything unmentioned stays as filmed. Add
placement and appearance only where the change needs them. Chain passes (layout, then setting,
then lighting) instead of stacking them. Output keeps the source length and framing, at most 720p.
New dialogue must fit the length of the line it replaces.

## Settings Line

`Settings: 10 s, 16:9, fhd`. Add `generate_audio: false` for silent clips, `draft: true` for fast
explorations, `mode: i2v` or `mode: v2v` with inputs.
