from pathlib import Path
import tempfile
from PIL import Image


def test_assets_exist():
    root = Path(__file__).resolve().parents[1]
    assert (root / "assets" / "style-reference.png").exists()
    assert (root / "prompts" / "style-lock.md").exists()
    assert (root / "scripts" / "compose.py").exists()
