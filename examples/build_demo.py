#!/usr/bin/env python3
"""Build an 18-second silent original demo from the checked-in slide PNGs."""
import argparse
from pathlib import Path
import subprocess
import tempfile

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--output", type=Path, default=Path(__file__).parent / "demo/demo.mp4")
args = p.parse_args()
slides = Path(__file__).resolve().parent / "demo/slides"
if args.output.exists():
    p.exit(1, "Output exists; choose a new --output path.\n")
with tempfile.TemporaryDirectory() as tmp:
    # The list file is beside temporary copies to avoid path quoting ambiguities.
    import shutil
    for i, name in enumerate(["01-transcript", "02-frames", "03-notes"]):
        shutil.copyfile(slides / (name + ".png"), Path(tmp) / f"{i}.png")
    listing = Path(tmp) / "slides.txt"
    listing.write_text("file '0.png'\nduration 6\nfile '1.png'\nduration 6\nfile '2.png'\nduration 6\nfile '2.png'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
                    "-vf", "fps=12,tpad=stop_mode=clone:stop_duration=1", "-frames:v", "216",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", "-n", str(args.output.resolve())], check=True)
print(args.output)
