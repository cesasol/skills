---
name: flux-prompt-gen
description: Generate optimized text-to-image prompts for Black Forest Labs FLUX models (FLUX.1, FLUX.2 [pro], FLUX.2 [max], FLUX.2 [klein]). Use this skill whenever the user wants to create, improve, or refine a Flux image prompt — including when they describe an image they want to generate, ask to "write a Flux prompt", say "help me prompt Flux/BFL/FLUX.2", want to improve an existing prompt, or are building an image generation pipeline using any FLUX model. Also trigger when users ask about Flux prompting techniques, best practices, or how to get specific visual results from FLUX.
---

# FLUX Prompt Generation Skill

All FLUX models share a core structure but have **model-specific behaviors** — always ask or infer which model is being used before finalizing a prompt.

---

## Model Selection Guide

| Model | Prompt Style | Key Differentiator |
|-------|-------------|-------------------|
| **FLUX.1 [dev/schnell/pro]** | Structured, medium length | Responds to keyword-forward structured prose |
| **FLUX.2 [pro] / [max]** | Natural language + JSON support | Handles hex colors, JSON schemas, multi-reference |
| **FLUX.2 [klein]** | Novelist prose, lighting-heavy | NO prompt upsampling — must be fully descriptive |

---

## Universal Core Framework

All FLUX models respond to: **Subject → Action → Style → Context**

**Word order matters**: Front-load the most important elements. FLUX weighs earlier tokens more.

Priority order: Main subject → Key action → Critical style → Essential context → Secondary details

---

## Prompt Length Guidelines

| Length | Words | Best For |
|--------|-------|----------|
| Short | 10–30 | Quick concepts, style exploration |
| Medium | 30–80 | Most production work (sweet spot) |
| Long | 80–300+ | Complex scenes, multi-subject, technical specs |

Start short. Add only what materially changes the image.

---

## FLUX.1 Prompting

### Base Structure

```
[Subject description], [action/pose], [style/medium], [lighting/context], [atmosphere]
```

### Enhancement Layers (add progressively)

```
Foundation:    Subject + Action + Style + Context
+ Visual:      Specific lighting, color palette, composition
+ Technical:   Camera settings, lens specs, quality markers
+ Atmospheric: Mood, emotional tone, narrative
```

### Use-Case Patterns

**Character-focused** (portraits, character art):
> Detailed character → Action → Style → Context

**Context-focused** (landscapes, architecture):
> Setting → Atmospheric conditions → Style → Technical specs

**Style-focused** (artistic interpretations):
> Artistic reference → Subject → Context → Technical execution

**Technical/Photography**:
> Subject → Background → Lighting → Lens/settings

### Photography Controls

- **Aperture**: `f/1.4` = blurred background; `f/8` = sharp throughout
- **Focal length**: `24mm` = wide scene; `85mm` = zoomed/compressed
- **Lighting**: `Rembrandt lighting`, `golden hour`, `blue hour`, `chiaroscuro`, `split lighting`
- **ISO**: low = clean; high = grain/atmosphere

### Structured Descriptions Beat Keyword Lists

❌ `Woman, red dress, beach, sunset, waves, golden light`
✅ `A joyful woman in a flowing red dress walks along a sandy beach, golden hour, gentle waves, warm lighting`

---

## FLUX.2 [pro] / [max] Prompting

All FLUX.1 techniques apply, plus these exclusive capabilities:

### HEX Color Control

Associate hex codes directly with objects:
```
a vintage illustration of an apple in color #0047AB on a white background
```

For gradients:
```
vase with color gradient starting #02eb3c to #edfa3c, flowers in #ff0088
```

### JSON Structured Prompting

Use for complex scenes, automation, or brand precision:

```json
{
  "scene": "overall scene description",
  "subjects": [
    {
      "description": "detailed subject",
      "position": "where in frame",
      "action": "what they're doing",
      "color_match": "exact"
    }
  ],
  "style": "artistic style",
  "color_palette": ["#hex1", "#hex2"],
  "lighting": "lighting description",
  "mood": "emotional tone",
  "camera": {
    "angle": "camera angle",
    "lens": "lens type",
    "lens-mm": 85,
    "f-number": "f/2.8",
    "depth_of_field": "shallow"
  }
}
```

Use JSON when: production workflows, automation, multiple subjects with precise colors, brand consistency.
Use natural language when: quick iteration, single-subject, creative exploration.

### Style Reference Table

| Style | Prompt Keywords |
|-------|----------------|
| Modern digital | `shot on Sony A7IV, clean sharp, high dynamic range` |
| 2000s digicam | `early digital camera, slight noise, flash photography, 2000s digicam style` |
| 80s vintage | `film grain, warm color cast, soft focus, 80s vintage photo` |
| Analog film | `shot on Kodak Portra 400, natural grain, organic colors` |

### Aspect Ratios

