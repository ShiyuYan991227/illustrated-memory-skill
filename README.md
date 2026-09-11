# Illustrated Memory Skill

Illustrated Memory is a reusable Agent/Codex Skill that turns a user-supplied photo into a consistent hand-painted illustrated journal page.

It keeps the uploaded photo as the content source, generates a watercolor/gouache-style illustration from it, writes a short English caption, and composes the final page with the original photo pasted back unchanged.

## What It Does

- Analyzes only the visible contents of the source photo
- Generates one image-specific English caption
- Guides an image model to create a soft watercolor, gouache, and colored-pencil illustration
- Uses `scripts/compose.py` to assemble the final page deterministically
- Preserves the original uploaded photo as real pixels in the lower-right of the final image

## Install

Copy this skill folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R illustrated-memory-skill ~/.codex/skills/illustrated-memory
```

Install the Python dependencies used by the compositor:

```bash
python -m pip install -r ~/.codex/skills/illustrated-memory/requirements.txt
```

Restart Codex if your environment only scans skills at startup.

## Use

Ask for the skill by name, for example:

```text
Use $illustrated-memory on this photo.
```

The agent should:

1. Analyze the uploaded image with `references/photo-analysis.md`.
2. Write a short caption with `references/caption.md`.
3. Generate the illustration using `references/style-lock.md`.
4. Run `scripts/compose.py` with the generated illustration and the untouched original photo.

Manual compositor example:

```bash
python scripts/compose.py \
  --illustration /path/to/generated-illustration.png \
  --original /path/to/original-photo.jpg \
  --caption "Late sunlight rests on the quiet table." \
  --output outputs/final.png
```

Optional:

```bash
python scripts/compose.py \
  --illustration /path/to/generated-illustration.png \
  --original /path/to/original-photo.jpg \
  --caption "Late sunlight rests on the quiet table." \
  --font /path/to/Handlee-Regular.ttf \
  --output outputs/final.png
```

## Structure

```text
illustrated-memory/
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
|-- config/
|   `-- style.yaml
|-- references/
|   |-- caption.md
|   |-- photo-analysis.md
|   `-- style-lock.md
|-- scripts/
|   `-- compose.py
|-- tests/
|   `-- test_compose.py
`-- requirements.txt
```

## Notes

The `assets/` folder is available for an optional `style-reference.png`. If you add one, the agent should use it only as a style reference and never copy its subject matter into new illustrations.

Do not commit user photos by default. Keep private inputs under a gitignored folder such as `private-inputs/`.
