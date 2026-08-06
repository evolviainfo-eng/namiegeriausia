# -*- coding: utf-8 -*-
"""Refresh the Instagram strip from the public profile endpoint.

No OAuth, no Meta app, no client involvement — the public web endpoint
answers with just an app-id header and a real User-Agent.

Fails safe: on any error it leaves data/ig-feed.json and img/ig-* untouched,
so the strip keeps showing the last good fetch instead of going blank.
"""
import json, os, sys, io, base64, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER = 'namiegeriausia'
COUNT = 12
OUT_JSON = os.path.join(ROOT, 'data/ig-feed.json')
IMG_DIR = os.path.join(ROOT, 'img')
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
HDRS = {'x-ig-app-id': '936619743392459', 'User-Agent': UA,
        'Accept': '*/*', 'Accept-Language': 'lt-LT,lt;q=0.9,en;q=0.8'}


def clean_caption(node, limit=150):
    """Her own words, minus the hashtag tail — a wall of #interjerodizainas
    reads as spam on the site even though it belongs on Instagram."""
    e = node.get('edge_media_to_caption', {}).get('edges', [])
    if not e:
        return ''
    txt = e[0]['node']['text']
    keep = []
    for line in txt.split('\n'):
        w = [t for t in line.split() if not t.startswith('#')]
        if w:
            keep.append(' '.join(w))
    txt = ' '.join(keep).strip()
    if len(txt) > limit:
        cut = txt[:limit].rsplit(' ', 1)[0]
        txt = cut.rstrip('.,;:–—-') + '…'
    return txt


def get(url, headers=HDRS, timeout=30):
    r = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(r, timeout=timeout) as f:
        return f.read()


def fetch_profile():
    u = f'https://www.instagram.com/api/v1/users/web_profile_info/?username={USER}'
    return json.loads(get(u))['data']['user']


def main():
    try:
        u = fetch_profile()
    except Exception as e:
        print(f'IG fetch failed ({e}) — keeping existing feed', file=sys.stderr)
        return 0                      # fail safe: never break the build

    edges = u['edge_owner_to_timeline_media']['edges'][:COUNT]
    if not edges:
        print('IG returned no posts — keeping existing feed', file=sys.stderr)
        return 0

    from PIL import Image
    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)

    old = {}
    if os.path.exists(OUT_JSON):
        try:
            old = {p['code']: p for p in json.load(open(OUT_JSON))['posts']}
        except Exception:
            old = {}

    posts, fetched = [], 0
    for e in edges:
        n = e['node']
        code = n['shortcode']
        name = f'ig-{code}'
        dest = os.path.join(IMG_DIR, f'{name}-640.webp')

        if not os.path.exists(dest):                 # only pull what's new
            try:
                raw = get(n['display_url'], headers={'User-Agent': UA}, timeout=45)
            except Exception as ex:
                print(f'  skip {code}: {ex}', file=sys.stderr)
                if code in old:
                    posts.append(old[code])
                continue
            im = Image.open(io.BytesIO(raw)).convert('RGB')
            w, h = im.size                            # centre square crop
            s = min(w, h)
            im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))
            for W in (640,):
                im.resize((W, W), Image.LANCZOS).save(
                    os.path.join(IMG_DIR, f'{name}-{W}.webp'), 'WEBP', quality=82, method=6)
            fetched += 1

        # inline blur-up so a tile is never an empty square; sits on the tile,
        # not the <img>, and JS clears it the moment the real image paints
        with Image.open(os.path.join(IMG_DIR, f'{name}-640.webp')) as t:
            b = io.BytesIO()
            t.convert('RGB').resize((24, 24), Image.LANCZOS).save(b, 'WEBP', quality=45, method=6)
            blur = base64.b64encode(b.getvalue()).decode()

        posts.append({
            'code': code,
            'url': f'https://www.instagram.com/p/{code}/',
            'ts': n.get('taken_at_timestamp'),
            'video': bool(n.get('is_video')),
            'caption': clean_caption(n),
            'blur': blur,
        })

    if not posts:
        print('nothing usable — keeping existing feed', file=sys.stderr)
        return 0

    json.dump({'handle': USER, 'posts': posts},
              open(OUT_JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # drop images for posts that fell out of the window
    keep = {f'ig-{p["code"]}' for p in posts}
    for f in os.listdir(IMG_DIR):
        if f.startswith('ig-') and f.rsplit('-', 1)[0] not in keep:
            os.remove(os.path.join(IMG_DIR, f))

    print(f'{len(posts)} posts in strip, {fetched} newly downloaded')
    return 0


if __name__ == '__main__':
    sys.exit(main())
