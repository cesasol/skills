# Ernie Image Prompting Guide

## Overview

Ernie Image is an 8B Diffusion Transformer (DiT) model with a built-in **Prompt Enhancer** — a separate language model that rewrites short prompts into structured descriptions before they reach the
diffusion model. This makes Ernie behave differently from most open models.

## Key Characteristics

- **Built-in Prompt Enhancer** automatically expands short prompts
- **Best-in-class text-in-image rendering** (scores 0.9733 on LongTextBench)
- **Strong layout understanding** — spatial phrases like "left third" or "centered" are followed
- **Multi-panel and comic layouts** work unusually well
- **Bilingual English + Chinese** workflows are seamless
- **Camera and lens language** matters strongly for photorealism

## The Prompt Enhancer: When to Use It

### Keep Enhancer ON

- Short or casual prompts
- Scene, landscape, portrait, or illustration ideation
- When you want rich detail without writing it all yourself

### Turn Enhancer OFF

- Exact control over details and precise spatial relationships
- Already-detailed prompts (over 80 words)
- Iterations from a saved enhanced prompt
- Benchmark-style precision tasks

**Trade-off**: With Enhancer enabled, GENEval Counting improves from 0.7781 to 0.8187 (better object counting), while overall GENEval drops from 0.8856 to 0.8728. The Enhancer adds breadth but can
cost precision.

## The 5-Part Prompt Formula

```text
[Subject] + [Scene/Context] + [Style] + [Lighting/Mood] + [Quality/Composition]
```

| Component | Example |
| ----------- | --------- |
| Subject | A ceramic coffee mug |
| Scene/Context | on a weathered oak table, morning kitchen |
| Style | commercial product photography |
| Lighting/Mood | soft window light from the left, warm tones |
| Quality/Composition | shallow depth of field, 8K, centered composition |

Full example:
> "A ceramic coffee mug on a weathered oak table in a morning kitchen setting, commercial product photography style, soft window light from the left with warm tones, shallow depth of field, 8K,
> centered composition"

## Text in Images (Ernie's Superpower)

Ernie Image is optimized for text-in-image prompts. Headlines, labels, and short callouts actually come out readable.

1. **Put the exact text string in quotation marks**
2. **Keep each text element under 8-10 words**
3. **Specify font weight and placement**
4. **Describe the background contrast** so text stays readable
5. **Use headlines and labels, not paragraphs**

Example:
> "Summer music festival poster, bold serif headline \"SUMMER BEATS 2026\" at the top in white, lineup names below in smaller sans-serif, dark teal background with abstract wave graphics, art deco
> border details, concert poster style"

## Multi-Panel and Comic Layouts

Ernie is unusually good at grids, panel sequences, and speech bubbles:

- **State the grid explicitly**: "3x2 grid", "4-panel vertical layout", "2-column split"
- **Describe each panel in numbered sequence**
- **Repeat character descriptors across panels**
- **Specify border treatment and dialogue text**

Example:

```text
4-panel manga comic, clean ink line art, expressive character design, black and white:
[Panel 1]: girl with short dark hair runs through a rainy city street, coat collar up, expression determined
[Panel 2]: she stops at an alleyway where a glowing golden door stands between two buildings, eyes wide
[Panel 3]: she pushes the door open and steps through, warm light flooding toward her
[Panel 4]: she emerges in a sunlit meadow full of wildflowers, turning back to see the door has vanished behind her, soft smile
Thin panel borders, cinematic pacing, readable expression work
```

## Bilingual Prompts (English + Chinese)

Ernie handles bilingual text better than most models:

- **State which language appears where**
- **Keep each string short**
- **Specify simplified or traditional Chinese** where relevant
- **Use labels, titles, and short callouts** rather than body copy

Example:
> "Tea product packaging label, \"MOUNTAIN WHITE TEA\" in clean serif at top, \"白毫银针\" in elegant traditional brush-style Chinese below, minimal pale silver background, fine line botanical
> illustration border, premium luxury packaging design, centered layout"

## Advanced Techniques

### Camera and Lens Language for Realism

| Term | Effect |
| ------ | -------- |
| `85mm portrait lens` | Natural facial proportions, compressed background |
| `35mm architectural lens` | Straight lines, minimal distortion |
| `macro photography` | Extreme close-up detail, soft surrounding blur |
| `shot on 35mm film` | Grain, muted saturation, analog response |

Example:
> "Portrait of a chef in a commercial kitchen, shot on 85mm lens at f/1.8, natural window light from the left, subject sharply focused, pots and pans softly blurred behind, candid expression,
> editorial portrait photography"

### Lighting Vocabulary

| Term | Effect |
| ------ | -------- |
| `golden hour` | Warm directional light, long shadows |
| `Rembrandt lighting` | 45-degree key light, classic portrait triangle shadow |
| `overcast diffused light` | Flat, even, ideal for products |
| `rim lighting` | Bright subject outline, dramatic separation |
| `volumetric light shafts` | Visible light beams through atmosphere |

### Compositional Language Ernie Understands

- `rule of thirds`
- `foreground / mid-ground / background layering`
- `subject in left third, negative space right`
- `bird's eye view` and `low angle looking up`
- `centered with negative space below`
- `top third`, `bottom third`
- `split-panel left and right`

## Iteration Workflow

1. Generate with your initial prompt (Enhancer ON for short prompts)
2. **Copy the enhanced prompt** after the first run
3. Keep what improved the image
4. Rewrite the drifted parts explicitly
5. Paste the modified enhanced prompt back into the next run (Enhancer OFF)

Most strong results appear on the second or third iteration, not the first.

## Common Mistakes

❌ **Too vague**
> "a nice picture of a woman"

✅ **Improved**
> "Portrait of a woman in her 40s sitting at an outdoor cafe, late afternoon golden light, relaxed confident expression, soft background blur, documentary photography style"

❌ **Conflicting styles**
> "photorealistic anime watercolor 8-bit pixel art"

✅ **Improved**
> "Anime-style illustration with a soft watercolor texture, pastel colors, clean linework, Studio Ghibli aesthetic"

❌ **Forgetting to quote text strings**
> "poster with the text Summer Beats 2026 at the top"

✅ **Improved**
> "Poster with the text \"SUMMER BEATS 2026\" in bold white serif at the top"

## Prompt Cheat Sheet

### Prompt Formula

```text
[Subject] + [Scene/Context] + [Style] + [Lighting] + [Composition/Quality]
```

### Text-in-Image Rules

- Put exact text in quotes
- Keep each text element under 8-10 words
- Specify font weight, placement, and contrast

### Prompt Enhancer

- **ON:** short prompts, ideation, complex scenes
- **OFF:** exact control, enhanced-prompt iteration, detailed prompts

### Multi-Panel

- State the grid explicitly
- Number each panel
- Repeat character descriptors across panels
