"""Draws the Klimhal world (320x224 native, saved at 4x) and the new icons.
Run from the site folder:  python3 tools/make-klimhal.py
Needs Pillow. world-home.png is reused for the door at the bottom."""
import os, random
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'assets')
S = 4


def C(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


INK = C('2b2433')
P = dict(
    k=INK, w=C('ffffff'), s=C('f2c9a0'), S=C('d9a37a'),
    r=C('d9482b'), R=C('a8321c'), y=C('f5c842'), o=C('f08a3c'), p=C('ef8fb0'),
    b=C('4a7fc7'), B=C('2f5a9e'), g=C('2f9e5b'), G=C('227a45'), t=C('9ad0a8'),
    n=C('9a9aa8'), N=C('d4d2dc'), d=C('3a3550'), h=C('1b1824'), m=C('b8573f'),
    e=C('e4c07a'), E=C('b8873f'), c=C('efe3d0'), u=C('8a5a3a'), U=C('6a4128'),
    x=C('d6b89a'), z=C('a8d4f0'), Z=C('6fa8d8'), v=C('8b6bb5'),
)


def sprite(img, x0, y0, rows, pal=P):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch != '.' and ch in pal:
                img.putpixel((x0 + i, y0 + j), pal[ch])


def rect(d, x, y, w, h, fill, line=None):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=fill, outline=line)


# ------------------------------------------------------------------ world
W, H = 320, 224
img = Image.new('RGB', (W, H), C('d9d4e2'))
d = ImageDraw.Draw(img)
rnd = random.Random(7)

# floor: cool concrete with a quiet grid
for y in range(86, H):
    for x in range(W):
        if (x % 40 == 0) or (y % 32 == 22):
            img.putpixel((x, y), C('c9c4d4'))
for _ in range(260):
    x, y = rnd.randrange(W), rnd.randrange(120, H)
    img.putpixel((x, y), C('e3dfec'))

# back wall
rect(d, 0, 0, W, 86, C('e6e1ee'))
for x in range(0, W, 40):
    d.line([x, 0, x, 85], fill=C('d6d1e0'))
rect(d, 0, 0, W, 7, C('2a4452'))                       # roof beam
rect(d, 0, 7, W, 2, C('1d3340'))
rect(d, 0, 82, W, 4, C('b9b3c7'))                      # skirting
d.line([0, 86, W, 86], fill=INK)

# the climbing wall
WX, WY, WW, WH = 66, 12, 196, 68
rect(d, WX, WY, WW, WH, C('c9cadb'), INK)
for gx in range(WX + 4, WX + WW - 2, 8):               # bolt-hole grid
    for gy in range(WY + 4, WY + WH - 2, 8):
        img.putpixel((gx, gy), C('aeb0c6'))
for gx in range(WX + 49, WX + WW - 1, 49):             # panel seams
    d.line([gx, WY + 1, gx, WY + WH - 2], fill=C('b4b6cc'))
d.line([WX + 1, WY + 34, WX + WW - 2, WY + 34], fill=C('b4b6cc'))
routes = {
    'b': [(82, 66), (88, 56), (94, 47), (101, 38), (110, 31), (120, 24), (128, 18)],
    'r': [(142, 70), (147, 61), (155, 54), (150, 44), (158, 36), (166, 28), (172, 19)],
    'y': [(190, 68), (197, 60), (192, 51), (200, 43), (208, 36), (203, 26), (212, 18)],
    'g': [(226, 70), (232, 61), (240, 54), (234, 45), (243, 37), (250, 29), (246, 19)],
    'p': [(112, 70), (118, 62), (124, 55), (118, 47), (126, 40), (134, 33), (140, 25)],
}
for col, pts in routes.items():
    for i, (hx, hy) in enumerate(pts):
        big = (i % 3 == 0)
        w, h = (6, 4) if big else (4, 3)
        rect(d, hx, hy, w, h, P[col], INK if big else None)
        if col in 'by':
            img.putpixel((hx + 1, hy), P['w'])
for (tx, ty, col) in [(86, 72, 'b'), (146, 72, 'r'), (194, 72, 'y'), (230, 72, 'g'), (116, 72, 'p')]:   # route tape on the bottom row
    rect(d, tx, ty, 8, 2, P[col])
