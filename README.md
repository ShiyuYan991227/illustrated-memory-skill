# Illustrated Memory Skill

**Illustrated Memory** is a reusable workflow that can take **any everyday user-uploaded photograph** and turn it into a consistent hand-painted watercolor / gouache illustrated journal page.

It is designed to work across many kinds of source images, including people, pets, food, streets, buildings, landscapes, travel scenes, interiors, plants, objects, and everyday moments.

**photo → visual understanding → watercolor-style illustration → image-specific English caption → deterministic composition**

The source image content is never hard-coded. The uploaded photograph is always the content source; this repository only locks the **visual style, caption tone, and final layout system**.

## What stays fixed vs. what changes

### Fixed
- watercolor + gouache + colored-pencil picture-book rendering style
- soft matte palette and handmade pigment texture
- rough, irregular painted edges that dissolve into paper
- warm cream paper-texture background with no decorative scrapbook ornaments
- large centered illustration
- untouched source photo placed at the lower-right with slight overlap
- short, observational English caption in muted sage-green handwriting

### Dynamic for every uploaded photo
- subject(s)
- scene and composition
- dominant colors
- lighting and shadow pattern
- atmosphere
- caption wording

The model must never insert a cat, tree, courtyard, green foliage, or any other object merely because it appeared in an example or style reference.

## Core design principle

The **original uploaded photo remains unchanged** in the final layout. Only the main illustration layer is generated / stylized. The final journal page should be assembled deterministically with code so the source photo can be pasted back as its original pixels.

## Visual system

- nostalgic independent picture-book / illustrated-journal feeling
- gouache + transparent watercolor + colored-pencil texture
- visible dry-brush marks and pigment granulation
- natural, muted, matte colors derived from each source photo
- irregular painted edges that dissolve into paper
- warm cream aged-paper texture, with **no decorative scrapbook elements**
- large centered illustration
- untouched source photo lower-right with subtle overlap
- short observational English caption in muted sage-green handwriting

`assets/style-reference.png` is a **style-only** reference. Its depicted subject matter must not influence the content of a new illustration.

## Repository structure

```text
illustrated-memory-skill/
├── SKILL.md
├── README.md
├── assets/
│   └── style-reference.png
├── config/
│   └── style.yaml
├── prompts/
│   ├── caption.md
│   ├── photo-analysis.md
│   └── style-lock.md
├── scripts/
│   └── compose.py
├── tests/
│   └── test_compose.py
└── requirements.txt
```

## How an agent should use it

1. Receive **any user photo** as the source image.
2. Analyze only what is visibly present using `prompts/photo-analysis.md`.
3. Generate one image-specific English caption with `prompts/caption.md`.
4. Style-transfer the source photo using `prompts/style-lock.md`. If the host supports a second image reference, use `assets/style-reference.png` for **rendering style only**, never for scene content.
5. Save the generated illustration layer.
6. Compose the final page using the generated illustration plus the **original uploaded image file**:

```bash
python scripts/compose.py \
  --illustration /path/to/generated-illustration.png \
  --original /path/to/user-uploaded-photo.jpg \
  --caption "<caption generated from this photo>" \
  --font /path/to/Handlee-Regular.ttf \
  --output outputs/final.png
```

## Examples of valid inputs

The same skill can process, for example:

- a portrait in window light
- a dog running on a beach
- a bowl of noodles on a table
- an old building on a rainy street
- mountains seen through a train window
- flowers beside a notebook
- a night market
- a family travel snapshot

The output should preserve the uploaded photo's actual content and composition while translating only its rendering into the locked watercolor illustration system.

## Caption behavior

The caption is generated anew for each photo. It should describe a small visible moment rather than name a fixed subject or repeat a template. For example, depending on the source image, it might focus on light, movement, weather, texture, a gesture, an object, or a quiet environmental detail.

## Font recommendation

For a stable visual identity, render the caption deterministically instead of asking the image model to draw text. Recommended open handwriting fonts:

1. **Handlee** — first choice; casual and light
2. **Kalam** — slightly stronger handwritten character
3. **Caveat** — looser and more expressive

Font files are intentionally not bundled in this repository. Supply a local `.ttf` / `.otf` using `--font`.

## Privacy / GitHub note

Do not commit user source photos by default. Keep them under a gitignored directory such as `private-inputs/`. The bundled style reference exists only to communicate visual rendering style.

## Design lock

If results drift, do **not** rewrite the skill around one successful example photo. Adjust only:

- photo-specific scene understanding
- caption wording
- local color adaptation

Keep the rendering style, rough-edge behavior, paper background, original-photo preservation rule, layout, and caption tone stable. That is what makes images from very different source photos feel like pages from the same illustrated journal.
