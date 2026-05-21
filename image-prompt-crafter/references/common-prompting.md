# Common Prompting Principles

These principles apply across all supported image generation models.

## Prompt Structure Template

A well-structured prompt generally follows this flow:

```text
[SUBJECT], [LOCATION/ACTION],
[STYLE], [CAMERA/FRAMING], [LIGHTING], [COLORS], [EFFECTS],
[ADDITIONAL ELEMENTS]
```

This is a guide, not a rigid formula. Use only the parts that improve the image.

## Core Principles

### 1. Start with the Subject

Begin with what the image is *about*. Be specific:

- **Vague**: "a person in a garden"
- **Specific**: "an elderly gardener with weathered hands carefully pruning heirloom roses"

Details that matter: age, appearance, clothing, materials, what they are doing, how they feel.

### 2. Add Environmental Context

Set the scene with location, time of day, weather, and atmosphere:

- "Victorian greenhouse at dawn, condensation on glass panes"
- "neon-lit Tokyo alley at midnight after rain"

### 3. Specify Style and Medium

Tell the model what *kind* of image to make:

- **Photography**: "documentary photography", "fashion editorial", "macro photography"
- **Art**: "oil painting", "watercolor illustration", "charcoal sketch"
- **Digital**: "concept art", "3D render", "pixel art"
- **Film**: "cinematic still", "IMAX quality", "film noir"

Reference specific artists, movements, or camera gear for stronger direction.

### 4. Describe Lighting

Lighting is the single most important factor for image quality. Describe:

- **Source**: natural window light, studio softbox, neon signs, candlelight
- **Quality**: soft, harsh, diffused, directional, ambient
- **Direction**: side light, backlight, overhead, underlight
- **Temperature**: warm golden hour, cool blue hour, neutral daylight
- **Effect**: lens flare, volumetric light shafts, dramatic shadows

### 5. Control Composition

Guide framing and arrangement:

- **Shot type**: close-up, medium shot, wide shot, bird's-eye view, low angle
- **Focus**: shallow depth of field, everything sharp, focus on eyes
- **Rules**: rule of thirds, leading lines, symmetry, negative space
- **Depth**: foreground/mid-ground/background layering

### 6. Add Color and Effects

Define palette and finishing touches:

- **Palette**: "muted earth tones", "deep teal and coral", "monochrome"
- **Effects**: "film grain", "motion blur", "soft bloom", "bokeh"

Use one or two strong effects. Too many make the image unfocused.

### 7. Enrich with Details

Add supporting elements that make the scene feel lived-in:

- "floating dust particles catching light"
- "wind-blown fabric"
- "steam rising from a coffee cup"
- "reflections on wet pavement"

## What to Avoid

### Negative Prompts

None of the supported models reliably handle negation. Instead of saying what you *don't* want, describe what you *do* want:

| Instead of... | Write... |
| -------------- | ---------- |
| "no people" | "empty", "deserted", "solitary" |
| "without glasses" | "clear, unobstructed eyes" |
| "no modern elements" | "traditional", "historical", "period-accurate" |
| "not dark" | "brightly lit", "sun-drenched" |
| "not blurry" | "sharp focus", "crisp details" |
| "no text" | "clean surfaces", "unmarked", "blank" |

### Vague Quality Words

Words like "beautiful", "nice", "good", "amazing" provide no actionable guidance. Replace with specifics:

- "beautiful sunset" → "vivid orange and magenta sunset with dramatic cloud formations"
- "good lighting" → "soft Rembrandt lighting from a 45-degree key light"

### Conflicting Styles

Do not combine contradictory directives:

- ❌ "photorealistic cartoon watercolor 8-bit pixel art"
- ✅ "anime-style illustration with soft watercolor texture, pastel colors, clean linework"

### Keyword Soup

Write in natural language, not comma-separated tag lists. Models understand prose:

- ❌ "woman, red hair, city, night, neon, cyberpunk, 4K, detailed"
- ✅ "A young woman with bright red hair stands on a rain-slicked rooftop at night, surrounded by holographic neon advertisements in a cyberpunk metropolis"

## Text in Images

When the image should contain readable text:

1. **Put the exact text in quotation marks**: `"OPEN 24 HOURS"`
2. **Describe placement**: `"The text 'SALE' appears in bold red letters across the top"`
3. **Specify style**: `"elegant serif typography"`, `"bold industrial sans-serif"`
4. **Keep text short** — long strings are harder to render accurately
5. **Describe background contrast** so text stays readable

## Iteration Strategy

Strong prompts come from iteration, not perfect first drafts:

1. Start with a simple version (subject + location + style)
2. Generate and observe what the model got right and wrong
3. Adjust **one important detail at a time**
4. Repeat

This isolates cause and effect. Changing everything at once makes it impossible to learn what works.

## Prompt Length Guidelines

| Length | Words | Best For |
| -------- | ------- | ---------- |
| Short | 10-30 | Quick concepts, style exploration |
| Medium | 30-80 | Most scenes, everyday prompting |
| Long | 80-300+ | Complex multi-subject scenes, very directed outputs |

More words do not automatically mean better results. Every word should earn its place.

## Photography Cheat Sheet

### Camera & Lens Terms

| Term | Effect |
| ------ | -------- |
| f/1.4 – f/2.8 | Blurry background (shallow depth of field) |
| f/8 – f/16 | Everything sharp (deep depth of field) |
| 24mm | Wide angle — shows more scene |
| 35mm | Natural, documentary perspective |
| 50mm | Eye-level, neutral perspective |
| 85mm | Portrait-ideal, background compression |
| 135mm+ | Telephoto — strong compression |
| Macro lens | Extreme close-up detail |
| Anamorphic lens | Widescreen cinematic look with oval bokeh |

### Lighting Terms

| Term | Effect |
| ------ | -------- |
| Golden hour | Warm, soft, flattering light |
| Blue hour | Cool, moody twilight |
| Overcast | Flat, even, shadow-free |
| Rembrandt lighting | Dramatic triangle of light on face |
| Split lighting | Half-face illuminated, high contrast |
| Chiaroscuro | Strong light/shadow drama |
| Backlit / rim light | Subject glowing at edges |
| Practical lighting | Visible light sources in scene |
| Diffused light | Soft, wrap-around, minimal shadows |

### Composition Terms

| Technique | Example Phrase |
| ----------- | ---------------- |
| Rule of thirds | "composed using rule of thirds" |
| Leading lines | "diagonal lines leading to main entrance" |
| Foreground/background | "strong foreground boulder, background mountains" |
| Low angle | "low angle worm's eye view, dramatic diagonal lines" |
| High angle | "bird's eye view, geometric patterns" |
| Dutch angle | "dutch angle, psychological tension" |
| Symmetrical | "perfectly symmetrical composition" |
| Negative space | "minimalist composition with generous negative space" |

## Style Keywords Reference

| Category | Keywords |
| ---------- | ---------- |
| Photographic | "shot on Kodak Portra 400", "35mm film", "Sony A7IV", "Hasselblad X2D" |
| Cinematic | "cinematic", "anamorphic lens flare", "teal and orange color grading", "film noir" |
| Artistic | "oil painting", "watercolor", "pencil sketch", "impasto", "Art Nouveau", "Bauhaus" |
| Digital art | "concept art", "matte painting", "octane render", "unreal engine", "stylized 3D" |
| Illustration | "flat design", "vector illustration", "comic art", "anime style", "graphic novel" |
| Vintage | "80s vintage photo", "2000s digicam", "VHS aesthetic", "polaroid", "sepia tone" |
