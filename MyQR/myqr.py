#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from MyQR.mylibs import theqrmodule
from PIL import Image
import itertools

# Positional parameters
#   words: str
#
# Optional parameters
#   version: int, from 1 to 40
#   level: str, just one of ('L','M','Q','H')
#   picutre: str, a filename of a image
#   colorized: bool
#   constrast: float
#   brightness: float
#   save_name: str, the output filename like 'example.png'
#   save_dir: str, the output directory
#
# See [https://github.com/sylnsfar/qrcode] for more details!
def run(words, version=1, level='H', picture=None, colorized=False, contrast=1.0, brightness=1.0, save_name=None, save_dir=os.getcwd()):

    supported_chars = r"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ··,.:;+-*/\~!@#$%^&`'=<>[]()?_{}|"


    # check every parameter
    if not isinstance(words, str) or any(i not in supported_chars for i in words):
        raise ValueError('Wrong words! Make sure the characters are supported!')
    if not isinstance(version, int) or version not in range(1, 41):
        raise ValueError('Wrong version! Please choose a int-type value from 1 to 40!')
    if not isinstance(level, str) or len(level)>1 or level not in 'LMQH':
        raise ValueError("Wrong level! Please choose a str-type level from {'L','M','Q','H'}!")
    if picture:
        if not isinstance(picture, str) or not os.path.isfile(picture) or picture[-4:] not in ('.jpg','.png','.bmp','.gif'):
            print(picture)
            raise ValueError("Wrong picture! Input a filename that exists and be tailed with one of {'.jpg', '.png', '.bmp', '.gif'}!")
        if picture[-4:] == '.gif' and save_name and save_name[-4:] != '.gif':
            raise ValueError('Wrong save_name! If the picuter is .gif format, the output filename should be .gif format, too!')
        if not isinstance(colorized, bool):
            raise ValueError('Wrong colorized! Input a bool-type value!')
        if not isinstance(contrast, float):
            raise ValueError('Wrong contrast! Input a float-type value!')
        if not isinstance(brightness, float):
            raise ValueError('Wrong brightness! Input a float-type value!')
    if save_name and (not isinstance(save_name, str) or save_name[-4:] not in ('.jpg','.png','.bmp','.gif')):
        raise ValueError("Wrong save_name! Input a filename tailed with one of {'.jpg', '.png', '.bmp', '.gif'}!")
    if not os.path.isdir(save_dir):
        raise ValueError('Wrong save_dir! Input a existing-directory!')
    
        
    def combine(ver, qr_name, bg_name, colorized, contrast, brightness, save_dir, save_name=None, scale_factor=4):
        from MyQR.mylibs.constant import alig_location
        from PIL import ImageEnhance, ImageFilter
        
        qr = Image.open(qr_name)
        qr = qr.convert('RGBA') if colorized else qr
        
        bg0 = Image.open(bg_name).convert('RGBA')
        bg0 = ImageEnhance.Contrast(bg0).enhance(contrast)
        bg0 = ImageEnhance.Brightness(bg0).enhance(brightness)


        if bg0.size[0] < bg0.size[1]:
            bg0 = bg0.resize((qr.size[0]-scale_factor*24, (qr.size[0]-scale_factor*24)*int(bg0.size[1]/bg0.size[0])))
        else:
            bg0 = bg0.resize(((qr.size[1]-scale_factor*24)*int(bg0.size[0]/bg0.size[1]), qr.size[1]-scale_factor*24))

        bg = bg0 if colorized else bg0.convert('1')

        aligs = []
        if ver > 1:
            aloc = alig_location[ver-2]
            for a in range(len(aloc)):
                for b in range(len(aloc)):
                    if not ((a==b==0) or (a==len(aloc)-1 and b==0) or (a==0 and b==len(aloc)-1)):
                        # for i in range(2*3*(aloc[a]-2), 2*3*(aloc[a]+3)):
                        #     for j in range(2*3*(aloc[b]-2), 2*3*(aloc[b]+3)):
                        for i in range(scale_factor*3*(aloc[a]-2), scale_factor*3*(aloc[a]+3)):
                            for j in range(scale_factor*3*(aloc[b]-2), scale_factor*3*(aloc[b]+3)):
                                aligs.append((i,j))


        def chunks(l, n):
            """Yield successive n-sized chunks from l."""
            for i in range(0, len(l), n):
                yield l[i:i + n]

        coords = list(range(0,scale_factor*3))

        coords_1 = [coords[i:i + scale_factor] for i in range(0, len(coords), scale_factor)][1]
        coords_21 = list(itertools.product(coords_1, coords_1))

        for i in range(qr.size[0]-scale_factor*24):
            for j in range(qr.size[1]-scale_factor*24):
                # if not ((i in (18,19,20)) or (j in (18,19,20)) or (i<24 and j<24) or (i<24 and j>qr.size[1]-49) or (i>qr.size[0]-49 and j<24) or ((i,j) in aligs) or (i%3==1 and j%3==1) or (bg0.getpixel((i,j))[3]==0)):
                if not (
                    (i<scale_factor*24 and j<scale_factor*24) or
                    (i<scale_factor*24 and j>qr.size[1]-scale_factor*48) or
                    (i>qr.size[0]-scale_factor*48 and j<scale_factor*24) or
                    ((i,j) in aligs) or
                    # (i%6==2 and j%6==2) or
                    # (i%6==2 and j%6==3) or
                    # (i%6==3 and j%6==2) or
                    # (i%6==3 and j%6==3) or
                    ((i%(scale_factor*3),j%(scale_factor*3)) in coords_21) or
                    (bg0.getpixel((i,j))[3]==0)
                ):

                    qr.putpixel((i+scale_factor*12,j+scale_factor*12), bg.getpixel((i,j)))

        qr_name = os.path.join(save_dir, os.path.splitext(os.path.basename(bg_name))[0] + '_qrcode.png') if not save_name else os.path.join(save_dir, save_name)
        qr.save(qr_name)
        qr.resize((qr.size[0]*3, qr.size[1]*3)).save(qr_name)
        return qr_name

    # tempdir = os.path.join(os.path.expanduser('~'), '.myqr')
    tempdir = save_dir

    try:
        # if not os.path.exists(tempdir):
        #     os.makedirs(tempdir)

        scale_factor = 4

        ver, qr_name = theqrmodule.get_qrcode(version, level, words, tempdir, scale_factor)

        if picture and picture[-4:]=='.gif':
            import imageio

            im = Image.open(picture)
            duration = im.info.get('duration', 0)
            im.save(os.path.join(tempdir, '0.png'))
            while True:
                try:
                    seq = im.tell()
                    im.seek(seq + 1)
                    im.save(os.path.join(tempdir, '%s.png' %(seq+1)))
                except EOFError:
                    break

            imsname = []
            for s in range(seq+1):
                bg_name = os.path.join(tempdir, '%s.png' % s)
                imsname.append(combine(ver, qr_name, bg_name, colorized, contrast, brightness, tempdir, scale_factor))

            ims = [imageio.imread(pic) for pic in imsname]
            qr_name = os.path.join(save_dir, os.path.splitext(os.path.basename(picture))[0] + '_qrcode.gif') if not save_name else os.path.join(save_dir, save_name)
            imageio.mimwrite(qr_name, ims, '.gif', **{ 'duration': duration/1000 })
        elif picture:
            qr_name = combine(ver, qr_name, picture, colorized, contrast, brightness, save_dir, save_name, scale_factor)
        elif qr_name:
            qr = Image.open(qr_name)
            qr_name = os.path.join(save_dir, os.path.basename(qr_name)) if not save_name else os.path.join(save_dir, save_name, scale_factor)

        return ver, level, qr_name
        
    except:
        raise
    finally:
        import shutil
        # if os.path.exists(tempdir):
        #     shutil.rmtree(tempdir)