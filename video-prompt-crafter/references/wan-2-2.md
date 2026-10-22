# Wan 2.2 Prompting Guide

Applies to: Alibaba's open-weight **Wan 2.2** (Apache 2.0, July 2025): `Wan2.2-T2V-A14B`,
`Wan2.2-I2V-A14B`, `Wan2.2-TI2V-5B`, plus `Wan2.2-S2V-14B` (speech-driven) and `Wan2.2-Animate-14B`.
It runs locally in ComfyUI, Diffusers, or the official repo, and on Alibaba Cloud Model Studio as
`wan2.2-t2v-plus`, `wan2.2-i2v-plus`, `wan2.2-i2v-flash`, and `wan2.2-kf2v-flash`. It is the newest
open-weight Wan; Wan 2.5 and later are API-only (see `wan-3.md`).

## Hard Limits

- **Silent.** T2V, I2V, and first/last-frame clips have no audio track. Write no dialogue, sound
  effects, or music. Show speech as action ("her lips move as she talks"). Lip-synced speech needs
  S2V with a real audio file.
- **One continuous shot, about 5 seconds.** No multi-shot, cuts, timestamps, or `Shot 1:` syntax,
  and no `Image 1` reference tags; those are Wan 2.6+ features.
- **Text renders approximately.** Short quoted words on signs can work; long copy does not.

| Variant | Frames | fps | Sizes (W×H) |
| ------- | ------ | --- | ----------- |
| T2V-A14B, I2V-A14B | 81 | 16 | 1280×720, 720×1280, 832×480, 480×832 |
| TI2V-5B (T2V and I2V in one) | 121 | 24 | 1280×704, 704×1280 |
| S2V-14B | follows the audio | 16 | as A14B, plus 1024×704, 704×1024 |

- Frame count must be 4n+1. Raising it far past the default loops or degrades motion; chain clips
  instead (last frame → I2V).
- For I2V the size is an area; the aspect ratio follows the input image.
- ComfyUI 14B templates default to 640×640 for low VRAM; recommend a size from the table.
- API `wan2.2-t2v-plus` is fixed at 5 s and offers 480p and 1080p tiers: 832×480, 480×832, 624×624,
  1920×1080, 1080×1920, 1440×1440, 1632×1248, 1248×1632. `wan2.2-kf2v-flash` does first+last frame.

## Prompt Length and Rewriting

- Official rewriter targets: **T2V 60-200 words, I2V 100 words or fewer**. Around 80-120 words works
  well for T2V. The text encoder reads 512 tokens; the API cuts prompts at 800 characters.
- The API's `prompt_extend` defaults to `true` and rewrites your prompt. Put `prompt_extend: false`
  on the Settings line when you send a finished prompt to the API. ComfyUI has no rewriter.

## Prompt Shape

Wan 2.2's own rewriter and examples use: optional comma-separated **cinematic tag prefix** (light,
shot size, composition, tone) → subject and appearance → action as it unfolds → background and
environment motion → camera move. If there is a style, it goes first.

- Formula: **Subject (with description) + Scene (with description) + Motion (with speed and
  amplitude) + Aesthetic control (light, shot size, angle, lens, camera move) + Style**.
- Describe visible things. Mood prose ("full of life and tension") is noise.
- Add no subjects the user did not ask for. If nothing moves, add one action and some background
  motion (clouds drifting, wind in leaves).
- Skip a camera-angle tag when you already describe a camera move.
- Camera: "The camera slowly pans to the right", "the camera pushes in", "the camera pulls back to
  reveal...". Sequence moves with "then". Still frame: "fixed camera".
- Keep orbits under about 45 degrees. Whip pans, slow 360° orbits, and simultaneous compound moves
  (dolly back while tilting up) often fail; push-in, pull-back, pans, tilt up, tracking, and crash
  zoom work.

Official T2V example (`wan2.2-t2v-plus`):

```wan-2-2
Low contrast. In a retro 1970s-style subway station, a street musician plays amidst dim colors and rough
textures. He wears an old-fashioned jacket and holds a guitar, playing with concentration. Commuters hurry
past, and a small crowd gradually gathers to listen. The camera slowly pans to the right, capturing a scene
where the sound of the instrument mixes with the city's noise, with old-fashioned subway signs and mottled
walls in the background.
```

