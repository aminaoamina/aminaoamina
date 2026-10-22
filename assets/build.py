"""Generate the profile hero: the animated background GIF with a name card drawn on every frame,
saved as an animated WebP (smaller than a GIF for the same look).

The source GIF (assets/source/background.gif) is not committed; only hero.webp is.
Edit the text below or replace the source, then run:  python assets/build.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageSequence

OUT = Path(__file__).resolve().parent
SOURCE = OUT / "source" / "background.gif"
FONTS = Path("C:/Windows/Fonts")

KICKER = "AI × CYBERSECURITY"
NAME = "Amina Bayoudh"
SUBTITLE = ["Network Infrastructure & Data Security", "Engineering Student · AI Enthusiast"]
STATUS = "Open to a 6-month PFE internship · from January 2027"

W, H = 860, 402       # output size; the source is cropped to this shape and scaled up
FOCUS_Y = 0.5         # which part of the source stays visible, from 0 (top) to 1 (bottom)
FRAME_STEP = 1        # keep 1 frame in N; raise it if the file gets too big
QUALITY = 70
MAX_BYTES = 5_000_000

ACCENT = (255, 180, 84)


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def card_layer():
    """Transparent layer with the dark name card and its text."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cw, ch = 500, 236
    x, y = 34, (H - ch) // 2
    d.rounded_rectangle((x, y, x + cw, y + ch), radius=12, fill=(5, 7, 13, 190), outline=(255, 255, 255, 45))

    tx = x + 28
    d.text((tx, y + 26), KICKER, font=font("consola.ttf", 13), fill=(154, 164, 178))
    d.text((tx - 2, y + 46), NAME, font=font("segoeuib.ttf", 48), fill=(255, 255, 255))
    for i, line in enumerate(SUBTITLE):
        d.text((tx, y + 118 + i * 27), line, font=font("segoeui.ttf", 19), fill=(201, 209, 217))
    d.ellipse((tx, y + 197, tx + 9, y + 206), fill=ACCENT)
    d.text((tx + 18, y + 191), STATUS, font=font("segoeui.ttf", 14), fill=(255, 255, 255))
    return layer


def fit(frame):
    """Crop the frame to the W:H shape around FOCUS_Y, then scale it to W x H."""
    fw, fh = frame.size
    crop_h = round(fw * H / W)
    top = round((fh - crop_h) * FOCUS_Y)
    return frame.crop((0, top, fw, top + crop_h)).resize((W, H), Image.LANCZOS)


def main():
    src = Image.open(SOURCE)
    card = card_layer()
    frames, durations = [], []
    for i, frame in enumerate(ImageSequence.Iterator(src)):
        if i % FRAME_STEP:
            continue
        frames.append(Image.alpha_composite(fit(frame.convert("RGBA")), card).convert("RGB"))
        durations.append(frame.info.get("duration", 100) * FRAME_STEP)

    out = OUT / "hero.webp"
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=durations, loop=0,
                   quality=QUALITY, method=4)
    size = out.stat().st_size
    print(f"wrote hero.webp: {len(frames)} frames, {size / 1e6:.1f} MB")
    if size > MAX_BYTES:
        print(f"warning: larger than {MAX_BYTES / 1e6:.0f} MB, raise FRAME_STEP or lower QUALITY")


if __name__ == "__main__":
    main()
