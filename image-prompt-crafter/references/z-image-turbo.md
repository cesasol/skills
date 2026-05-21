# Z-Image Turbo Prompting Guide

## Overview

Z-Image Turbo is a 6 billion parameter model built on the Scalable Single-Stream DiT (S3-DiT) architecture. It generates high-quality images in under a second. It is a few-step distilled model that
does **not** use classifier-free guidance at inference, which means **negative prompts are not supported**. All constraints must be placed in the positive prompt.

## Key Characteristics

- **No negative prompts** — all guidance must be in the positive prompt
- **Optimal prompt length: 80-250 words** — extremely long prompts (300+ words) may truncate or degrade coherence
- **Limit to 3-5 key visual concepts** per prompt — the model processes structured descriptions best when focused
- **Strong bilingual support** for English and Chinese text rendering
- **Excellent at interpreting detailed descriptions** across photorealistic and artistic styles

## Prompt Structure

Effective prompts follow a hierarchical structure with six key categories:

| Component | Purpose | Example |
| ----------- | --------- | --------- |
| Subject Specification | Defines primary content | "An elderly gardener with weathered hands" |
| Environmental Context | Establishes setting | "Victorian garden at morning, dappled sunlight" |
| Visual Style | Guides aesthetic treatment | "Shot on Leica M6 with Kodak Portra 400 film grain" |
| Composition | Controls framing and focus | "Ultra-wide landscape, rule of thirds" |
| Technical Parameters | Optimizes generation | `num_inference_steps: 8`, `acceleration: "high"` |
| Quality/Detail | Finishing touches | "sharp focus", "crystal-clear detail" |

## Subject Specification

Start with a clearly defined subject. Replace vague descriptors with concrete details:

- **Instead of**: "a person in a garden"
- **Use**: "an elderly gardener with weathered hands carefully pruning roses in a Victorian garden"

## Environmental Context

The setting influences how Z-Image Turbo renders your scene:

- **Location**: Indoor, outdoor, or specific setting
- **Time of day**: Morning light, sunset, or night
- **Weather/atmosphere**: Clear, foggy, rainy, or mysterious
- **Background elements**: What surrounds your main subject

Example: "The background features ancient stone walls covered in moss, with dappled morning sunlight filtering through a canopy of oak trees."

## Visual Style Directives

Z-Image Turbo responds effectively to style guidance:

- **Artistic references**: Painting, illustration, or photography
- **Technical specifications**: Camera type, lens, film stock
- **Lighting conditions**: Soft, harsh, directional, or ambient
- **Color palette**: Vibrant, muted, monochromatic, or specific colors

Example: "Shot on a Leica M6 with Kodak Portra 400 film grain aesthetic, using natural window light creating soft shadows."

## Compositional Control

Direct the visual hierarchy and arrangement:

- **Close-up, wide shot, or from below**
- **Focus directives**: shallow depth of field, specific elements in focus
- **Composition rules**: rule of thirds, leading lines, symmetry

Example: "An ultra-wide landscape shot with a dramatic foreground rock formation drawing the eye toward distant mountains, following the rule of thirds."

## No Negative Prompts Strategy

Since Z-Image Turbo doesn't support negative prompts, include all constraints in the positive prompt:

- Instead of a negative prompt saying "no blur", include **"sharp focus"** or **"crisp details"** in your main prompt
- Instead of "no people", use **"empty landscape"** or **"deserted"**
- Instead of "no text", use **"clean unmarked surfaces"**

## Common Mistakes to Avoid

1. **Prompt overloading** — Focus on the most important 3-5 elements rather than cramming every possible detail
2. **Contradictory instructions** — Avoid conflicting directives like "photorealistic cartoon style"
3. **Vague descriptions** — Terms like "beautiful," "nice," or "good" provide little guidance. Be specific
4. **Missing style guidance** — Without style direction, the model will make its own interpretations
5. **Excessive length** — Stay within 80-250 words for optimal coherence

## Prompt Templates

### Photorealistic Portraits

> "A [age/ethnicity] [gender] with [distinctive features] wearing [clothing/accessories], [expression/emotion], [pose/action]. The lighting is [lighting description]. Shot on [camera] with [lens] in
> [setting/environment], [time of day]."

Filled example:
> "A 65-year-old Asian woman with silver hair and gentle wrinkles wearing a hand-knitted cardigan, contemplative expression, reading by a window. The lighting is soft natural afternoon light. Shot on
> Canon 5D with 85mm lens in a cozy library, golden hour."

### Conceptual Art

> "A [adjective] [concept] represented as [visual metaphor], featuring [key visual elements]. The style is inspired by [artist/movement], with a [color palette] color palette."

### Product Photography

> "A professional product photo of [product] on a [background] background. [Product details/features] are clearly visible. Lit with [lighting setup] at [angle]."

## Parameter Optimization (API)

| Parameter | Type | Range/Options | Default | When to Use |
| ----------- | ------ | --------------- | --------- | ------------- |
| `num_inference_steps` | integer | 1-30 | 8 | 4 for speed, 8 balanced, 12+ for maximum quality |
| `num_images` | integer | 1-4 | 1 | Generate multiple variants per request |
| `seed` | integer | Any integer | random | Set specific value for reproducible results |
| `image_size` | string | See below | `landscape_4_3` | Choose based on output requirements |
| `acceleration` | string | `none`, `regular`, `high` | `none` | `high` for sub-second generation |

**Image size options**: `square_hd`, `square`, `portrait_4_3`, `portrait_16_9`, `landscape_4_3`, `landscape_16_9`

## LoRA Customization

The LoRA version supports up to 3 LoRAs simultaneously. Scale parameter:

- **0.0-0.5**: Subtle style influence
- **0.7-1.0**: Moderate to strong influence (recommended starting point)
- **1.0+**: Very strong influence, may overpower base model

**Prompt expansion feature**: The LoRA endpoint supports `enable_prompt_expansion`, which enhances shorter prompts. Most beneficial for prompts under 50 words.
