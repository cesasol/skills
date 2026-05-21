---
name: image-prompt-crafter
description: >
  Craft, upsample, and refine text prompts for AI image generation models.
  Use this skill whenever the user wants to create, improve, expand, or translate
  prompts for text-to-image models including Flux (FLUX.1 Dev, FLUX.2 Dev, FLUX.2 Klein),
  Z-Image Turbo, or Ernie Image. Triggers on phrases like "prompt for image generation",
  "make this prompt better", "upsample this prompt", "refine my prompt", "convert this
  prompt for [model]", or any request involving writing or improving AI image prompts.
  Also triggers when the user describes a scene or concept they want to turn into an
  image, even if they don't explicitly say "prompt".
---

# Image Prompt Crafter

Craft, upsample, and refine text prompts for AI image generation. This skill covers
Flux family models (FLUX.1 Dev, FLUX.2 Dev, FLUX.2 Klein), Z-Image Turbo, and Ernie Image.

## Workflow

When the user asks you to craft, upsample, refine, or convert a prompt:

1. **Identify the target model(s)**. Default to the model they mention. If no specific
   model is provided, infer the best supported model for the user's prompt and use it
   without asking a follow-up question. If they want output for multiple models, produce
   one optimized prompt per model.

   Model inference guidelines:
   - Choose **Ernie Image** for prompts with readable text, posters, graphic layouts,
     multi-panel layouts, diagrams, typography, or bilingual/Chinese-language needs.
   - Choose **FLUX.2 Dev** for complex, highly detailed scenes, precise color direction,
     long natural-language prompts, product/editorial work, or when maximum prompt
     control is useful.
   - Choose **FLUX.2 Klein** for local/lightweight workflows only when the user implies
     speed, smaller model use, or very literal prompt following; make the prompt detailed.
   - Choose **FLUX.1 Dev** for general high-quality photographic or cinematic images when
     no FLUX.2-specific benefit is needed.
   - Choose **Z-Image Turbo** for fast iteration, stylized/conceptual images, bilingual
     English/Chinese prompts, or concise 80-250 word prompts with 3-5 core concepts.

2. **Read the relevant reference file(s)** from `references/`:
   - `common-prompting.md` — always read this first
   - `flux-family.md` — for FLUX.1 Dev, FLUX.2 Dev, FLUX.2 Klein
   - `z-image-turbo.md` — for Z-Image Turbo
   - `ernie.md` — for Ernie Image

3. **Determine the task type**:
   - **Craft from scratch**: user describes a concept or scene in plain language
   - **Upsample**: user has a short/basic prompt and wants it expanded with detail
   - **Refine**: user has a prompt and wants to improve it based on feedback or a specific goal
   - **Translate/convert**: user has a prompt for one model and wants it adapted for another

4. **Apply the principles** from the reference files to produce 2-3 prompt variations.
   - Each variation should explore a different angle: different framing, lighting, mood, or detail emphasis
   - All variations must preserve the user's core subject and intent
   - Keep one variation closest to the user's original vision, and branch the others in interesting directions
   - Recommend an aspect ratio for each variation outside the prompt text, based on the
     composition and intended use

5. **Choose recommended aspect ratios** using the visual goal, not arbitrary defaults:
   - `1:1` for icons, album covers, product hero images, centered subjects, and social posts
   - `4:5` or `3:4` for portraits, fashion/editorial shots, posters, and vertical character art
   - `2:3` for print posters, book covers, full-body portraits, and travel-poster formats
   - `16:9` for cinematic landscapes, widescreen scenes, environment concept art, and banners
   - `21:9` for panoramic cinematic vistas and very wide compositions
   - `9:16` for mobile wallpapers, story/reel covers, tall architecture, and vertical scenes
   - `3:2` or `4:3` for natural photography, documentary scenes, and balanced editorial images

## Output Format

Output the prompt variations with a single line description that explains the difference and a recommended aspect ratio.

For each target model, provide 2-3 variations of the prompt. Each variation goes in its own fenced code block using triple backticks.

```[TARGET MODEL]
[First prompt variation]
```

Recommended aspect ratio: [ratio]
[First prompt description]

```[TARGET MODEL]
[Second prompt variation]
```

Recommended aspect ratio: [ratio]
[Second prompt description]

```[TARGET MODEL]
[Third prompt variation - if appropriate]
```

Recommended aspect ratio: [ratio]
[Third prompt description]

Rules for the output:

- No markdown headers (no `#`, no `##`)
- No bold labels like "**Optimized prompt:**"
- No introductory or concluding text

## Important Rules

- **Never include explicit aspect ratio or resolution instructions inside the prompt text**
  like "4:3 aspect ratio", "1024x1024", "16:9", or specific pixel dimensions. The
  recommended aspect ratio must be listed separately after each prompt block. Compositional
  terms like "panoramic view", "portrait orientation", "wide shot", or "vertical composition"
  are fine because they describe framing, not technical output dimensions.

- **Never use negative prompts**. None of the supported models benefit from them. Instead,
  frame constraints positively (e.g., instead of "no people", use "empty landscape").

- **Preserve the user's core intent**. When upsampling or refining, the original subject,
  style, and mood must remain intact. Add detail and precision, do not change the vision.

- **Use natural language**. All supported models understand prose better than keyword
  soup. Write prompts that read like clear image descriptions.

- **Quote text that should appear in the image** using double quotation marks.
  Example: `a neon sign that reads "OPEN 24 HOURS"`.

- **Be specific about lighting** — it has the single greatest impact on output quality
  across all models.

- **Iterate incrementally**. If the user is refining, suggest changing one element at a
  time rather than rewriting everything.

## Common Mistakes and Edge Cases

- If the user asks for an aspect ratio, include it only in the separate recommendation
  line, not inside the prompt block.
- If the prompt contains conflicting styles, pick the dominant style or ask one brief
  clarification question when the conflict changes the core intent.
- If the user provides unsafe, copyrighted-character, or brand-heavy wording, preserve
  the visual intent using generic descriptive language.
- If the requested image includes text, keep the quoted text short and choose Ernie Image
  when no model was specified.

## Quick Model Differentiators

| Model | Prompt Length | Upsampling | Text in Image | Special Notes |
| ------- | -------------- | ------------ | --------------- | --------------- |
| FLUX.1 Dev | Medium-Long | Built-in | Excellent | 12B params, natural language |
| FLUX.2 Dev | Medium-Long | Built-in | Excellent | Up to 32K tokens, HEX colors |
| FLUX.2 Klein | Must be detailed | None | Excellent | 4B params, what-you-write-is-what-you-get |
| Z-Image Turbo | 80-250 words | None | Good bilingual | No negative prompts, 3-5 concepts max |
| Ernie Image | Short-Medium | Built-in Enhancer | Best-in-class | Layout instructions, multi-panel, bilingual |

## Cross-Model Conversion Tips

When converting a prompt from one model to another:

- **To FLUX.2 Klein**: Expand significantly. Klein has no upsampling — every detail must
  be in the prompt. Add `Style: [style]. Mood: [mood].` at the end.

- **To Z-Image Turbo**: Condense to 80-250 words. Prioritize the 3-5 most important visual
  concepts. Remove redundant detail.

- **To Ernie Image**: Shorten if under 50 words (Enhancer will expand). Keep text-in-image
  elements in quotes. Add explicit layout terms if relevant.

- **From Ernie to others**: Expand the enhanced description manually since other models
  lack the built-in enhancer.
