"""Bring Nano Banana outputs to 1080p and mirror the folder structure of original/.

Usage: python3 renderings/finalize.py <raw_dir>
<raw_dir> holds one PNG per original, named like the original (W1_Bad.png, ...).
"""
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parent
ORIGINAL = ROOT / "original"
OUT = ROOT / "fotorealistisch"


def main(raw_dir: Path) -> None:
    missing = []
    for src in sorted(ORIGINAL.rglob("*.jpg")):
        raw = raw_dir / f"{src.stem}.png"
        if not raw.exists():
            missing.append(src.name)
            continue
        w, h = Image.open(src).size
        size = (1440, 1080) if w * 3 == h * 4 else (1920, 1080)
        dest = OUT / src.relative_to(ORIGINAL)
        dest.parent.mkdir(parents=True, exist_ok=True)
        img = Image.open(raw).convert("RGB")
        img = img.resize(size, Image.LANCZOS)
        img.save(dest, "JPEG", quality=92, optimize=True, progressive=True)
        print(f"{dest.relative_to(ROOT)}  {size[0]}x{size[1]}")
    if missing:
        print(f"\nmissing {len(missing)}: {', '.join(missing)}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
