# FLUX 3 Image Prompting Guide

Applies to: **FLUX 3 Image** and **FLUX 3 Image Klein**, for text-to-image and image-to-image (editing,
restyling, multi-reference compositing). FLUX 3 Video and FLUX 3 Action are out of scope.

Do not confuse **FLUX 3 Image Klein** (5.6B, FLUX 3 generation) with **FLUX.2 Klein 4B** (see `flux-2-klein.md`).

## What Changed From Earlier Flux

- **The prompt carries everything.** There is no `negative_prompt`, `guidance`, `seed`,
  `mode`, mask, or strength field. Bounding boxes, when used, go at the end of the prompt string.
- **One endpoint for generation and editing.** Send only `prompt` for text-to-image. Add 1-10 images in
  `images` and the prompt becomes an instruction for what to do with them.
- **Write the full caption.** Specify positions, light, text, and every detail the user wants to control.
- **FLUX 3 Image Klein** has the same features (text-to-image, editing, multi-reference, boxes) and is
  trained on full detailed captions. Always write a full detailed caption for it.
- **No seed.** Two runs of the same prompt differ. Compare several results before deciding a change failed.
- **Aspect ratio** is a separate field: `21:9`, `2:1`, `16:9`, `3:2`, `7:5`, `4:3`, `5:4`, `1:1`, `4:5`,
  `3:4`, `5:7`, `2:3`, `9:16`, `1:2`, `9:21`, or `auto`. `auto` follows image 1, and with no images it
  gives `1:1`, so always recommend a ratio for non-square text-to-image work.
- **Resolution**: `768sq` for fast drafts, `1k` default, `2k` for print and hero images, `4k` largest.

## Text to Image

### Caption Order

FLUX 3 launch captions follow this order. Use it as a guide, not a formula; skip slots that do not apply.

1. **Medium and style first**: "High-angle black and white photograph with a grainy film texture."
2. **Subjects and where they sit**: "In the right foreground…", "To the left…", "The background…"
3. **Pose and appearance**: "walk in mid-stride towards the right edge, rendered almost as silhouettes"
4. **Small details**: "cars and buses appearing as small dark shapes", "a faint haze"
5. **Light and its effect**: "long, sharp diagonal shadows under harsh, directional lighting"
6. **Color and background**: palette, then what fills the back of the frame

**Only describe what is visible.** Drop "beautiful", "iconic", "masterpiece". Every phrase should name
something you could point to in the frame.

Short caption, minimal control:

```text
Four men in dark suits cross a sunlit rooftop, a busy avenue far below.
```

Detailed caption, which gives control over each element:

```text
High-angle black and white photograph with a grainy film texture. In the right foreground, a brightly lit,
pale, flat rooftop anchors the composition. Four men in dark suits walk in mid-stride towards the right edge
of the building, rendered almost entirely as silhouettes against the stark surface. They cast long, sharp
diagonal shadows under harsh, directional lighting. To the left, a plunging view reveals a deep urban canyon
and a congested city street far below. The street is split by light and shadow, the left side in deep
darkness while the right catches intense sunlight. The background is filled with towering skyscrapers with
repetitive grids of windows, softening into atmospheric perspective.
```

### Make the Frame and Prompt Agree

Give the model content that fills the chosen shape. For `21:9`: "cliffs on one side, turquoise sea on the
other". The same prompt in `9:16` would squeeze both sides into a narrow column.

### Positive Framing

FLUX 3 has no negative prompt field. Describe what fills the space instead:

| Instead of | Write |
| ---------- | ----- |
| "no people" | "empty", "deserted", "solitary" |
| "no colors" | "monochrome", "black and white" |
| "no background clutter" | "plain studio backdrop in one color" |
| "no modern elements" | "traditional", "period-accurate" |
| "not running" | "walking slowly", "standing still" |
| "not many" | "few", "single", "minimal" |

If an unwanted element persists, describe the replacement early in the sentence, add detail so it takes up
the space, and give it context: "a deserted beach at dawn, before the first swimmers arrive".

### Text and Typography

- Put exact words in double quotes, then say **where** they go and **how** they look (type style, size role
  such as headline, subheading, or body copy, color or hex code).
- Write line breaks inside the quote as `\n`: `"you'll do\neverything"`.
- Non-Latin scripts: keep the prompt in English and quote the script directly: `The text reads "東京".`
- Without boxes, give position in words: `Below the scene, bold serif typography reads "…"`.
- Product ads and covers: name the headline, subtext, product view, background, and aesthetic, e.g.
  `product advertisement, "Ultra-strong titanium" headline, small subtext below, close-up of the phone edge,
  dark gradient background, clean minimalist tech aesthetic`.

