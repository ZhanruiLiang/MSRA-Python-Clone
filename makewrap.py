import Image
import sys
src, dest = sys.argv[1:3]
img0 = Image.open(src)
size = img0.size
size2 = (size[0]*2, size[1]*2)
img1 = img0.transpose(Image.FLIP_LEFT_RIGHT)
img2 = img1.transpose(Image.FLIP_TOP_BOTTOM)
img3 = img0.transpose(Image.FLIP_TOP_BOTTOM)
img = Image.new(img0.mode, size2)
img.paste(img0, (0, 0))
img.paste(img1, (size[0], 0))
img.paste(img2, (size[0], size[1]))
img.paste(img3, (0, size[1]))

img.save(dest)
