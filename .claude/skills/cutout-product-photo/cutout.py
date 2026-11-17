from PIL import Image, ImageDraw, ImageFilter
import numpy as np
im = Image.open('/tmp/claude-0/-home-user/4f2079ce-e445-59ad-8ca4-aaa9c0b2aadd/scratchpad/gc/grubclub-04.webp').convert('RGB')
W, H = im.size
a = np.array(im).astype(float)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
# how lime-green-background-like each pixel is (0..1): strong green over red, low blue
s = np.clip(((g - r) - 6) / 10, 0, 1) * np.clip((105 - b) / 25, 0, 1) * np.clip((g - 75) / 15, 0, 1)
hard = (s > .5)
m = Image.fromarray((hard * 255).astype('uint8')).convert('RGB')
# the outer background = bg-like pixels connected to the image border (tape / interior lime stays)
for pt in [(0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1), (W // 2, 5), (W // 2, H - 5), (5, H // 2), (W - 5, H // 2)]:
    if m.getpixel(pt) == (255, 255, 255):
        ImageDraw.floodfill(m, pt, (255, 0, 0))
ma = np.array(m)
outer = (ma[..., 0] == 255) & (ma[..., 1] == 0)
# soft edge ring: outer region grown by 3px, alpha follows how un-background each pixel is
ring = np.array(Image.fromarray((outer * 255).astype('uint8')).filter(ImageFilter.MaxFilter(7))) > 0
alpha = np.where(outer, 0.0, np.where(ring, 1 - s, 1.0))
alpha = np.clip(alpha, 0, 1)
# remove the lime tint from edge pixels: un-mix with the local background colour
bgc = np.array([205., 245., 60.])
rgb = a.copy()
edge = ring & ~outer
al = np.clip(alpha, .08, 1)[..., None]
un = (a - (1 - al) * bgc) / al
rgb[edge] = np.clip(un, 0, 255)[edge]
# slight inward bite so no halo survives
ao = Image.fromarray((alpha * 255).astype('uint8')).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.9))
out = Image.fromarray(rgb.astype('uint8'), 'RGB').convert('RGBA')
out.putalpha(ao)
bb = ao.point(lambda v: 255 if v > 10 else 0).getbbox()
out = out.crop(bb)
out.thumbnail((1100, 1100), Image.LANCZOS)
out.save('/tmp/claude-0/-home-user/4f2079ce-e445-59ad-8ca4-aaa9c0b2aadd/scratchpad/gc/box2.webp', quality=92, method=6)
print(out.size, bb)
for name, col in (('dark', (14, 50, 81)), ('light', (247, 246, 250))):
    bg = Image.new('RGBA', out.size, col + (255,)); bg.alpha_composite(out); bg.convert('RGB').save(f'/tmp/claude-0/-home-user/4f2079ce-e445-59ad-8ca4-aaa9c0b2aadd/scratchpad/gc/box2_{name}.png')