| Ratio | Use Case |
|-------|----------|
| 1:1 | Social media, product shots |
| 16:9 | Landscapes, cinematic |
| 9:16 | Mobile, portraits |
| 4:3 | Magazine, presentations |
| 21:9 | Panoramas |

### Text / Typography in Images

- Wrap exact text in quotes: `the text 'OPEN' in red neon letters`
- Specify placement, font style, color (`#hex` works)
- Front-load text descriptions for better accuracy

### Prompt Upsampling

FLUX.2 [pro/max] supports `prompt_upsampling: true` — auto-expands short prompts. Good for exploration, skip for brand-controlled outputs.

### Multi-Language

Prompting in the language matching the cultural context produces more authentic results (French for Parisian scenes, Japanese for anime styles, etc.)

---

## FLUX.2 [klein] Prompting

**Critical difference**: No prompt upsampling — write every detail explicitly. Think like a novelist, not a search engine.

### Structure

```
Subject → Setting → Details → Lighting → Atmosphere
```

### Lighting is the Highest-Leverage Element

Describe: source + quality + direction + temperature + surface interaction

```
soft, diffused natural light filtering through sheer curtains, casting warm shadows across worn wooden surfaces
```

vs `"good lighting"` (weak)

### Prose Style

✅ Strong: *"A weathered fisherman in his late sixties stands at the bow of a small wooden boat, wearing a salt-stained wool sweater, hands gripping frayed rope. Golden hour sunlight filters through morning mist, creating a sense of quiet determination."*

❌ Weak: *"old fisherman, boat, wool sweater, rope, golden hour, mist, documentary style"*

### Style/Mood Annotations (append to prose)

```
[Scene description]. Style: Country chic meets luxury lifestyle editorial. Mood: Serene, romantic, grounded.
```

### Image Editing Prompts ([klein] i2i)

Focus on the transformation, not the full scene:

| Edit Type | Pattern |
|-----------|---------|
| Style transfer | `"Turn into [style]"` |
| Object swap | `"Replace [element] with [new element]"` |
| Add elements | `"Add [element] to [location]"` |
| Environmental | `"Change the season to winter"` |

❌ Avoid: `"Make it better"`, `"Improve the lighting"`, `"Fix the image"`

---

## Positive-Only Framing (All Models)

FLUX models do **not** support negative prompts. Always describe what you want to see, not what to avoid.

**Mental model**: Ask "If this thing wasn't there, what would I see instead?"

Common conversions:
- `no people` → `empty`, `deserted`, `solitary`
- `no background distractions` → `smooth gradient background from deep blue to black`
- `not dark` → `brightly lit`, `sun-drenched`
- `not too realistic` → `stylized illustration with simplified forms and bold color blocks`
- `no modern elements` → `period-accurate`, `historical`, `traditional`

---

## Advanced Techniques

### Layered Compositions

```
Foreground (sharp focus): [closest element]
Middle Ground: [main subject]
Background (blurred): [setting]
```

### Style Fusion

```
Primary style: [dominant approach]
+ Secondary style: [complementary approach]
+ Unifying element: [cohesive color palette or technique]
```

### Cinematic References

```
Dramatic chiaroscuro lighting in the style of Roger Deakins cinematography, 
teal and orange color grading reminiscent of Blade Runner 2049, 
slight Dutch angle for psychological tension
```

## Examples

**User asks:** "Write a FLUX.2 [klein] prompt for a gold alchemy-themed landing page hero."

**Deliver:** a natural-language prompt that front-loads the subject, includes precise lighting,
composition, material, and brand color details, then adds a shorter and a more detailed variation.

## Edge Cases

- If the user does not name a FLUX variant, infer from context when obvious; otherwise ask once before finalizing model-specific syntax.
- If the user requests text in the image, keep wording short and exact; FLUX can still distort long typography.
- If the user gives a negative prompt, rewrite it into positive visual constraints rather than preserving negations.

### Comic Strip / Sequential Art

For consistent characters across panels: repeat the full physical description in every panel prompt. Character continuity requires redundancy.

---

## Quality Control Checklist

Before delivering a prompt, verify:
- [ ] Most important elements are front-loaded
- [ ] Specific descriptors used (not vague terms like "artistic" or "nice lighting")
- [ ] Positive framing throughout — no negations
- [ ] All elements serve a unified vision
- [ ] Length matches scene complexity
- [ ] Model-specific features used (hex for FLUX.2, prose for [klein])

---

## Output Format

When generating a prompt for the user, always deliver:

1. **The ready-to-use prompt** (copy-paste ready, no code fences unless JSON)
2. **Model target** (which FLUX variant it's optimized for)
3. **Brief rationale** (1-2 lines on key choices — optional if context is obvious)
4. **Variations** (2 alternatives: one shorter/simpler, one more detailed) — unless user specifies otherwise