# a start flag on the red route
rect(d, 168, 14, 5, 3, P['r'], INK)
# orange slab ramp at the wall's foot
for i in range(0, 20):
    d.line([WX + WW - 22 + i, WY + WH - 1 - i * 1, WX + WW - 2, WY + WH - 1 - i * 1], fill=C('f08a3c'))
d.polygon([(WX + WW - 22, WY + WH - 1), (WX + WW - 2, WY + WH - 21), (WX + WW - 2, WY + WH - 1)], fill=C('f08a3c'), outline=INK)

# 'Outdoors' poster
rect(d, 12, 18, 42, 48, P['c'], INK)
rect(d, 15, 21, 36, 42, P['z'])
d.polygon([(15, 63), (28, 38), (36, 50), (42, 40), (51, 63)], fill=P['G'])
d.polygon([(23, 63), (36, 33), (49, 63)], fill=C('7d7a90'))
d.polygon([(36, 33), (32, 41), (36, 39), (40, 42)], fill=P['w'])
rect(d, 18, 24, 6, 6, P['y'])
rect(d, 15, 63, 36, 1, INK)

# rope + gear rack on the far right
rect(d, 272, 22, 38, 3, P['u'], INK)
for hx, col in ((278, 'r'), (286, 'y'), (294, 'b'), (302, 'g')):
    rect(d, hx, 25, 3, 7, P['n'], INK)
    rect(d, hx, 31, 3, 2, P[col])
rect(d, 276, 42, 30, 24, P['v'], INK)                  # coiled rope
for ring in range(3):
    d.ellipse([278 + ring * 3, 44 + ring * 3, 303 - ring * 3, 63 - ring * 3], outline=C('c3a8e0'))

# crash mats under the wall
for mx in range(0, W, 64):
    rect(d, mx, 90, 64, 32, C('4a7fc7'), INK)
    rect(d, mx + 1, 91, 62, 3, C('7ea6e6'))
    rect(d, mx + 1, 118, 62, 3, C('2f5a9e'))
    d.line([mx + 32, 92, mx + 32, 119], fill=C('3b6cb5'))
rect(d, 0, 86, W, 4, C('2f5a9e'))
d.line([0, 86, W, 86], fill=INK)

# bench with climbing shoes (bottom left)
rect(d, 14, 154, 70, 8, P['e'], INK)
rect(d, 14, 154, 70, 2, C('f0d79e'))
rect(d, 18, 162, 5, 14, P['E'], INK)
rect(d, 75, 162, 5, 14, P['E'], INK)
shoe_a = ['..kkkk..', '.krrrrk.', 'krrwrrrk', 'kkkkkkkk']
shoe_b = ['..kkkk..', '.kbbbbk.', 'kbbwbbbk', 'kkkkkkkk']
sprite(img, 22, 150, shoe_a); sprite(img, 32, 150, shoe_b)
sprite(img, 52, 150, ['.kkkk.', 'kyyyyk', 'kyywyk', 'kkkkkk'])    # yellow shoe, a tad smaller
rect(d, 62, 146, 14, 9, P['g'], INK)                 # backpack
rect(d, 64, 148, 10, 2, P['G'])

# chalk bucket (bottom right)
rect(d, 268, 168, 24, 22, C('f4f1f8'), INK)
rect(d, 268, 168, 24, 4, C('d8d4e4'), INK)
rect(d, 268, 178, 24, 3, P['r'])
d.ellipse([271, 160, 289, 172], fill=P['w'], outline=INK)
d.ellipse([275, 163, 285, 169], fill=C('e6e1ee'))
for (px, py) in ((264, 190), (294, 192), (284, 193), (270, 195), (277, 197), (297, 187), (262, 184)):
    img.putpixel((px, py), P['w'])
d.ellipse([264, 189, 296, 197], outline=C('e9e4f2'))

# the friend, standing on the mat (ponytail, orange tee, chalk bag)
friend = [
    '.......kkkk.......',
    '......kyyyyk.k....',
    '.....kyyyyyykyk...',
    '.....kyyyyyykyyk..',
    '.....kyssssykyyk..',
    '.....ksksskkyyk...',
    '.....ksssssk.kk...',
    '......kssssk......',
    '.....kkoooookk....',
    '....kooooooook....',
    '...ksookooookss...',
    '...ksoooooooosk...',
    '...ksoooooooosk...',
    '...ksskkkkkkssk...',
    '....kkdddddddk....',
    '.....kdddddddk....',
    '.....kdddkdddk....',
    '.....kdddkdddk....',
    '.....kdddkdddk....',
    '.....kkddkddkk....',
    '.....kwwkkwwkk....',
    '....kkkkk.kkkkk...',
]
# stop the loop above from sprawling: 18x22 sprite, placed at (206,108)
sprite(img, 206, 108, friend)
d.ellipse([206, 127, 224, 134], outline=C('b9b3c7'))

