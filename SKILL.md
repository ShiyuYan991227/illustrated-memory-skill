---
name: illustrated-memory
description: Transform a user-supplied photo into a nostalgic illustrated journal page with a watercolor-style main illustration, short English caption, and deterministic layout that preserves the original photo unchanged.
metadata:
  short-description: Turn photos into illustrated journal pages
---

# Illustrated Memory

Use this skill when the user wants a photo turned into the Illustrated Memory visual system: a gentle hand-painted picture-book interpretation, a short observational English caption, and a fixed journal-page composition that includes the untouched original photo.

## Required Outcome

Create a final portrait journal page with:

- a warm cream paper-texture background
- a large watercolor/gouache/colored-pencil illustration based on the uploaded photo
- the original photo pasted intact in the lower-right, scaled proportionally
- a short English caption in a muted sage-green handwriting style

The final page should feel quiet, handmade, airy, and consistent across very different source photos.

## Core Constraints

- Treat the original photo as the source of truth. Do not regenerate, repaint, recolor, retouch, crop, extend, or otherwise alter the original-photo layer.
- Apply style conversion only to the generated illustration layer.
- Compose the final page deterministically with `scripts/compose.py` whenever local image composition is available.
- Do not ask the image model to regenerate the entire final poster when a compositor can paste the original photo pixels.
- Keep the background texture-only: no stickers, stamps, tape, decorative flowers, notebook holes, postcards, or scrapbook ornaments.
- Keep the main illustration visually dominant, centered, and organically edged. It should not look like a clean rectangular photo card.
- Write one short, concrete, image-specific English caption. Avoid motivational quotes, generic philosophy, and exaggerated sentimentality.

## Workflow

1. Analyze the source photo using [references/photo-analysis.md](references/photo-analysis.md). Mention only what is visibly supported.
2. Write one caption using [references/caption.md](references/caption.md).
3. Generate the illustration layer from the source photo using [references/style-lock.md](references/style-lock.md).
4. If the image tool supports a separate style reference and `assets/style-reference.png` exists, use it only for rendering style. Never copy its subject matter into the new image.
5. Check the illustration before compositing. Regenerate if the subject, pose, layout, lighting, or major objects drift materially.
6. Compose the final page with:

```bash
python scripts/compose.py \
  --illustration /path/to/generated-illustration.png \
  --original /path/to/user-photo.jpg \
  --caption "A short caption from this specific photo." \
  --output outputs/final.png
```

Pass `--font /path/to/Handlee-Regular.ttf` or another handwriting font when available. If no font is supplied, the script uses a system fallback.

## Quality Check

Before returning the image, confirm that:

- the illustration is the largest visual element
- painted edges are irregular and organic
- the original photo appears in the lower-right and is unchanged aside from proportional scaling
- the original photo slightly overlaps the illustration
- the caption is English, short, and visually balanced
- the page has no decorative scrapbook elements

Return the final composed image. When useful, also keep the intermediate illustration layer and caption text so the user can iterate on them independently.
