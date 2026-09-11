---
name: illustrated-memory
description: Turn a user photo into a consistent nostalgic hand-painted journal page: analyze the photo, create a picture-book style interpretation, write a short English caption, and deterministically compose the illustration with the untouched original photo on a textured cream paper background.
---

# Illustrated Memory

Use this skill when the user wants a photo transformed into the established "Illustrated Memory" visual system: a gentle hand-painted picture-book interpretation, a short observational English caption, and a fixed journal-page composition that also preserves the original photo unchanged.

## Non-negotiable rules

1. The original photo is source-of-truth. Never regenerate, repaint, recolor, retouch, crop, extend, or otherwise alter it for the final original-photo layer.
2. Style conversion applies only to the generated illustration layer.
3. Final layout must be deterministic whenever local image composition is available. Do not ask the image model to regenerate the entire final poster if a compositor can place the original image as pixels.
4. Background is texture only: warm cream/beige paper with subtle fibers, grain, and faint aging. No stickers, stamps, tape, flowers, notebook holes, postcards, decorative patterns, or scrapbook ornaments.
5. The main illustration sits prominently near the visual center and uses irregular painted edges. It must not look like a clean rectangular photo card or Polaroid.
6. The original photo is placed at the lower-right, kept intact, scaled proportionally, and may overlap the illustration slightly.
7. Caption is short English, observational, gentle, and specific to the visible moment. Avoid motivational quotes and generic philosophy.
8. Caption typography should feel like casual green pencil/watercolor handwriting, not calligraphy and not a polished digital script.

## Workflow

### 1. Analyze the source photo

Extract only what is visually supported:
- main subject(s)
- environment and spatial structure
- lighting direction and distinctive light/shadow pattern
- one small moment worth remembering
- dominant natural colors
- emotional tone

Do not invent objects, weather, time of day, or actions that are not supported by the image.

### 2. Write the caption

Use `prompts/caption.md`.

Generate one caption only. The caption should usually be 7–16 words. Prefer concrete sensory observations: light, shadow, breeze, leaves, movement, animals, streets, or small everyday details.

### 3. Generate the illustration layer

Use the source photo as the content reference and `assets/style-reference.png` as the style reference when the host image tool supports multiple references. If only one reference is supported, prioritize the source photo and apply the style via `prompts/style-lock.md`.

Preserve:
- composition
- subject identity and pose
- spatial relationships
- major objects
- lighting direction
- key visible details

Transform only the rendering style.

### 4. Verify the illustration before compositing

Reject/regenerate if any of the following occur:
- major subject is missing or changed
- subject pose changes substantially
- architecture/layout changes materially
- extra decorative objects appear
- image becomes anime, glossy digital art, photorealistic, or vector-like
- illustration has a clean photo-like rectangular border
- colors become neon/high-saturation

### 5. Compose the final page deterministically

Use `scripts/compose.py` whenever possible.

Recommended layout defaults:
- portrait canvas: 1536 × 2048 (3:4)
- illustration width: 72% of canvas
- illustration centered horizontally, upper-middle vertically
- original width: 28% of canvas
- original lower-right, overlapping illustration by about 4–8% of canvas width
- caption below/left of illustration, avoiding the original-photo layer
- background: generated subtle cream paper texture only

The original layer must be pasted from the original file itself. Never use an image-model reproduction of the original.

### 6. Final quality check

Confirm:
- main illustration is visually dominant and centered
- painted edges are rough/organic, not a sharp card frame
- original photo is present and unchanged
- original slightly overlaps the generated illustration
- caption is English and visually balanced
- no unwanted scrapbook decorations
- page feels airy, quiet, handmade, and consistent with `assets/style-reference.png`

## Output

Return the final composed image. If the host supports it, also keep the intermediate illustration layer and caption text so the user can iterate on either one independently.
