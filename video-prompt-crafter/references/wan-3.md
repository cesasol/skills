# Wan 3.0 Prompting Guide

Applies to: Alibaba **Wan 3.0** (preview since August 2026), API model IDs `wan3.0-video` (standard)
and `wan3.0-video-prime` (faster, same capabilities), on Alibaba Cloud Model Studio, Qwen Cloud,
Runware (`alibaba:wan@3.0`), DeepInfra, and others. **Closed weights:** no local or ComfyUI path;
local work goes to Wan 2.2. One model handles every task. It picks text-to-video, image-to-video,
reference, edit, or extend from the attached media types and the prompt's wording.

Users saying Wan 2.5, 2.6, or 2.7 get Wan 3.0: those versions are closed-weight predecessors with
the same reference, shot, and dialogue conventions, and Wan 3.0 supersedes them.

## Specs

| Parameter | Values |
| --------- | ------ |
| `duration` | 2-30 s, default 5; `-1` lets the model choose. With input video, input + output ≤ 30 s |
| `resolution` | `480P`, `720P`, `1080P` (default); 30 fps |
| `ratio` | `adaptive` (default, picks from media and prompt), `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16` |
| `audio` | `true` (default): dialogue with lip-sync, effects, ambience, music. `false` for silent |
| `prompt_extend` | `true` (default): an LLM rewrites the prompt. Required `true` with `file`/`link` input |
| `seed` | -1 (random) or 0-2147483647; not perfectly reproducible |
| Prompt length | up to 20,000 characters; Chinese and English |
| Negative prompt | **No field.** Write a `Negative prompt list:` line at the end of the prompt |

Inputs (`input.media[].type`):

- `first_frame` (1), or `first_frame` + `last_frame`: reproduced exactly as those frames. Cannot be
  combined with any reference, file, or link input.
- `reference_image` (up to 10), `reference_video` (up to 5, 15 s total), `reference_audio` (up to
  5, 15 s total): combine freely. Prompts cite them as `Image N`, `Video N`, `Audio N`.
- `file` (one document) or `link` (one public URL): the model reads it and makes a video from it.

Put `prompt_extend: false` on the Settings line for a finished prompt; the rewriter can reword your
reference labels and timestamps. Keep it `true` with a file or link input.

## Prompt Formula

Official complete formula. Skip sections you do not need:

```text
[Overall description]
+ [Reference citations: Image N / Video N / Audio N]
+ [Shot N (start-end seconds): subject + scene + motion + aesthetic control]
+ [Dialogue: xx says: "..."]
+ [Sound effects / background music]
+ [Style / mood]
+ [Negative prompt list]
```

- **Aesthetic control** is the part weak prompts skip: light source, light type, shot size, angle,
  lens, camera move. Without it you get a static camera in an undefined void.
- Write camera, lens, and angle per shot: `Close-up, 85mm telephoto, shallow depth of field, slow
  push-in`. For no movement: `Fixed shot, camera static`.
- One clear camera move per shot. Stacked moves fight each other.
- Keep each shot to a few key people and props; small details slip in crowded shots.

## Shots and Timing

- Wan 3.0 decides on its own whether to cut. Control it explicitly:
  - **Single take**: open with `One continuous shot.` For long takes, also add `No hard cuts, no
    jump cuts, no scene changes.`
  - **Multi-shot**: one-sentence overall description, then numbered shots with timestamps that run
    end to end with no gaps: `Shot 1 [0-3s]: ...` `Shot 2 [3-6s]: ...`.
- Use one timestamp format per prompt (`Shot 1 [0-3s]:`, `Shot 1 (00:00-00:03):`, or `[00:00-00:03]`).
- Keep shots 2-5 s each. Start a shot with `Hard cut,` or end it with `dissolve` for transitions.
- Put pacing in the overall description: `brisk buildup, sudden conflict, short climax, warm ending`.
- A 30 s take needs a beginning, a turn, and an end; length without a turn is a slow clip.

