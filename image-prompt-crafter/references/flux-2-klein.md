# FLUX.2 Klein 4B Prompting Guide

Applies to: **FLUX.2 Klein 4B** only, the local option. For **FLUX 3 Image** and **FLUX 3 Image
Klein**, read `flux-3.md` instead.

## Overview

FLUX.2 Klein 4B is Black Forest Labs' smallest open-weight model: Apache 2.0 and available in
ComfyUI and Diffusers. It does text-to-image and image
editing with up to 4 reference images, often in under a second. It has no prompt rewriting, so what
you write is exactly what the model receives.

## Prompting Principles

### Natural Language is King

Flux models understand prose. Write prompts that read like clear image descriptions rather than keyword lists. The model interprets relationships, context, and mood from natural language.

Example:

- ❌ "woman, red hair, city, night, neon, cyberpunk"
- ✅ "A young woman with bright red hair stands on a rain-slicked rooftop at night, surrounded by holographic neon advertisements"

### Prompt Structure

Flux responds well to this flow:

```text
[SUBJECT], [LOCATION],
[STYLE], [CAMERA SETTINGS], [LIGHTING], [COLORS], [EFFECT],
[ADDITIONAL ELEMENTS]
```

Front-load the most important information. Word order signals priority.

### Prompt Length

| Length | Words | Best For |
| -------- | ------- | ---------- |
| Short | 10-30 | Quick concepts, fast iteration, style exploration |
| Medium | 30-80 | Most scenes and everyday prompting |
| Long | 80-300+ | Complex multi-subject scenes or very directed outputs |

For Klein, write the long tier: one full paragraph, typically 80-200 words. BFL documents no
length cap. Short prompts produce generic results.

Size is set with `width` and `height`, so any aspect ratio can be recommended.

### Text in Images

Flux has excellent text rendering. Use this three-step approach:

1. **Enclose in quotation marks**: `"COFFEE SHOP"` or `"Est. 1952"`
2. **Describe placement**: `"The text 'OPEN' appears in red neon letters above the door"`
3. **Specify font style**: `"elegant serif typography"` or `"bold industrial sans-serif lettering"`

**Tips for best text accuracy:**

- Front-load text descriptions
- Use quotation marks around exact text
- Describe color and effects: "red neon letters", "gold serif lettering"
- Use hex codes for brand-precise colors: `"The logo text 'ACME' in color #FF5733"`
- Keep text short — long strings are harder to render
- Give each text element a size role: "large headline", "medium subheading", "small body copy"
- Specify font character: serif = traditional/formal, sans-serif = modern, script = elegant

### Typography Styles

| Style | Description |
| ------- | ------------- |
| 3D text | "raised chrome letters with realistic metal reflections" |
| Neon effects | "glowing neon text with electric blue light" |
| Vintage signs | "weathered painted text with chipped paint and rust" |
| Environmental | "carved directly into the ancient stone wall" |
| Object-based | "printed on a newspaper being read by the character" |

### No Negative Prompts

Flux models do not support negative prompts effectively. AI models generally struggle with negation — writing "a person without glasses" causes the model to focus on "glasses" and often generates
exactly what you were trying to avoid.

**Use the replacement strategy:**

| Instead of... | Write... |
| -------------- | ---------- |
| "no crowds" | "peaceful solitude", "empty pathways" |
| "not dark" | "brightly lit", "sun-drenched" |
| "no text" | "clean surfaces", "unmarked" |
| "without clothes" | "bare skin", "natural form" |
| "not sad" | "joyful", "content" |

If unwanted elements persist:

1. Be more specific about what you DO want in that space
2. Front-load the positive description
3. Add more descriptive detail to strengthen the positive alternative

### Lighting is Critical

Lighting has the greatest single impact on output quality. Describe it like a photographer:

- **Source**: natural, artificial, ambient, practical (visible in scene)
- **Quality**: soft, harsh, diffused, direct
- **Direction**: side, back, overhead, fill
- **Temperature**: warm, cool, golden, blue

**Portrait lighting:**

- **Rembrandt lighting** (45° key light): "Portrait with Rembrandt lighting, key light at 45 degrees, dramatic chiaroscuro effect"
- **Split lighting** (90° side light): "Artistic portrait, split lighting, strong side illumination"

**Environmental light:**

- Window light = soft, even
- Golden hour = warm and soft
- Blue hour = cool and moody
- Overhead artificial = harsh and dramatic

### Style Fusion

Combine two styles with a unifying palette:

> "Ancient Greek marble statue precision and anatomical detail, infused with cyberpunk neon lighting, holographic overlays, and electric blue/magenta glow effects"

Add explicit style/mood annotations at the end for consistent aesthetics:

```text
[Scene description]. Style: Country chic meets luxury lifestyle editorial.
Mood: Serene, romantic, grounded.
```

### Multilingual Prompting

Flux can be prompted in multiple languages, but English produces the most precise results since the majority of training data is in English.

### Iteration

Build prompts incrementally. Start simple, observe, then add one element at a time:

1. "A tall sharp-featured man in an oversized charcoal wool coat"
2. Add location: "...standing on a wet cobblestone street at night"
3. Add style: "...fashion editorial, moody street lighting"
4. Add details: "...he holds a teddybear, a dog walks beside him"
5. Add atmosphere: "...colorful vintage cars, flash photography, dark sky"
6. Change medium: "...watercolor illustration style"

## Klein 4B Specifics

- **Write one detailed paragraph.** BFL: "describe scenes like a novelist". Cover subject, setting,
  light source and direction, camera, and palette, then end with `Style: [style]. Mood: [mood].`
  The Style/Mood ending is for text-to-image only; edit instructions end with what must stay
  unchanged.
- **Use natural-language emphasis**, not weight syntax: "prominently featuring", "with particular
  attention to", "especially detailed".
- **Hex colors work**: "the logo text 'ACME' in color #FF5733".
- **Editing** takes up to 4 reference images. Give each image a role in the instruction: "The subject from image 1 wearing the jacket from image 2, photographed in the environment
  from image 3." Name what must stay unchanged.
- **Seed is supported.** Add `Settings: fixed seed` to every Klein block, so the variations
  differ only by prompt.

## Photorealistic Style Reference

| Style | Key Descriptors |
| ------- | ---------------- |
| Modern Digital | "shot on Sony A7IV, clean sharp, high dynamic range" |
| 2000s Digicam | "early digital camera, slight noise, flash photography, candid, 2000s digicam style" |
| 80s Vintage | "film grain, warm color cast, soft focus, 80s vintage photo" |
| Analog Film | "shot on Kodak Portra 400, natural grain, organic colors" |

For photorealism, specify camera models, lenses, and film stocks. "Shot on Fujifilm X-T5, 35mm f/1.4" produces more authentic results than just "professional photo."