**Design brief format.** BFL's FLUX 3 poster and design examples use labeled sections. Adapt it for posters,
covers, and type-led artwork:

```text
Create a finished graphic design artwork for an original design.
ART DIRECTION: [genre and type treatment, texture, two or three named colors or hex codes].
ORIGINAL VISUAL: [the central image idea and its scale relative to the type].
EXACT VISIBLE TITLE: "[title]"
EXACT SUPPORTING COPY: "[line one / line two]"
Use the supporting copy as a carefully typeset secondary block; slashes indicate line breaks.
Create a coherent, distinctive layout with readable text and intentional hierarchy. Full-bleed artwork.
Keep important text at least 5 percent from all edges. Use only the supplied visible copy and invent all
visual forms from this description.
```

**Long-copy infographics.** List the copy by layout role: `TITLE:`, `INTRODUCTION:`, `SECTION 1 HEADING:`,
`SECTION 1 BODY:`, …, `BOTTOM TAKEAWAY:`. Precede it with "Reproduce every sentence verbatim. The headings
below describe layout roles and are not extra printed words." End with a `TYPESETTING:` line: complete
paragraphs in readable body type, short line lengths, generous leading, headings clearly larger than body,
diagram lines kept away from prose, all sections fully visible.

BFL's own examples put the ratio in the first line ("a finished 1:1 artwork") and end with "No real brands…"
lists. In this skill, put the ratio on the recommendation line and keep the constraints positive ("use only
the supplied visible copy", "invent all visual forms").

### Structured Prompts

FLUX 3 documents two structures: prose captions and **caption plus box rows**. The JSON scene schema
(`scene`, `subjects`, `style`, `lighting`, `camera`) belongs to FLUX.2 and is not a FLUX 3 format. When
converting a FLUX.2 JSON prompt, flatten it into a medium-first caption. Turn its subjects into box rows
only when exact positions matter.

### Bounding Boxes (Optional Layout Control)

Use boxes only when the user needs exact placement or size, or supplies a layout. Otherwise write positions
in words.

1. Write one caption paragraph. Tag each element with an id in angle brackets: `<silhouette_1>`.
2. Append a space and a JSON array with one row per id. `bbox` is `[top, left, bottom, right]` on a 0-1000
   grid from the top-left corner. `desc` describes the element.

```text
Minimalist graphic illustration featuring a black silhouette of a person <silhouette_1> centered
against a solid, vibrant chartreuse background <background_1>. The figure is captured in a dynamic,
mid-stride running pose, facing the left side of the frame.
[{"id": "background_1", "bbox": [0, 0, 1000, 1000],
  "desc": "A flat field of neon yellow-green with a subtle paper texture and fine, organic grain."},
 {"id": "silhouette_1", "bbox": [150, 150, 850, 850],
  "desc": "A black silhouette of a person in motion, made of dense stippled ink."}]
```

- Boxes guide placement and scale; elements can extend slightly past them.
- The grid stretches with the frame, so recommend the aspect ratio the boxes were designed for.
- Give each line of text its own row and quote the exact words in `desc`: `text reading "Sauna"`.
- Very small boxes often fail to render new elements. Give new elements room.
- Use lowercase ids with a number (`person_1`, `person_2`).

## Image to Image (Editing)

### Request Basics

- `images`: 1-10 references (each at least 256 × 256 px, at most 16 MP). "Image 1" is the first entry.
  Use the same words for an image every time it is mentioned.
- The prompt is an **instruction**, not a scene description: "Change the jacket from red to blue."
- `aspect_ratio: auto` keeps image 1's frame. **Put the base image first.** Set an explicit ratio only when
  the edit should change the frame, and describe what fills the new space.

### Single-Reference Instructions

Write the instruction in three parts:

1. **Name the target so only one thing matches**: by position, size, color, or neighbor.
2. **Say what changes, and into what**: name it as it is now and as it should be.
3. **Name what must stay**: "keep her pose", "keep the lace embroidery white".

When an exact value matters, write the value:

| To get | Write |
| ------ | ----- |
| A target color | A hex code: "change the color of only one bird in the middle to #e01075" |
| Exact words | Quoted text plus placement and style: "Add the words 'Open late' in white sans-serif letters on the shop window" |
| A specific place | A region: "On the lower left path, replace the tiny wolf with a cyberpunk dog" |
| A preserved detail | The detail by name: "keeping all lace embroidery details white and fully visible" |

Edit-type phrasing:

- **Background replacement**: describe the new setting and its lighting so the subject fits in.
- **Style transfer**: say what keeps its shape: "keep the proportions and layout exactly as in the original".
- **Object add / remove / replace**: be specific about what changes and what stays. Removal is an
  instruction, not a negative prompt: "Remove the white car parked on the right. Keep the red car and the
  street unchanged."
- **Color and material**: hex code for color; name the material: "turn the statue into polished silver".
- **Lighting, weather, season**: short and plain: "Change it to night", "Change this to winter".
- **Text editing**: quote the new words, give placement and style: "in handwritten pink marker, diagonally
  across the top photo".
- **Clothing, pose, expression**: name the garment or body part and the new state; name what must persist.

**Several changes at once** — write an edit record:

```text
Modify image 1 by making three replacements. On the lower left path, replace the tiny
anthropomorphic wolf with a cyberpunk dog. On the lower right, replace the fallen frosted bamboo
log with a fallen bamboo leaf made of gold. In the middle of the misty forest, replace the small
dark bird on a branch with a bird made of robot parts. Keep the rest of the scene exactly
unchanged, preserving the dense upper bamboo leaves, the vertical trunks receding into the fog,
the slanting sunbeams, the frozen stream, and the stone lantern.
```

The preserve list names every major element, not only "the rest of the image".

### Multi-Reference Instructions

Give each image a role, name how the pieces relate, and say how they should integrate.

| Role | Supplies | Example phrasing |
| ---- | -------- | ---------------- |
| Subject | A person, animal, or character to keep recognizable | "the woman in image 2" |
| Product | An object whose shape, color, and label must hold | "the bottle from image 3, label facing the camera" |
| Setting | The scene everything goes into | "the kitchen in image 1" |
| Style | Palette, medium, texture, or lighting | "in the style of image 4" |

One image can supply several roles, such as both the material and the background. Patterns from BFL examples:

- Object into scene: "Replace the cartridge from image 1 with the van in image 2, adjust the lighting on the
  van to integrate well within image 1."
- Style transfer: "Turn image 1 into the style of image 2, keeping the temple's shape and layout."
- Material from one image, shape from another: "Take the shape of the knife from image 2 and recreate it
  entirely out of Skittles like in image 1, keeping the full knife silhouette, on the same background as
  image 1."
- Several sources onto one base: "Paint the artwork from images 2, 3, and 4 onto the coins in image 1."
- People compositing: "Place the people from image 1 and image 2 posing together over the background from
  image 3. Match lighting, shadows, scale, and perspective so they look naturally in the same scene."
- Outfit assembly: "Medium shot of a young woman walking down an urban street, wearing the shoes from image
  1, the jeans from image 2, and the knit sweater from image 3. Shallow depth of field, warm strong sunlight."
- Base, object, and style together: "Use image 1 as the base scene. Take the drink from image 3 and place it
  next to the animal in image 1, matching the lighting, scale, and shadows. Render the entire final image in
  the art style of image 2."

Vague to specific:

| Instead of | Write |
| ---------- | ----- |
| "Combine these images" | "Place the couple from image 2 at the table in image 4, with the view from image 1 through the window." |
| "Add the product" | "Put the bottle from image 3 on the counter in image 1, label facing the camera, lit by the window on the left." |
| "Make it better" | "Warm the light to late-afternoon sun and soften the shadows on her face. Keep the background unchanged." |
| "Change the shirt" | "Change the man's grey T-shirt to #c0392b, keeping the print on the front." |

### Edit Box Rows (Optional)

Add rows when several similar objects match, or a change needs an exact position or size. Refer to images
as `<ref_image_0>` (first image), `<ref_image_1>` (second), and tag elements with `<id>` tokens. State each
addition or removal in the instruction **and** in the rows.

| Row | `from` | `src_bbox` | `tgt_bbox` | Effect |
| --- | ------ | ---------- | ---------- | ------ |
| Keep | `"ref_image_0"` | its box | the same box | stays in place |
| Move | `"ref_image_0"` | its box | a new box | moves or resizes |
| New | `null` | `null` | its box | adds, replaces, or recolors with `desc` |
| Remove | `"ref_image_0"` | its box | `null` | removes the element |
| From another image | `"ref_image_1"` | box in image 2 | box in output | places that element |

Box coordinates must be measured on the user's real images. Only write rows when the user supplies
coordinates or a layout. Otherwise use positional wording.

### Iterate With Edits

Generate from a short prompt, then send each result back with one change: "Move the man to a wet
cobblestone street at night. Keep his face, hair, coat, and pose the same." Then "Put a small, worn teddy
bear in the man's hands. Keep everything else the same." Each step shows what one instruction did.
