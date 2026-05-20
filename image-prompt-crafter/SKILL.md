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

1. **Identify the target model(s)**. Ask if unclear. Default to the model they mention.
   If they want output for multiple models, produce one optimized prompt per model.

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

5. **Output ONLY the prompt variations** in fenced code blocks. No additional text.

## Output Format

Output ONLY the prompt variations. No titles, no headers, no "Key choices", no explanations.

For each target model, provide 2-3 variations of the prompt. Each variation goes in its own fenced code block using triple backticks.

```
[First prompt variation]
```

```
[Second prompt variation]
```

```
[Third prompt variation - if appropriate]
```

Rules for the output:
- No markdown headers (no `#`, no `##`)
- No bold labels like "**Optimized prompt:**"
- No bullet lists of "Key choices"
- No introductory or concluding text
- Just the code blocks containing the prompt text, one per variation

## Important Rules

- **Never include explicit aspect ratio or resolution instructions** like "4:3 aspect ratio",
  "1024x1024", "16:9", or specific pixel dimensions in the prompt text. The user controls
  image size separately. Compositional terms like "panoramic view", "portrait orientation",
  "wide shot", or "vertical composition" are fine because they describe framing, not technical
  output dimensions.

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

## Quick Model Differentiators

| Model | Prompt Length | Upsampling | Text in Image | Special Notes |
|-------|--------------|------------|---------------|---------------|
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
