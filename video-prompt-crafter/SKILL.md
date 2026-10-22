---
name: video-prompt-crafter
description: >
  Use when the user wants to write, expand, refine, or convert a prompt for an AI video
  generation model, including Wan 2.2 (local ComfyUI or API), Wan 3.0, FLUX 3 Video, and
  Gemini Omni (Omni Flash, also called "Veo 4"); when they want to animate a still image,
  connect first and last frames, extend or edit a clip, plan a multi-shot sequence, or add
  dialogue, sound effects, or music to a generated video; or when they describe a scene, ad,
  or short they want turned into a video clip, even if they never say "prompt". Triggers
  include "text-to-video prompt", "image-to-video", "make this video prompt better", and
  "convert this Veo/Kling/Sora prompt for [model]".
---

# Video Prompt Crafter

Craft, expand, refine, and convert prompts for AI video generation, image-to-video, and video
editing. A video prompt directs a shot over time: who moves, how the camera moves, what changes
between the first and last frame, and what the viewer hears. Always write the complete final
prompt yourself.

## Workflow

1. **Pick the target model(s)** with the rules below. Do not ask a follow-up question about the
   model. If the user wants several models, write one set of variations per model.
2. **Read the references** in `references/`: `common-video-prompting.md` always, plus the one for
   each target model (see the table).
3. **Classify the task** and apply its rule:
   - **Craft**: the user describes a concept. Write the full prompt.
   - **Expand**: the user has a short prompt. Add camera, light, motion, and sound; keep the subject.
   - **Refine**: the user has a prompt and a problem. Variation 1 is their prompt with only the fix
     applied, every untouched sentence kept word for word. The others try different fixes.
   - **Convert**: the user has a prompt for another model. Keep the content; rewrite it into the
     target model's syntax and drop what the target cannot do (see Conversion).
   - **Animate (image-to-video, first/last frame, keyframes)**: describe motion, camera, and sound.
     Leave out what the image already shows.
   - **Edit or extend a video**: write a short change instruction, not a new scene.
4. **Budget the beats.** Fit the action to the clip length: about one subject action plus one
   camera move per 5 seconds. When the user asks for more than the model's maximum length, write
   one prompt per clip, each clip its own block, and say so in the description sentence.
5. **Write 2-3 variations.** Variation 1 stays closest to the user's vision; the others branch on
   camera, pacing, lighting, or sound. Every variation keeps the core subject and intent.

## Choosing the Model

Take the first rule that matches.

1. The user names a supported model: use it. "Veo 4", "Omni Flash", "Veo 3", and "Veo 3.1" mean
   Gemini Omni. "Wan 3" means Wan 3.0. "Wan 2.5", "Wan 2.6", or "Wan 2.7" means Wan 3.0, and a
   named model outside the table (Kling, Sora, Runway, Seedance, LTX, Hunyuan) means the model the
   rules below pick. In both cases start variation 1's description sentence with
   `Written for <model>; <named model> is not supported.`
2. The context points to local generation (ComfyUI, Diffusers, "on my GPU", offline, open
   weights): **Wan 2.2**. It is the only model here with open weights.
3. They want to edit or extend an existing video, or keep iterating on a clip turn by turn:
   **Gemini Omni**.
4. They supply reference images, videos, or audio for a character, object, style, or voice that
   must not appear as a literal frame, or they need more than 20 seconds: **Wan 3.0**.
5. They supply a start image, start and end frames, or a storyboard of keyframes: **FLUX 3 Video**.
6. Anything else: **FLUX 3 Video**. Use Gemini Omni instead when the user works in the Gemini app,
   Google Flow, or YouTube Shorts.

