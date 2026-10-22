---
name: image-prompt-crafter
description: >
  Use when the user wants to write, expand, refine, or convert a prompt for an AI image
  generation model, including FLUX 3 Image, FLUX 3 Image Klein, FLUX.2 Klein 4B,
  Ideogram 4.0 and 4.5, Krea 2 (Medium, Large, Turbo), Krea 3, and Z-Image Turbo, including
  local ComfyUI workflows; when they need image-to-image edit instructions (edit this photo,
  restyle, put X into Y, combine reference images) or want a look carried over from style
  references or a moodboard; or when they describe a scene, poster, logo, or concept they
  want turned into an image, even if they never say "prompt". Triggers include "prompt for image generation", "make this prompt
  better", "upsample this prompt", and "convert this prompt for [model]".
---

# Image Prompt Crafter

Craft, expand, and refine text prompts for AI image generation and image-to-image editing.
Always write the complete final prompt. Never rely on, mention, or recommend any model-side
prompt rewriting or expansion feature.

## Workflow

1. **Pick the target model(s).** Do not ask a follow-up question about the model. If the
   user wants several models, write one set of variations per model.
2. **Read the references** in `references/`: `common-prompting.md` always, plus the one for
   each target model (see the table below).
3. **Classify the task** and apply its rule:
   - **Craft**: the user describes a concept. Write a full prompt from it.
   - **Expand**: the user has a short prompt. Add detail; keep subject, style, and mood.
   - **Refine**: the user has a prompt and a problem. Variation 1 is their prompt with only
     the fix applied, keeping every untouched sentence word for word. The other variations
     each try a different fix for the same problem.
   - **Convert**: the user has a prompt for another model. Keep its content and apply the
     conversion tips below.
   - **Edit (image-to-image)**: the user has input images. Write an instruction, not a scene
     description. Vary the wording, specificity, and preserve list across variations, never
     the requested change.
4. **Write 2-3 variations.** Variation 1 stays closest to the user's vision; the others
   branch on framing, lighting, mood, or detail emphasis. Every variation keeps the core
   subject and intent.
5. **Recommend an aspect ratio** per variation from the composition and intended use, using
   a ratio the target model accepts (each reference lists its sizes):
   - `1:1` icons, logos, album covers, product hero shots, centered subjects, social posts
   - `4:5` or `3:4` portraits, fashion/editorial, posters, vertical character art
   - `2:3` print posters, book covers, full-body portraits, travel posters
   - `3:2` or `4:3` natural photography, documentary scenes, balanced editorial images
   - `16:9` cinematic landscapes, environment concept art, banners; `21:9` panoramas
   - `9:16` mobile wallpapers, story/reel covers, tall architecture

## Choosing the Model

Take the first rule that matches. Use FLUX 3 Image Klein only when the user names it or rule 6
picks it, FLUX.2 Klein 4B only when the user names it or rule 2 picks it, Krea 2 only when
the user names it or rule 4 picks it, and Ideogram 4.0 and Krea 3 only when the user names
them. "Quoted text" means the exact words that must appear in the image, counted in characters
across all of them. A style reference lends only its look; an input image to edit has content
that stays.

1. The user names a supported model: use it. "FLUX.2 Klein" or "Klein 4B" means FLUX.2 Klein
   4B. "Krea 2 Medium", "Large", or "Turbo" means Krea 2 with that variant. If they name a
   model not in the table below (FLUX.2 Dev, FLUX.1 Dev, FLUX.2 Klein 9B, Krea 1, or any
   other), write for the model rule 2 would pick in a local workflow, otherwise FLUX 3 Image.
   If they name Krea 2 but supply images to edit, write for Krea 3, or FLUX.2 Klein 4B in a
   local workflow. Start variation 1's description line (never the prompt) with
   `Written for <model>; <named model> is not supported.`, or for a Krea 2 edit with
   `Written for <model>; Krea 2 cannot edit images.`
2. The context points to a local workflow (ComfyUI, Diffusers, "on my GPU", offline, their own
   hardware): **Z-Image Turbo**. When they supply or describe input images to edit, use
   **FLUX.2 Klein 4B** instead, because Z-Image Turbo cannot edit images.
3. They want a JSON layout with an exact hex palette, or multi-turn edits of a design they
   are iterating on: **Ideogram 4.5**.
