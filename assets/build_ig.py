# -*- coding: utf-8 -*-
"""Cut the Instagram rail tiles at 640 and 900, from a 4x master where it helps.

A tile renders at 340px (72vw on a phone), so 900px covers it at 2x with room
to spare. Sources come from two places: the original 2026 scrape in
assets/raw/ig/ for the posts that were already there, and assets/raw/ig-strip/
for anything fetch_ig.py has pulled since.

Super-resolution is only worth its time when the source is close to the output.
A 3072px cover downscaled to 900 is already a 3.4x reduction and needs no help,
so SR is skipped above SR_ABOVE and the tile is cut straight from the original.

  python3 assets/build_ig.py
"""
import base64, glob, io, json, os, sys, subprocess

from PIL import Image, ImageFilter
Image.MAX_IMAGE_PIXELS = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'img')
SR = os.path.join(ROOT, 'assets/sr-ig')
WIDTHS = (640, 900)
SR_ABOVE = 2250          # source already ≥2.5x the largest tile: leave it alone


def source(code):
    for pat in (f'assets/raw/ig-strip/{code}.jpg',
                f'assets/raw/ig-strip/{code}.jpeg',
                f'assets/raw/ig/{code}_00_*.jpg'):
        fs = sorted(glob.glob(os.path.join(ROOT, pat)))
        if fs:
            return fs[0]
    return None


def master(f, code):
    """4x master for a small source, the source itself for a big one."""
    with Image.open(f) as probe:
        w = probe.width
    if w >= SR_ABOVE:
        return Image.open(f).convert('RGB'), 'source'
    out = os.path.join(SR, code + '.png')
    if not os.path.exists(out):
        os.makedirs(SR, exist_ok=True)
        lst = os.path.join(SR, code + '.txt')
        open(lst, 'w').write(f + '\n')
        try:
            subprocess.run([sys.executable, os.path.join(ROOT, 'assets/sr_mps.py'), lst, SR],
                           check=True)
        except Exception as ex:
            print(f'  SR unavailable for {code} ({ex}); cutting from source')
        os.remove(lst)
        made = os.path.join(SR, os.path.splitext(os.path.basename(f))[0] + '.png')
        if made != out and os.path.exists(made):
            os.rename(made, out)
    if os.path.exists(out):
        return Image.open(out).convert('RGB'), '4x'
    return Image.open(f).convert('RGB'), 'source'


def square(im):
    w, h = im.size
    s = min(w, h)
    # IG crops its own grid from the centre, so the tile matches what she posted
    return im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))


def main():
    fp = os.path.join(ROOT, 'data/ig-feed.json')
    feed = json.load(open(fp, encoding='utf-8'))
    posts = feed['posts']
    for p in posts:
        code = p['code']
        f = source(code)
        if not f:
            print('NO SOURCE', code); continue
        im, how = master(f, code)
        sq = square(im)
        for W in WIDTHS:
            if W > sq.width:
                continue
            r = sq.resize((W, W), Image.LANCZOS)
            r = r.filter(ImageFilter.UnsharpMask(radius=1.1, percent=45, threshold=2))
            r.save(os.path.join(IMG, f'ig-{code}-{W}.webp'), 'WEBP', quality=88, method=6)
        # inline blur-up so a tile is never an empty square
        b = io.BytesIO()
        sq.resize((24, 24), Image.LANCZOS).save(b, 'WEBP', quality=45, method=6)
        p['blur'] = base64.b64encode(b.getvalue()).decode()
        print(f'{code}  {im.size} via {how}')

    json.dump(feed, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    keep = {f'ig-{p["code"]}' for p in posts}
    for f in os.listdir(IMG):
        if f.startswith('ig-') and f.rsplit('-', 1)[0] not in keep:
            os.remove(os.path.join(IMG, f))
    print(f'{len(posts)} tiles')


if __name__ == '__main__':
    main()
