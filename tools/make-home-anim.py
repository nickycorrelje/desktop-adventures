"""Splits the animated bits (black cat, red dog, record) out of world-home.png
and writes sprite sheets. Run once from tools/:  python3 make-home-anim.py
Needs assets/world-home-full.png (the original, with cat/dog/record baked in)."""
import math, os
from PIL import Image
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
full = Image.open(f'{A}/world-home-full.png').convert('RGBA')
bg = full.copy()
G = 8  # one art pixel = 8 px in the 1280-wide image
SEAT = (217, 119, 79, 255); INK = (43, 36, 51, 255); EYE = (244, 200, 66, 255)

def box(b): return full.crop(b)
def sheet(frames):
    w, h = frames[0].size
    s = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames): s.paste(f, (i * w, 0))
    return s
def cell(img, c, r, col, ox, oy):  # paint one art pixel, c/r relative to origin
    for y in range(G):
        for x in range(G):
            img.putpixel((ox + c * G + x, oy + r * G + y), col)

# ------------------------------------------------------------- cat (on the sofa)
CB = (216, 624, 312, 680); cw, ch = CB[2] - CB[0], CB[3] - CB[1]
base = box(CB)
def cat_frame(tail='down', blink=False):
    f = base.copy()
    # remove the original tail nub (art pixel at x=296..?, drawn at col 10,row 4 of the old crop) and redraw
    # original tail nub sits at world x 280..288, y 632..640
    for y in range(8):
        for x in range(8): f.putpixel((280 - CB[0] + x, 632 - CB[1] + y), SEAT)
    tails = {'down': [(280, 632)], 'up': [(280, 632), (280, 624)], 'out': [(280, 632), (288, 632), (288, 624)]}
    for (wx, wy) in tails[tail]: cell(f, 0, 0, INK, wx - CB[0], wy - CB[1])
    if blink: cell(f, 0, 0, INK, 232 - CB[0], 640 - CB[1])
    return f
cat = [cat_frame('down'), cat_frame('up'), cat_frame('out'), cat_frame('up'), cat_frame('down', True)]
for y in range(CB[1], CB[3]):
    for x in range(CB[0], CB[2]): bg.putpixel((x, y), SEAT)
sheet(cat).save(f'{A}/anim-cat.png')

# ------------------------------------------------------------- dog (on the rug)
DB = (696, 632, 816, 712)
SH = 88  # diamond pattern repeats every 88 px
for y in range(DB[1], DB[3]):
    for x in range(DB[0], DB[2]): bg.putpixel((x, y), full.getpixel((x + SH, y)))
dogfull = full.crop(DB)
dogbg = bg.crop(DB)
dog = Image.new('RGBA', dogfull.size, (0, 0, 0, 0))
for y in range(dog.height):
    for x in range(dog.width):
        if dogfull.getpixel((x, y)) != dogbg.getpixel((x, y)): dog.putpixel((x, y), dogfull.getpixel((x, y)))
TAILC = (168, 50, 28, 255)
def shift_tail(img, dy):
    out = img.copy(); tail = []
    for y in range(img.height):
        for x in range(img.width):
            if x + DB[0] >= 768 and img.getpixel((x, y)) == TAILC: tail.append((x, y)); out.putpixel((x, y), (0, 0, 0, 0))
    for x, y in tail:
        if 0 <= y + dy < img.height: out.putpixel((x, y + dy), TAILC)
    return out
dogs = [dog, shift_tail(dog, -16), dog, shift_tail(dog, 8)]
sheet(dogs).save(f'{A}/anim-dog.png')
open(f'{A}/_dogbox.txt', 'w').write(str(DB))

# ------------------------------------------------------------- record (spinning)
VB = (520, 200, 712, 264)
disc_c = (598, 236)
DISC = (27, 24, 36); LAB = (47, 158, 91)
vfull = full.crop(VB)
vd = vfull.copy()
def frame(k):
    f = vd.copy(); th = k * math.pi / 2 + math.pi / 4
    for y in range(VB[1], VB[3], G):
        for x in range(VB[0], VB[2], G):
            px = full.getpixel((x + 4, y + 4))[:3]
            dx, dy = (x + 4 - disc_c[0]), (y + 4 - disc_c[1]) * 2.2
            a = math.atan2(dy, dx); r = math.hypot(dx, dy)
            d = abs((a - th + math.pi) % (2 * math.pi) - math.pi)
            if px == DISC and d < 0.28 and 30 < r < 80: cell(f, 0, 0, (84, 80, 112, 255), x - VB[0], y - VB[1])
            if px == LAB and d < 0.55 and r > 4: cell(f, 0, 0, (150, 220, 175, 255), x - VB[0], y - VB[1])
    return f
sheet([frame(k) for k in range(4)]).save(f'{A}/anim-vinyl.png')
# the base image loses the record's *disc area* only: the sprite covers it
for y in range(VB[1], VB[3]):
    for x in range(VB[0], VB[2]): pass
bg.save(f'{A}/world-home.png')
print('ok', CB, DB, VB)
