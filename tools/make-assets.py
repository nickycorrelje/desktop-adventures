import sys
sys.argv=[sys.argv[0],'/home/claude/site/assets']
sys.path.insert(0,'/home/claude/gen')
import art8, art9, art5, art
from PIL import Image
OUT='/home/claude/site/assets'
orig8=art8.sprite
def nohero(img,x,y,rows,*a,**k):
    if rows is art.HERO or rows is art8.HERO: return
    return orig8(img,x,y,rows,*a,**k)
art8.sprite=nohero; art9.sprite=nohero
art8.start_world().save(OUT+'/world-start.png')
art9.work_tall().save(OUT+'/world-work.png')
import shutil
shutil.copy('/home/claude/gen/out11/walk3.png',OUT+'/walk.png')
# head icon for the logo
h=Image.new('RGBA',(12,8),(0,0,0,0)); art.sprite(h,0,0,art.HERO[:8]); h.resize((48,32),Image.NEAREST).save(OUT+'/head.png')
sheet,names=art.icons()
for i,nm in enumerate(names):
    sheet.crop((i*16,0,i*16+16,16)).resize((96,96),Image.NEAREST).save(f'{OUT}/icon-{nm}.png')
print(Image.open(OUT+'/world-start.png').size, Image.open(OUT+'/world-work.png').size, names)