Official multi-shot example:

```wan-3
A vision of harmony between future technology and nature. Shot 1 [0-2s]: Wide shot of an aerial garden in a
futuristic city, floating plants swaying gently in the breeze. Shot 2 [2-4s]: A robot gardener carefully trims
plants with precise, graceful movements. Shot 3 [4-7s]: Sunlight streams through a transparent dome,
illuminating the entire garden and showcasing the perfect fusion of technology and nature. Shot 4 [7-10s]: The
camera pulls back to reveal the grand scale of the entire futuristic city, with the aerial garden as just one
part of it.
```

## Dialogue and Sound

- Dialogue: speaker + verb + colon + quoted line, one speaker per sentence: `The old man says:
  "..."`, `Image 2 replies: "..."`. Quoted lines are spoken exactly.
- Delivery: `in a relaxed tone, at a moderate speed, with a clear voice, in American English`.
- `Voiceover: "..."` for off-screen narration. `Lip sync` for a visible speaker.
- Voice cloning: `Voice timbre references Audio 1` once per character.
- The model invents lines unless told: write `No dialogue` when there is no speech.
- Effects: standalone sentences tied to visible actions, optionally timed: `From the 6th second,
  thunder rolls in the distance.` Ambience follows from described weather and materials.
- Music: say nothing and the model picks; describe it (`a soft cello enters under the last shot`);
  or turn it off (`No background music.`).

## References

- Cite every input by number, or features bleed between subjects. Numbers follow the upload order
  of each type, counted separately: `Image 1` and `Video 1` can coexist. With one input of a type,
  `the reference image` also works. Use no `@` prefix (that is a third-party UI convention).
- Appearance: `The child in Image 1 stands in the entryway of the apartment in Image 2.`
- Role mapping: `Protagonist: Image 1. Antagonist: Image 2. Scene: Image 3.`
- Motion only: `Replace the man in Video 1 with the woman in Image 1, keeping the skateboarding
  action, trajectory, and scene unchanged. Video 1 is used only for motion; do not inherit its
  character appearance.`
- Style only: `Only reference the color tone and lighting of Image 2, not its characters.`
- Storyboard: `Use the storyboard only as shot guidance`, then restate each panel in order.

Official reference example:

```wan-3
Video 1 holds Image 3 and plays a soothing country folk song on the chair in Image 4, saying: 'The sunshine is
so nice today.' Image 1 holds Image 2, passes by Video 1, places Image 2 on the table next to Video 1, and
says: 'That sounds beautiful, can you sing it again?'
```

## Image-to-Video

The first frame sets subject, scene, and style. Write motion, plot, dialogue, and camera. Use
`ratio: adaptive` so the frame keeps its proportions. With a last frame, describe the transition
between the two. Write `Fixed shot` to stop automatic camera drift.

## Editing and Extension

- Edit: `reference_video` plus `Edit the video: change <X> in Video 1 to <Y>; keep the rest of the
  frame unchanged.` Change one thing per pass. Set `duration: -1`, `ratio: adaptive`.
- Official edit: `Edit the video: remove the woman's sunglasses in video 1, revealing natural eye
  makeup and gaze; the woman's movement and the rest of the frame stay unchanged.`
- Extend: `Extend Video 1 forward: ...` (continues from its last frame). Restate character traits,
  clothing, and setting to avoid continuity glitches.

## Negative Prompt List

End the prompt with one line listing only what to exclude, without repeating the positive prompt:

`Negative prompt list: No subtitles, no watermark, no face distortion, no extra fingers, no costume changes.`

Useful entries: no subtitles, no watermark, no background music, no dialogue, no voiceover, no
large camera movements, no frequent shot cuts, no slow motion, no face distortion, no extra
fingers, no twisted limbs, no costume changes, no scale drift, no game-CG look.

## Settings Line

`Settings: 10 s, 16:9, 1080P, prompt_extend: false`. Add `audio: false` for silent clips and
`ratio: adaptive` for image or video inputs.
