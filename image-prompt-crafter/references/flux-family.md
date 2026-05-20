# Flux Family Prompting Guide

Applies to: **FLUX.1 Dev**, **FLUX.2 Dev**, **FLUX.2 Klein**

## Overview

The Flux family from Black Forest Labs uses flow matching and natural language understanding. All variants excel at prompt adherence, visual quality, and text rendering. They share core prompting behavior with key differences noted below.

## Shared Principles (All Flux Models)

### Natural Language is King

Flux models understand prose. Write prompts that read like clear image descriptions rather than keyword lists. The model interprets relationships, context, and mood from natural language.

Example:
- ❌ "woman, red hair, city, night, neon, cyberpunk"
- ✅ "A young woman with bright red hair stands on a rain-slicked rooftop at night, surrounded by holographic neon advertisements"

### Prompt Structure

Flux responds well to this flow:

```
[SUBJECT], [LOCATION],
[STYLE], [CAMERA SETTINGS], [LIGHTING], [COLORS], [EFFECT],
[ADDITIONAL ELEMENTS]
```

Front-load the most important information. Word order signals priority.

### Prompt Length

| Length | Words | Best For |
|--------|-------|----------|
| Short | 10-30 | Quick concepts, fast iteration, style exploration |
| Medium | 30-80 | Most scenes and everyday prompting |
| Long | 80-300+ | Complex multi-subject scenes or very directed outputs |

Flux.2 supports prompts up to 32K tokens. Start short and add only what changes the image.

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
- Specify font character: serif = traditional/formal, sans-serif = modern, script = elegant

### Typography Styles

| Style | Description |
|-------|-------------|
| 3D text | "raised chrome letters with realistic metal reflections" |
| Neon effects | "glowing neon text with electric blue light" |
| Vintage signs | "weathered painted text with chipped paint and rust" |
| Environmental | "carved directly into the ancient stone wall" |
| Object-based | "printed on a newspaper being read by the character" |

### No Negative Prompts

Flux models do not support negative prompts effectively. AI models generally struggle with negation — writing "a person without glasses" causes the model to focus on "glasses" and often generates exactly what you were trying to avoid.

**Use the replacement strategy:**

| Instead of... | Write... |
|--------------|----------|
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

```
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

## Model-Specific Differences

### FLUX.1 Dev

- 12 billion parameters
- Open-weight, guidance-distilled
- Natural language oriented
- Built-in prompt upsampling (short prompts get expanded)
- No negative prompts

**Best practices:**
- Write clear, descriptive natural language
- Short prompts work well due to upsampling
- Reference specific cameras, lenses, film stocks for photorealism

### FLUX.2 Dev

- Up to 32K token prompts
- Built-in prompt upsampling (short prompts get expanded)
- Excellent typography
- HEX color codes supported: `"in color #FF5733"`
- JSON structured prompts supported for production workflows
- No negative prompts

**Best practices:**
- Same as FLUX.1 Dev but with much longer prompt capacity
- Use HEX codes for brand-precise colors
- Can use JSON format for complex production workflows

### FLUX.2 Klein

- 4 billion parameters
- Sub-second generation
- **NO prompt upsampling** — what you write is exactly what the model receives
- Must write detailed, descriptive prompts for best results
- Supports image editing with single and multi-reference inputs
- Add `Style: [style]. Mood: [mood].` at the end for consistent aesthetics

**Best practices:**
- **Write detailed prose** — short prompts will produce generic results
- Use natural language emphasis instead of weight syntax: "prominently featuring", "with particular attention to", "especially detailed"
- Lighting descriptions have the highest single impact
- For editing: "The subject from the first image wearing the jacket from the second image, photographed in the environment from the third image"
- Keep prompts under 100 words to avoid confusion
- Use the seed parameter to maintain consistency when testing variations

### FLUX.1 Kontext (Editing)

- Specify what should CHANGE — the input image provides all other context
- Use quotation marks for text editing: `Replace 'joy' with 'BFL'`
- Be explicit about preservation: "while maintaining the same facial features and hairstyle"
- Prefer specific verbs: "change the clothes" over "transform the person"
- For multiple changes, add as many explicit details as possible

## Photorealistic Style Reference

| Style | Key Descriptors |
|-------|----------------|
| Modern Digital | "shot on Sony A7IV, clean sharp, high dynamic range" |
| 2000s Digicam | "early digital camera, slight noise, flash photography, candid, 2000s digicam style" |
| 80s Vintage | "film grain, warm color cast, soft focus, 80s vintage photo" |
| Analog Film | "shot on Kodak Portra 400, natural grain, organic colors" |

For photorealism, specify camera models, lenses, and film stocks. "Shot on Fujifilm X-T5, 35mm f/1.4" produces more authentic results than just "professional photo."
