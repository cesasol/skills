# Gemini Omni Prompting Guide

Applies to: Google DeepMind **Gemini Omni** video generation and editing, currently **Gemini Omni
1.1 Flash**: `gemini-omni-1.1-flash` on the Gemini API (Interactions API),
`gemini-omni-1.1-flash-preview` on Vertex / Gemini Enterprise Agent Platform, fal
(`google/gemini-omni-flash`), and the Gemini app, Google Flow, and YouTube Shorts. It replaces Veo
3.1 in the Gemini app and Gemini API. "Veo 4" is not an official name; users who say it mean Omni.
**Closed weights.**

## Specs

| Item | Values |
| ---- | ------ |
| Length | 3-10 s. The Gemini API has no duration parameter: state the length in the prompt. Vertex `duration` `"3s"`-`"10s"`; fal 3-10, default 8 |
| Extension | +10 s per turn, up to 40 s total, appended at the end |
| Aspect ratio | `16:9` (default) and `9:16` only |
| Resolution | `360p`, `720p` (default), `1080p` and `4k` (upscaled) |
| Audio | Always generated: speech with lip-sync, ambience, effects, music |
| Inputs | First frame, first + last frame, up to 10 reference images, up to 3 reference videos (≤3 s each, their audio ignored), videos to edit or extend (≤10 s) |
| Negative prompt, seed | **No fields.** Put short "No X" clauses in the prompt |
| Language | English is fully supported; other languages are not evaluated |

Omni reasons about the prompt before generating and fills in detail from world knowledge. It needs
less frame-by-frame prescription than Veo: state the intention and the details you need to control.

## What to Include

Shot framing and motion, style, lighting (source and quality), location, and action. Add sound
design and, for edits, what stays the same. Meta-instructions are supported: `Consider
micro-detail, expression and timing to create a very rich, detailed but entirely natural scene.`

## Shots and Timing

- **Omni cuts by default.** It makes a few shots and builds a small narrative. For one take, say
  so: `One continuous shot, no jump cuts.` or `In a single unbroken scene.`
- Timing in plain language: `After 3 seconds, a woman enters the scene.`, `At 5s the chorus starts.`
- Timecodes for a sequence, about one beat per 3 s:

```text
[0-3s] A person is walking
[3-6s] They stop and turn around
[6-10s] They start running
```

- **State the length in the prompt**: `The whole scene lasts 8 seconds.` or `Entire story in 10
  seconds.` Rapid cutting can be timed in frames at 24 fps: `roughly 9 frames per item at 24FPS`.
- Editing terms work: match cut, jump cut, hard cut, montage, establishing shot sequence.

Official single-shot example:

```gemini-omni
Continuous, unbroken handheld shot of a fluffy tabby cat sitting on a sunny windowsill, looking out into a
leafy garden. The cat's tail twitches slowly, and its ears rotate slightly toward ambient noises. Sunbeams
illuminate dust motes in the air. Sound design: Gentle breeze, distant bird chirps. No dialogue.
```

## Camera

Use plain videography language: static / locked off, push in, punch in, dolly zoom, whip pan, arc,
crane, handheld, drone. Chain moves in order: `a close-up on his shoes, quickly tilting up to medium
shot, then widening.` Device looks work: `natural smartphone zoom`, `webcam style`, `shot on 35mm film`.

## Dialogue and Sound

- Speaker description + verb + colon + quoted line: `The man in the blue sweater replies: "Did your
  father go out on the boat too?"` Add voice and accent in prose: `in a calm voice with a soft
  Irish accent`.
- If quoted lines show up as captions, add `No subtitles.`; if they persist, drop the quotes and
  keep the colon (`A woman says: My name is Clara.`).
- `No dialogue.` when there is no speech; otherwise Omni may add some.
- Describe audio in its own sentences or a `Sound design:` label. Music: `Include calm background
  music`, `The music swells`. Trim: `No extra sound effects.` Sync works: `The apartment lights
  switch on in sync with the beat.`

## On-Screen Text

Quote the exact string and give placement, animation, and timing: `One word on the screen at a
time: "did, you, know". Each word appears for 1s with a different animated style.` Define
background text so it is not gibberish: `a street sign that says: "Harbor Road"`.

## Images and References

- Without tags, Omni decides how to use each image. Make roles explicit with inline tags placed
  next to the noun they bind, indexed from 0 in upload order:
  - `<FIRST_FRAME>`, `<LAST_FRAME>` (needs a first frame; the same image for both makes a loop)
  - `<IMAGE_REF_0>`, `<IMAGE_REF_1>`, ... and `<VIDEO_REF_0>`, ... for references
  - Example: `in the style of <IMAGE_REF_0> a woman <IMAGE_REF_1> is walking`
- Add a role sentence: `Use the given images as references; they should not be used as literal
  initial frames.` or `Use this image as the starting frame.`
- Say what to take from each: likeness, outfit, object, style ("grainy and moody as
  <IMAGE_REF_1>"), or motion ("apply the pose and motion from <VIDEO_REF_0>").
- Do not ask it to match a reference video's audio or to reason across several reference videos.
- First + last frame: describe what the first frame shows, the exact camera move or transition
  path, and what the last frame reveals. Image-to-video otherwise: describe motion, not the image.

Official first/last-frame example:

```gemini-omni
A close-up low-angle shot of a stylish drummer in a beige suit playing a red drum kit in a grand hall
transitions as the camera whip-pans to the side, revealing an older saxophonist playing alongside a ballet
dancer spinning in a white outfit under soft purple stage lights. One continuous shot, no jump cuts.
```

## Editing and Extending (Multi-Turn)

Each turn builds on the previous video; Omni keeps everything you do not mention.

- **Keep edit prompts short.** Overly descriptive edits cause unintended changes. End with
  `Keep everything else the same.`
  - Instead of a long description of a cat running in and jumping: `Add a cat that jumps onto his
    lap, he begins to pet it. Keep everything else the same.`
  - `Make the phone invisible. Keep everything else the same.`
  - `Change the camera angle to be over the violinist's shoulder.`
  - `Change the lighting to be more dramatic.` / `Make this video anime.`
- One change per turn for the most predictable result.
- Extension: `Continue the scene: the camera pans across the mountains.` Say whether it continues
  or cuts (`Show the same characters in the next scene.`) and how audio carries (`The music
  continues into the chorus.`). Timestamps restart at 0s for the extension.
- Uploaded videos must be 10 s or less; new dialogue cannot be added to an uploaded talking clip.

## Settings Line

`Settings: 16:9, 720p`. Add `task: image_to_video`, `reference_to_video`, `edit`, or `extend` when
inputs are attached, and `duration: "8s"` on Vertex or fal. The length sentence stays in the prompt.
Edits keep the source clip's length and ratio: `Settings: source length, source ratio, 720p, task: edit`.
