# Krea 2 and Krea 3 Prompting Guide

Applies to: **Krea 2** (Medium, Large, Turbo; text-to-image, released 2026-06-22, Turbo and RAW have open
weights) and **Krea 3** (hosted only, released 2026-10-15; instruction-following image editing plus
text-to-image). Krea 1 and community "Krea 2 Edit" LoRAs are out of scope.

Sources (checked 2026-10-22):

- <https://www.krea.ai/docs/developers/krea-2/overview> (and `style-transfer`, `moodboards`, `generative-sliders`)
- <https://www.krea.ai/docs/user-guide/features/krea-2> and `krea-2-turbo`
- <https://github.com/krea-ai/krea-2> (`docs/prompting.md`, `docs/expansion.txt`, local inference settings)
- <https://www.krea.ai/blog/krea-2-deep-dive-walkthrough> (style references, moodboards)
- <https://www.krea.ai/docs/developers/krea-3/overview> (parameters, thinking modes, regional edits, prompting)
- <https://www.krea.ai/blog/introducing-krea-3> and <https://www.krea.ai/krea-3> (prompt pattern, examples)
- <https://docs.comfy.org/tutorials/partner-nodes/krea/krea-3> (ComfyUI Partner Node) and
  <https://docs.comfy.org/tutorials/image/krea/krea-2> (local Krea 2, style LoRAs)

## Which Krea

| Need | Model |
| ---- | ----- |
| A new image whose look matters most: illustration, painting, raw film looks, fashion, worlds | Krea 2 |
| A look carried from style reference images or a moodboard, with weighted strength | Krea 2 |
| Krea's own style LoRAs, or a local run on open weights | Krea 2 (Turbo locally) |
| Editing input images: product into a scene, recolor, swap, relight, sketch to photo | Krea 3 |
| Keeping a product, label, logo, or character identical across new images | Krea 3 |

**Krea 2 cannot edit images.** Its image inputs are style references only: they lend a look, never
content. When the user wants to keep or change something in an image, use Krea 3.

**Krea 3 has no local weights.** In ComfyUI it runs as a Partner Node that calls Krea's servers.

## Krea 2

### Variants

Put the variant first on the `Settings:` line of every Krea 2 block (`Settings: Krea 2 Large`).

| Variant | Pick for |
| ------- | -------- |
| Krea 2 Medium | Default. Illustration, anime, painting, graphic and expressive styles; stable output |
| Krea 2 Large | Photorealism and raw looks: grain, motion blur, low dynamic range, gritty texture |
| Krea 2 Turbo | Fast drafts and many directions; the open-weights checkpoint for local runs |

### Text to Image

Write **one cohesive natural-language paragraph**. Krea says long, detailed prompts give the best results;
its own example captions run 40-120 words.

1. **Medium and aesthetic early**: "A minimalist flat-color illustration", "heavily blurred lo-fi film
   still". Krea 2 does not default to a polished look, so name the finish you want: grain, paper texture,
   chromatic aberration, studio gloss.
2. **Subjects with their own attributes**: group each subject with its clothing, pose, and action.
3. **Materials and textures** rather than bare color words: "matte vinyl", "unglazed ceramic", "heavy ink
   texture on off-white paper".
4. **Camera and composition**: shot type, angle, lens feel, depth of field, where things sit.
5. **Light and palette** last, specific to source and direction.

Quote text that must appear: `hand-lettered sans-serif typography reading "run wild"`. Keep it to short
headlines and labels.

Krea's own example (Turbo, 2K):

```text
A minimalist flat-color illustration of a person wading through expansive shallow ocean waves beneath a
pale peach sky. The dark-skinned figure, wearing an orange swim cap, light blue top, and bright green
shorts, steps carefully through knee-deep water. The ocean is rendered in muted mint green with delicate,
thin black linework detailing the continuous ripples and gentle whitecaps. Soft pinkish-peach reflections
echo the sky on the water's surface. A dark, jagged rock rests in the lower left foreground near a pale
grey shoreline. The horizon features a solid purplish-blue landmass and a stylized, layered yellow and blue
cloud. The high-angle wide perspective emphasizes the vast negative space of the water, utilizing a clean
ligne claire drawing aesthetic with a subtle paper texture.
```

### Style References and Moodboards

When the user supplies a style reference or a moodboard, **the reference carries the look and the prompt
carries the content**: subject, action, arrangement, camera, and light. Krea's own style-transfer
examples use bare prompts such as "a polar bear" and "a cat jumping sideways".

- Leave medium, palette, texture, and art-style words out of the prompt; they compete with the reference.
- The reference is a separate input. The prompt never mentions it ("the attached image", "image 1").
- Vary framing, pose, and light across variations, and vary the strength on the `Settings:` line.

| Control | Settings line | Range and starting point |
| ------- | ------------- | ------------------------ |
| Style reference | `style reference strength 0.6` | -2 to 2. 0.3-0.5 subtle, ~0.6 balanced, 0.8-1.0 reference dominates, negative pushes away. Up to 4 in the app, each with its own strength |
| Moodboard | `moodboard strength 0.35` | -0.5 to 1.5, one per request, built in the Krea app first |

### Other Controls

- **Aspect ratios (hosted)**: `1:1`, `4:3`, `3:2`, `16:9`, `2.35:1`, `4:5`, `2:3`, `9:16`, all at 1K.
  Use `4:5` or `2:3` instead of `3:4`, `2.35:1` instead of `21:9`, and `4:3` instead of `5:4`.
