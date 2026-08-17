from PIL import Image, ImageOps, ImageDraw
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def autocrop(im, bg_thresh=245, pad=18):
    gray = im.convert('L')
    # mask of "not near-white"
    mask = gray.point(lambda p: 255 if p < bg_thresh else 0)
    bbox = mask.getbbox()
    if not bbox:
        return im
    l,t,r,b = bbox
    l = max(0, l-pad); t = max(0, t-pad)
    r = min(im.width, r+pad); b = min(im.height, b+pad)
    return im.crop((l,t,r,b))

def square_pad(im, bg=(232,217,181)):
    w,h = im.size
    s = max(w,h)
    canvas = Image.new('RGB', (s,s), bg)
    canvas.paste(im, ((s-w)//2, (s-h)//2))
    return canvas

def make_circle_avatar(src_path, out_path, size=512, ring=(74,50,32), bg=(232,217,181)):
    im = Image.open(src_path)
    im = autocrop(im)
    im = square_pad(im, bg=bg)
    im = im.resize((size,size), Image.LANCZOS)
    mask = Image.new('L', (size,size), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((0,0,size,size), fill=255)
    out = Image.new('RGBA', (size,size), (0,0,0,0))
    out.paste(im, (0,0), mask)
    # ring
    d2 = ImageDraw.Draw(out)
    d2.ellipse((4,4,size-4,size-4), outline=ring+(255,), width=max(6,size//48))
    out.save(out_path)
    print('wrote', out_path, out.size)

def make_square_icon(src_path, out_path, size, bg=(20,58,58)):
    im = Image.open(src_path)
    im = autocrop(im, pad=6)
    im = square_pad(im, bg=bg)
    im = im.resize((size,size), Image.LANCZOS)
    im.save(out_path)
    print('wrote', out_path, im.size)

def make_home_scene(src_path, out_path, max_w=900):
    im = Image.open(src_path)
    im = autocrop(im, pad=10)
    w,h = im.size
    scale = max_w / w
    im = im.resize((max_w, int(h*scale)), Image.LANCZOS)
    im.save(out_path)
    print('wrote', out_path, im.size)

male = os.path.join(BASE, 'Male_rHabbit2.jpeg')
female = os.path.join(BASE, 'Female_rHabbit.jpeg')
tree = os.path.join(BASE, 'rHabbitson_Cruscoe.jpeg')

make_circle_avatar(male, os.path.join(BASE,'avatar_male.png'))
make_circle_avatar(female, os.path.join(BASE,'avatar_female.png'))
make_square_icon(tree, os.path.join(BASE,'icon-192.png'), 192)
make_square_icon(tree, os.path.join(BASE,'icon-512.png'), 512)
make_home_scene(tree, os.path.join(BASE,'home_scene.png'))
