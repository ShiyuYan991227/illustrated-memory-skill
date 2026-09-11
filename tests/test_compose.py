from pathlib import Path
import subprocess
import sys

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]


def test_skill_files_exist():
    assert (ROOT / "SKILL.md").exists()
    assert (ROOT / "agents" / "openai.yaml").exists()
    assert (ROOT / "references" / "style-lock.md").exists()
    assert (ROOT / "references" / "caption.md").exists()
    assert (ROOT / "references" / "photo-analysis.md").exists()
    assert (ROOT / "scripts" / "compose.py").exists()


def test_compose_script_creates_page(tmp_path):
    illustration = tmp_path / "illustration.png"
    original = tmp_path / "original.jpg"
    output = tmp_path / "final.jpg"

    Image.new("RGB", (800, 600), (120, 170, 145)).save(illustration)
    Image.new("RGB", (640, 480), (210, 120, 90)).save(original)

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "compose.py"),
            "--illustration",
            str(illustration),
            "--original",
            str(original),
            "--caption",
            "Late sunlight rests on the quiet table.",
            "--output",
            str(output),
            "--width",
            "768",
            "--height",
            "1024",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert output.exists()
    assert str(output) in result.stdout
    assert Image.open(output).size == (768, 1024)