Official tag-prefix style (from the Model Studio guide, generated with Wan 2.2):

```wan-2-2
Rim light, low contrast, medium close-up, daylight, left-heavy composition, clean single shot, warm tones,
soft light, clear sky light, side light, daytime. A young girl sits in a field of tall grass with two fluffy
donkeys standing behind her. The girl is about 11 or 12 years old, wearing a simple floral dress with her hair
in two braids, and has an innocent smile on her face. She sits cross-legged, gently touching the wildflowers
beside her. The donkeys are sturdy, with their ears pricked up, curiously looking toward the camera. Sunlight
bathes the field, creating a warm and natural scene.
```

## Image-to-Video and First/Last Frame

- Formula: **Motion + Camera movement**. Keep subject actions and camera phrases; drop static
  descriptions the image already shows. 100 words or fewer.
- First+last frame (ComfyUI FLF2V template, or `wan2.2-kf2v-flash`): describe the continuous change
  and the camera path from frame A to frame B. Official example: "Realistic style, a small black
  cat looks up at the sky curiously, the camera gradually rises from eye level, and finally
  captures its curious gaze from a top-down view."
- S2V prompts start "In the video, ..." and describe who speaks, their emotion, motion, and camera.

## Negative Prompt

Wan 2.2 has a real negative prompt field (API maximum 500 characters). Give it as a second block
tagged `negative-prompt`. Start from the official default, which is Chinese, and append
comma-separated English terms for this scene's risks:

```negative-prompt
色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，画得不好的脸部，畸形的，毁容的，形态畸形的肢体，手指融合，静止不动的画面，杂乱的背景，三条腿，背景人很多，倒着走
```

It covers: oversaturated, overexposed, static, blurry detail, subtitles, style/artwork/painting,
gray cast, worst/low quality, JPEG artifacts, ugly, incomplete, extra or fused fingers, bad hands
and faces, deformed limbs, motionless frame, cluttered background, three legs, crowded background,
walking backwards.

- Remove `字幕` (subtitles) when the user wants on-screen text.
- Remove `风格，作品，画作，画面` (style, artwork, painting, picture) for illustrated or painterly styles.
- **CFG 1 ignores the negative prompt.** The current ComfyUI 14B templates use the lightx2v 4-step
  LoRA at CFG 1. In that case, write the important constraints positively in the main prompt
  ("steady camera", "four legs") and note it in the description sentence.

## Settings Line

Give the variant, size, frames, and fps; add CFG notes only when they change the result.

- Local 14B: `Settings: T2V-A14B, 1280×720, 81 frames at 16 fps`
- Local 5B: `Settings: TI2V-5B, 1280×704, 121 frames at 24 fps`
- API: `Settings: wan2.2-t2v-plus, 1920*1080, 5 s, prompt_extend: false`

The lightx2v / Lightning speed LoRA reduces motion dynamics. When a variation depends on strong
motion, recommend the non-LoRA path (about 20-40 steps, CFG 3.5-5).

## Vocabulary From the Official Rewriter

- Light source: daylight, artificial lighting, moonlight, practical lighting, firelight,
  fluorescent lighting, overcast lighting, sunny lighting
- Light: soft lighting, hard lighting, top lighting, side lighting, underlighting, edge lighting,
  rim light, backlight
- Time: day time, night time, dawn time, sunrise time, dusk, golden hour
- Shot size: extreme close-up, close-up, medium close-up, medium shot, medium wide shot, wide shot,
  extreme wide shot
- Angle: over-the-shoulder, low angle, high angle, Dutch angle, aerial, overhead
- Composition: center, balanced, left-heavy, right-heavy, symmetrical, short-side composition
- Tone: warm colors, cool colors, mixed colors, low saturation
- Styles shown on 2.2: felt style, 3D cartoon, pixel style, puppet animation, claymation, black and
  white animation, documentary photography, tilt-shift, time-lapse
