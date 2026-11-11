"""Generate MAH DailyDesk's matching Windows ICO and PNG from vector-like shapes.

No prebuilt binary assets are required in source control. Pillow is needed only
for the build step, not when launching the regular Python application.
"""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
OUT.mkdir(parents=True, exist_ok=True)
S = 1024
im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
# Shadow and rich midnight background.
d.rounded_rectangle((49, 62, 978, 994), radius=236, fill=(1, 4, 15, 82))
d.rounded_rectangle((39, 35, 985, 980), radius=228, fill=(12, 17, 39, 255))
# Deep inner field and faint top-right gloss.
d.rounded_rectangle((80, 76, 945, 940), radius=192, outline=(114, 103, 212, 80), width=8)
# Soft corner highlight with alpha compositing (avoid covering the logo).
glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
ImageDraw.Draw(glow).ellipse((570, 40, 970, 395), fill=(85, 76, 179, 32))
im = Image.alpha_composite(im, glow)
d = ImageDraw.Draw(im)
# Signature violet / cyan slanted M as 3 connected ribbons.
purple = (178, 137, 255, 255)
cyan = (102, 234, 245, 255)
mid = (139, 150, 252, 255)
d.polygon([(190, 722), (190, 300), (302, 300), (482, 518), (482, 702), (298, 476), (298, 722)], fill=purple)
d.polygon([(386, 425), (486, 531), (659, 306), (782, 306), (552, 629), (552, 719), (441, 719), (441, 530)], fill=mid)
d.polygon([(655, 306), (781, 306), (781, 722), (655, 722)], fill=cyan)
# Tiny star/daily spark mark on upper right.
d.ellipse((769, 181, 806, 218), fill=cyan)
# Keep alpha clean and export widely usable sizes.
im.save(OUT / "MAH-DailyDesk.png", optimize=True)
im.save(OUT / "MAH-DailyDesk.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
print("Created", OUT / "MAH-DailyDesk.ico", "and", OUT / "MAH-DailyDesk.png")