| Model | Fence tag | Reference | Length | Audio | Negatives go |
| ----- | --------- | --------- | ------ | ----- | ------------ |
| Wan 2.2 | `wan-2-2` | `wan-2-2.md` | 5 s (81 frames at 16 fps) | None | `negative-prompt` block |
| Wan 3.0 | `wan-3` | `wan-3.md` | 2-30 s | Native, on by default | `Negative prompt list:` line |
| FLUX 3 Video | `flux-3-video` | `flux-3-video.md` | 5-20 s | Native, on by default | Short "No X" clauses |
| Gemini Omni | `gemini-omni` | `gemini-omni.md` | 3-10 s, extend to 40 s | Native, always on | Short "No X" clauses |

## Output Format

The response contains only variation blocks. One block is, in order:

1. A fenced code block holding the prompt, tagged with the model's fence tag.
2. For Wan 2.2 only: a second fenced block tagged `negative-prompt` (see `wan-2-2.md`).
3. `Settings: <duration>, <aspect ratio>, <resolution>` followed by every other parameter the
   result depends on (audio off, `prompt_extend: false`, task, frame count, fps). Use the
   parameter values the model's reference lists. For edits and extensions, write `source` for
   any length or aspect ratio that the input video sets.
4. For inputs: `Inputs: image 1 = <role>, image 2 = <role>`, in the order to upload them.
5. One sentence saying how this variation differs. For Refine, say what changed and why.

Example block:

```flux-3-video
Low tracking shot of a red fox trotting through fresh powder between white birch trunks at sunrise...
```

Settings: 8 s, 16:9, hd
Closest to your idea: one continuous take that follows the fox at eye level.

With several models, give all of one model's blocks before the next model's. Use no headers, no
bold labels, and no text before the first block or after the last.

## Rules

- **Settings stay out of the prompt.** Aspect ratio, resolution, fps, and frame count go on the
  Settings line. Clip length goes there too, except for Gemini Omni, which takes its length from
  the prompt ("The whole scene lasts 8 seconds."). Timestamps for beats inside the clip are fine.
- **Name the camera every time.** Give one framing term and one movement per shot, or write
  "locked-off camera". Without a camera cue the models drift or move the subject instead.
- **Write natural-language prose** in present tense, with concrete nouns and verbs the camera can
  see. Use labeled sections or timestamps only in the forms the model's reference documents.
- **Quote spoken lines and on-screen text** in double quotes, and tie every line to a visible
  speaker or to "voiceover". Wan 2.2 is silent: turn speech into visible action.
- **Describe sound by its source** for models with audio: dialogue, ambience, effects, and music,
  each tied to something on screen. Say "No music" or "No dialogue" when the user wants none.
- **Describe the lighting specifically**: its source, direction, and quality.
- **Follow an explicit user length request** ("keep it short") over the model's usual range.

## Edge Cases

- More beats than fit: keep the strongest beats in one prompt, or split into one prompt per clip.
  For a chain of clips, open each later clip from the previous clip's last frame.
- Conflicting camera directions (locked-off and tracking, one take and hard cuts): keep the one
  closest to the user's intent.
- Unsafe, real-person, copyrighted-character, or brand-heavy wording: keep the visual intent with
  generic descriptive language.
- An image or video described but not attached: write for the inputs they described and give the
  Inputs line.
- Wan 2.2 with dialogue or music requested: keep the speaking as mouth movement and gesture, and
  say in the description sentence that the clip is silent and the audio goes on in editing.

## Conversion

- **Remove what the target cannot do**: audio for Wan 2.2; cuts and timestamps for Wan 2.2;
  durations beyond the target's maximum; aspect ratios other than 16:9 and 9:16 for Gemini Omni.
- **Move negatives to where the target reads them** (the "Negatives go" column).
- **Rewrite reference syntax**: `<IMAGE_REF_0>` (Gemini Omni), `Image 1` (Wan 3.0), and plain
  descriptions plus keyframes (FLUX 3 Video, Wan 2.2).
- **Rewrite multi-shot syntax**: `SHOT ONE: ... HARD CUT.` (FLUX 3 Video), `Shot 1 [0-3s]:`
  (Wan 3.0), `[0-3s]` timecodes (Gemini Omni), one continuous shot (Wan 2.2).