4. They want a new image whose look comes from style references or a moodboard ("match this
   look", "use this as a style reference"): **Krea 2**.
5. They supply or describe input images to edit (edit, restyle, combine references): **FLUX 3 Image**.
6. The image must contain readable text (logos, signs, posters, covers, typography, diagrams,
   infographics, multi-panel layouts) or elements need exact placement:
   - Quick drafts with 100 characters of quoted text or fewer: **Z-Image Turbo**.
   - Quick drafts with more than 100 characters of quoted text: **FLUX 3 Image Klein**.
   - Everything else: **FLUX 3 Image**.
7. They want speed: quick drafts, many variations, fast iteration, a lightweight model. Also
   stylized or conceptual art: **Z-Image Turbo**.
8. Anything else (photographic, cinematic, product, editorial, or complex scenes):
   **FLUX 3 Image**.

| Model | Fence tag | Reference | Prompt length | Notes |
| ----- | --------- | --------- | ------------- | ----- |
| FLUX 3 Image | `flux-3-image` | `flux-3.md` | Short to long captions | Best text; edits with 1-10 images; optional boxes; no seed |
| FLUX 3 Image Klein | `flux-3-image-klein` | `flux-3.md` | Full captions | 5.6B open weights, same features as FLUX 3 Image |
| FLUX.2 Klein 4B | `flux-2-klein` | `flux-2-klein.md` | A full paragraph | Local edits with up to 4 refs; fixed seed; ends with Style/Mood |
| Ideogram 4.0 | `ideogram-4` | `ideogram.md` | Full prose or JSON | Open weights need JSON; exact-case text, hex, boxes |
| Ideogram 4.5 | `ideogram-4-5` | `ideogram.md` | Up to 10K chars or JSON | Precise multi-turn edits, masks, up to 4 references |
| Krea 2 | `krea-2` | `krea.md` | One full paragraph | Text-to-image only; weighted style refs, moodboards, LoRAs; Turbo runs locally |
| Krea 3 | `krea-3` | `krea.md` | Short instructions or captions | Hosted; fast edits with up to 8 refs; native 2K; regional edits |
| Z-Image Turbo | `z-image-turbo` | `z-image-turbo.md` | 80-250 words | Fast; first local choice; no editing; 3-5 core concepts |

## Output Format

The response contains only variation blocks. One block is, in order:

1. A fenced code block holding the prompt, tagged with the model's fence tag from the table.
2. `Recommended aspect ratio: <ratio>` (`auto` for edits that keep image 1's frame).
3. For edits: `Image order: image 1 = <role> (base), image 2 = <role>`.
4. Only if the result depends on a setting other than aspect ratio (model variant, quality
   tier, edit precision, custom size, fixed seed, LoRA, reference strength, thinking mode):
   `Settings: <setting>`.
5. One sentence saying how this variation differs. For Refine, say what changed from the
   user's prompt and why it fixes the problem.

Example block:

```z-image-turbo
<prompt text>
```

Recommended aspect ratio: 21:9
Settings: custom image_size, e.g. 1344x576
Closest to your idea: the whole ridge lit end to end under a wide, open sky.

With several models, give all of one model's blocks before the next model's. Use no
headers, no bold labels, and no text before the first block or after the last.

## Rules

- **Keep ratios and resolutions out of the prompt.** No "16:9", "1024x1024", or pixel sizes
  in the prompt text; they go on the recommendation lines. Framing words such as
  "panoramic view" or "vertical composition" are fine.
- **Phrase every constraint positively.** No negative prompts: "empty landscape", not "no
  people". In edits, "Remove the white car on the right" is an instruction, not a negative
  prompt.
- **Write natural-language prose,** not keyword lists, except the JSON forms the references
  document.
- **Quote text that should appear in the image** in double quotes:
  `a neon sign that reads "OPEN 24 HOURS"`.
- **Describe the lighting specifically.** It has the greatest single effect on quality.
- **Follow an explicit user length request** ("keep it short") over the model's usual range.

## Edge Cases

- Conflicting styles: keep the dominant one. If the conflict changes the core intent, reply
  with one short clarification question instead of prompts.
- Unsafe, copyrighted-character, or brand-heavy wording: keep the visual intent with generic
  descriptive language.
- Text with no model named: rule 6 picks the model by draft vs final and quoted-text length.
  Keep quoted text short unless the user supplies long verbatim copy.
- An edit described but no image attached: write the instruction for the images they
  described and give the image order.
- Never invent bounding-box coordinates for existing images. Use positional wording unless
  the user supplies coordinates or a layout.

## Cross-Model Conversion Tips

- **To FLUX 3 Image**: Reorder to medium and style first, then subjects and positions, light,
  color, and background. Drop quality filler and weight syntax. Flatten JSON prompts (such as
  FLUX.2's `scene`/`subjects` format) into a caption. Refer to inputs as "image 1", "image 2" by position.
- **To Ideogram**: Lead with the deliverable, then subject, setting, composition, light,
  camera. Give each text line its own sentence and end with "No other text." For exact
  layout, use the JSON caption schema with strict key order and `[y_min, x_min, y_max, x_max]`
  boxes.
- **To FLUX.2 Klein 4B**: Expand to a full descriptive paragraph; Klein receives only what you
  write. Turn box rows into positional wording. End with `Style: [style]. Mood: [mood].`
- **To Krea 2**: Write one full paragraph that names the medium and finish, with material and
  texture words. Turn box rows into positional wording. With a style reference, keep only the
  content and move the look to the reference. An edit prompt cannot convert; use Krea 3.
- **To Krea 3**: Write edits as one instruction led by the change, or by what stays when the
  subject moves into a new scene. Shrink preserve lists to one sentence naming what matters.
  Refer to inputs as "image 1" plus what they show; turn edit box rows into positional wording.
- **To Z-Image Turbo**: Condense to 80-250 words around the 3-5 most important visual
  concepts.