- **Creativity**: leave it at its default. The prompt you write is complete.
- **Generative Sliders** (-100 to 100, 0 neutral). Recommend one only when the brief clearly asks for it:
  `complexity -60` for clean icons and editorial illustration; `intensity 60, movement 30` for cinematic
  fashion or character work.
- **Seed**: the same seed and prompt reproduce the image.
- **No negative prompt.** The API has no field, and Turbo runs without guidance. Phrase every constraint
  positively.
- **Krea style LoRAs**: when the user names one, start the prompt with its trigger phrase and add
  `Settings: LoRA <name>, strength 1.0`.

| LoRA | Trigger phrase |
| ---- | -------------- |
| krea2_darkbrush | monochrome ink wash style |
| krea2_dotmatrix | monochrome stippling style |
| krea2_kidsdrawing | naive expressive sketch style |
| krea2_neondrip | textured abstract style |
| krea2_rainywindow | rainy window style |
| krea2_retroanime | purple retro anime style |
| krea2_softwatercolor | art deco watercolor style |
| krea2_sunsetblur | ethereal motion blur style |
| krea2_vintagetarot | vintage tarot style |

### Running Locally

Use **Krea 2 Turbo** (12B, 8 steps, CFG 0, timestep shift `mu` 1.15). It renders from 1K to 2K at any
width and height (multiples of 16), so any ratio works, including `21:9`: recommend the ratio only and
skip a size Settings line. Krea 2 RAW (52 steps, CFG 3.5) is the base checkpoint for LoRA training, not
for everyday generation. Locally, Krea 2 still only does text-to-image.

## Krea 3

### Request Basics

- One endpoint for both jobs. A prompt with no images is text-to-image; add up to 8 images and the prompt
  becomes an instruction.
- **Put the base image first.** Refer to images by number and content: "the sneaker from image 2", "the
  room in image 1". In the ComfyUI Partner Node, write `@Image1`, `@Image2` in connection order.
- With 5 or more images, each is downscaled to 1536 px on its longest side. Recommend 4 or fewer when
  small text, logos, or faces must hold.

### Edit Instructions

Pick the shape from what the edit keeps:

**A local change** (one object, color, material, piece of text, an addition or removal): lead with the
change, scope it with "only", add only the details that help execute it, and **close with one preservation
sentence** that names what matters. Unlike FLUX 3, do not list every element that stays.

```text
Change the mug to red, keeping everything else the same.
Remove only the woman in the red coat. Keep the shop window and its reflections as they are.
```

Recommend `Settings: regional_edit` for these (`precise_edit` in ComfyUI). It redraws only what changes
and keeps the rest pixel-exact, so edits can be chained on the latest output.

**A kept subject in a new image** (product into a campaign scene, character in a new place, sketch or
blockout to a finished photo): **start with what stays**, naming what must not drift (label, logo, face),
then describe the new scene like a photographer: setting, light, camera. Say what each image is for.

```text
Keep the perfume bottle from image 1 exactly as it is, including the gold label and the engraved logo.
Place it on wet black volcanic rock at the edge of a tide pool at dawn, low soft light from behind, a
faint mist over the water, shot at eye level with a 100mm lens and shallow depth of field.
```

Krea's own examples:

- `Replace only the seating in image 1 with the sofa, chairs and table from images 2 to 4. Keep the rug, the room and the reading woman.`
- `Turn the coloured-pencil terrace in image 1 into a photograph from the same viewpoint, keeping the railing, chairs, awning and plants where they are drawn.`
- `Relight the low-angle gas-station plate in image 1 for night, keeping the camera, the action and both people.`
- `Re-skin the roadside billboard in image 1 for the coffee range in image 2.`

Global edits (restyle, relight, season, reframe, combining several images into a new scene) re-render the
whole frame: leave `regional_edit` off.

**Exact values:**

- **Color**: a hex code on the object matches exactly: "Make the sofa #2F5D46". In layouts with a lot of
  printed text (UI mockups, posters), a hex code can print as visible text: there, name the color in
  words, or attach a palette swatch image and say which color goes where.
- **Text**: quote the new words and name the element they replace: `Change the poster title to "NIGHT
  SHIFT" in the same typeface, color and position.` Krea 3 also localizes: "Translate the title into
  Japanese, keeping the layout."
- **Style**: Krea 3 has no weighted style references. Attach the style image as a numbered reference and
  say what to take from it: "in the palette and brushwork of image 3".

### Text to Image

Write a detailed caption of one to four sentences: subject, setting, light, framing, and any quoted text
with its placement and type style. The same craft and lighting rules as other models apply.

### Settings to Recommend

- **Aspect ratio**: `1:1`, `4:5`, `3:4`, `2:3`, `9:16`, `5:4`, `4:3`, `3:2`, `16:9`, `21:9`. Use `auto`
  for edits; it follows image 1.
- **Resolution**: 1K by default. Recommend `resolution 2K` for small text, logos, product detail, and
  final deliverables.
- **Thinking mode**: `fast` is the default. Recommend `thinking_mode high` for three or more images, edits
  with several steps, or when a `fast` result missed. `thinking_mode ultra` (Max plan, always 2K, needs an
  image, takes minutes, no regional edit) only when the user asks for the best possible final.
- **Seed** does not reproduce an image; compare several runs before deciding a change failed.
- **Negative prompt** field exists; leave it empty and phrase constraints positively.
- No LoRAs and no weighted style references in the API yet.
