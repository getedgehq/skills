"""Assemble the 2x2 post image from the four renders (plus a tiny footer)."""
from PIL import Image, ImageDraw, ImageFont
names = ['p1_post_impressionist', 'p2_impressionist', 'p3_ukiyoe', 'p4_bruegel_winter']
TW, TH, G, FOOT = 1600, 1200, 16, 70
W, H = TW * 2 + G * 3, TH * 2 + G * 3 + FOOT
bg = (18, 18, 20)
im = Image.new('RGB', (W, H), bg)
for i, n in enumerate(names):
    t = Image.open(f'out/{n}.png').convert('RGB').resize((TW, TH), Image.LANCZOS)
    im.paste(t, (G + (i % 2) * (TW + G), G + (i // 2) * (TH + G)))
d = ImageDraw.Draw(im)
try:
    f = ImageFont.truetype('Inter.ttc', 30)
except OSError:
    f = ImageFont.load_default(30)
txt = 'made entirely with Python · no image model'
w = d.textlength(txt, font=f)
d.text(((W - w) / 2, H - FOOT + 12), txt, font=f, fill=(190, 190, 195))
im.save('out/grid_2x2.png')
im.resize((W // 2, H // 2), Image.LANCZOS).save('out/grid_2x2_web.jpg', quality=90)
print(im.size)
