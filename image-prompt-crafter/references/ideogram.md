# Ideogram 4.0 and 4.5 Prompting Guide

Applies to: **Ideogram 4.0** (hosted API and open weights `ideogram-oss/ideogram4`) and **Ideogram 4.5**
(hosted only, announced 2026-09-30, adds precise multi-turn editing). Strengths: typography, posters,
layouts, brand palettes, commercial and product imagery with planned copy space.

Sources (checked 2026-10-22):

- <https://github.com/ideogram-oss/ideogram4/blob/main/docs/prompting.md> (official JSON schema)
- <https://ideogram.ai/blog/claude-mcp/> (official 4.0 prompt guide: verbose vs JSON)
- <https://runware.ai/docs/models/ideogram-4-5/guides/prompting> (and `text-and-design`, `reference-editing`)
- <https://fuser.studio/articles/ideogram-4-5-prompt-guide> (tested text and edit behavior)

## Two Prompt Forms

Ideogram 4 was trained only on **structured JSON captions**. Both versions accept two forms, and both are
used as written, so always write the complete prompt:

| Situation | Form |
| --- | --- |
| Scenes, photos, posters, finished briefs | Full natural language |
| Exact placement of text blocks/objects, fixed hex palette | JSON with `bbox` |
| **Ideogram 4 open weights run locally** | **Always JSON.** Plain text fails and trips the safety filter |

Pick the form once per request from this table and write every variation in it. Without a
placement, palette, or open-weights requirement, all variations are natural language.

## Natural-Language Prompts (4.5 and hosted 4.0)

Ideogram 4.5 follows long, specific prompts closely (up to 10,000 characters). Order the details:

1. **Deliverable/format first**: "Commercial product photograph for a wide web banner", "Screen-printed
   poster for a summer night market". The composition follows from it. Name the format in words only
   ("wide web banner", "vertical story"), not ratios; the ratio goes on the separate line.
2. **Subject**, then **setting**.
3. **Composition**: which third the subject sits in, and what fills the rest.
4. **Light**: direction and quality.
5. **Camera** last: lens, height, depth of field.

### Plan copy space

If text will be laid over the image later, say where the subject sits, how much of the frame stays
empty, and what the empty part looks like: "The diffuser sits in the lower third, and the top 40% of the
frame is a calm, plain warm white wall, left empty for a headline."

### Write text like a typesetter

- Describe the piece and scene first (medium, subject, palette, texture).
- Give **each line of text its own sentence**, in reading order: position, relative size, color, then the
  exact words in double quotes. `Headline across the top in tall condensed orange letters: "NIGHT MARKET".`
- End with **"No other text."** (a positive closing constraint, not a negative prompt).
- Type quoted text in the exact case you want printed.
- Keep strings short (headlines, labels, prices, buttons). Typeface descriptions are followed loosely;
  words are followed precisely.
- Pair hex codes with color names and say "strictly limited to" to make a palette a rule.
- Dense layouts (menus, cards, infographics): one block per panel, left-to-right, top-to-bottom.

## JSON Caption Schema (4.0 format, accepted by 4.5)

Formal JSON Schema: `ideogram-caption.schema.json` (same folder). It cannot enforce key order, so follow
each `x-key-order` list. Key order matters (the model was trained on it). Serialize compactly, uppercase `#RRGGBB` colors only.

```json
{
  "high_level_description": "One or two sentences summarizing the whole image.",
  "style_description": {
    "aesthetics": "warm, playful, vibrant",
    "lighting": "bright afternoon sunlight, long soft shadows",
    "photo": "shallow depth of field, eye-level, 85mm lens",
    "medium": "photograph",
    "color_palette": ["#F5C542", "#87CEEB", "#4A4A4A"]
  },
  "compositional_deconstruction": {
    "background": "Environment description.",
    "elements": [
      {"type": "obj", "bbox": [200, 300, 800, 900], "desc": "Detailed subject description."},
      {"type": "text", "bbox": [40, 100, 160, 900], "text": "SUMMER", "desc": "Bold white sans-serif headline.", "color_palette": ["#FFFFFF"]}
    ]
  }
}
```

Rules:

- `compositional_deconstruction` is required, with `background` before `elements`.
  `high_level_description` is optional but strongly recommended. `style_description` is optional.
- `style_description` uses **exactly one** of `photo` or `art_style`:
  - Photo order: `aesthetics`, `lighting`, `photo`, `medium` (`"photograph"`), `color_palette`
  - Non-photo order: `aesthetics`, `lighting`, `medium`, `art_style`, `color_palette`
  - `medium` values: `photograph`, `illustration`, `3d_render`, `painting`, `graphic_design`, etc.
  - `color_palette` optional, last, up to 16 colors. Include background and shadow colors.
- Element key order: `obj` → `type`, `bbox`, `desc`, `color_palette`;
  `text` → `type`, `bbox`, `text`, `desc`, `color_palette`. `bbox` and per-element palette (max 5) optional.
- `bbox` is `[y_min, x_min, y_max, x_max]`, 0-1000, origin top-left. Note y comes first.
- Use `\n` inside `text` for line breaks. One text element per distinct text block.
- No negative fields, no weights, no quality filler.

## Editing (Ideogram 4.5)

4.5 is built for multi-turn edits with minimal drift. Image 1 is the image being edited; up to 4
references (3 when a mask is used) guide it and are never edited.

- Pattern: **name one change, protect the rest.**
  `Change the date line to "Fridays in August · 6–11 pm". Keep everything else exactly the same.`
- Refer to inputs by number and say what to take from each: "the green velvet from image 2. Keep its
  shape and position."
- Replacing text: quote the new text and name the element it replaces, "in the same font, colour and
  position". When new text is longer than the old, recommend a mask covering the whole old block with a margin.
- Settings to recommend: Edit Precision **High** + size Auto for edits you will build on (copies unchanged
  pixels); **Regular** only when a new aspect ratio is needed (full redraw).

## Settings to Recommend

- Quality `low`/`medium`/`high` (`very_low` for edits): draft low, ship high. Same seed does not lock layout
  across tiers.
- Sizes: 1K presets for drafts, 2K presets for delivery; ratios from 3:1 to 1:3.
- No negative prompt field. Transparent backgrounds are listed for 4.0 only.

## Examples

Natural language:

```text
A risograph poster for a jazz night in a basement club, printed in warm red and navy on cream paper. A
double bass and a saxophone overlap in the center as bold two-colour shapes with visible grain and slight
misregistration. Headline across the top in tall condensed red letters: "LATE SET". Below it in small navy
letters: "Thursdays · 9 pm". Along the bottom edge in navy capitals: "The Cellar · Free entry". No other text.
```

Product with copy space:

```text
Commercial product photograph for a wide web banner: a matte sage green insulated water bottle with a
bamboo cap stands on a flat wet granite rock beside a clear mountain stream. The bottle sits in the right
third of the frame, and the left half is calm, out-of-focus pine forest with room for copy. Morning light
from the left, a soft rim light on the bottle, fine water droplets on its surface. Shot on a 100mm lens at
eye level, shallow depth of field.
```