# potted plant behind the friend side (top-left floor)
rect(d, 6, 100, 16, 14, P['E'], INK) if False else None

# doorway at the bottom: lifted straight from the home room so the door matches
home = Image.open(os.path.join(OUT, 'world-home.png')).convert('RGB')
door = home.crop((528, 824, 756, 896)).resize((57, 18), Image.NEAREST)
img.paste(door, (132, 206))

img.resize((W * S, H * S), Image.NEAREST).save(os.path.join(OUT, 'world-klimhal.png'))

# ------------------------------------------------------------------ icons (16x16, saved at 6x)
ICONS = {}
ICONS['routes'] = [
    '................',
    '.kkkkkkkkkkkkkk.',
    '.kNNNNNNNNNNNNk.',
    '.kNNNNNNNNNbbNk.',
    '.kNNNNNNNNNbbNk.',
    '.kNNNNNNNyNNNNk.',
    '.kNNNNrrNNNNNNk.',
    '.kNNNNrrNNNNNNk.',
    '.kNNggNNNNNNNNk.',
    '.kNNggNNNNyNNNk.',
    '.kNNNNNNNNNNNNk.',
    '.kNpNNNNNbbNNNk.',
    '.kNpNNNNNbbNNNk.',
    '.kNNNNNNNNNNNNk.',
    '.kkkkkkkkkkkkkk.',
    '................',
]
ICONS['friend'] = [
    '................',
    '.....kkkkkk.....',
    '....kyyyyyykkk..',
    '...kyyyyyyyykyk.',
    '...kyyyyyyyykyk.',
    '...kysssssykyyk.',
    '...kssssssskyk..',
    '...ksksssksskk..',
    '...kssssssssk...',
    '...kssskksssk...',
    '....kssssssk....',
    '.....kkssskk....',
    '...kkooooooookk.',
    '..kooooooooooook',
    '..kooooooooooook',
    '................',
]
ICONS['boyfriend'] = [
    '................',
    '.....kkkkkk.....',
    '....khhhhhhk....',
    '...khhhhhhhhk...',
    '...khhhhhhhhk...',
    '...khhssssshk...',
    '...khssssssshk..',
    '...kssksssksSk..',
    '...ksssssssssk..',
    '...kssssmmsssk..',
    '....kssssssSk...',
    '.....kkssskk....',
    '...kkrrkyykbkk..',
    '..kgrrkyykbbggk.',
    '..kgrrkyykbbggk.',
    '................',
]
ICONS['chalk'] = [
    '................',
    '.....kkkkkk.....',
    '....kwwwwwwk....',
    '...kwwwwwwwwk...',
    '...kwwNwwwwwk...',
    '....kkkkkkkk....',
    '...kwwwwwwwwk...',
    '...kwwwwwwwwk...',
    '...krrrrrrrrk...',
    '...krrrrrrrrk...',
    '...kwwwwwwwwk...',
    '...kwwwwwwwwk...',
    '...kNNNNNNNNk...',
    '....kkkkkkkk....',
    '..w.w...w..w....',
    '................',
]
ICONS['outdoors'] = [
    '................',
    '................',
    '..........yy....',
    '.........yyyy...',
    '.....kk...yy....',
    '....kwwk........',
    '...kwwnwk.......',
    '..kwnnnnwk.kk...',
    '..knnnnnnk.kGk..',
    '.knnnnnnnnkGGGk.',
    '.knnnnnnnnkGGGGk',
    'kknnnnnnnnkGGGGk',
    'kGGGGGGGGGGGGGGk',
    'kkkkkkkkkkkkkkkk',
    '................',
    '................',
]
PICO = dict(P)
PICO['N'] = C('cfd0e0')
for nm, rows in ICONS.items():
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    sprite(im, 0, 0, rows, PICO)
    im.resize((96, 96), Image.NEAREST).save(os.path.join(OUT, f'icon-{nm}.png'))
print('ok', Image.open(os.path.join(OUT, 'world-klimhal.png')).size)
