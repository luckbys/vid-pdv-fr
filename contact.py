from pathlib import Path
import sys,json,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
revision=sys.argv[1] if len(sys.argv)>1 else '1'
folder=ROOT/'qa'/('v'+revision)
grid=json.loads((ROOT/'beats.json').read_text())
font=ImageFont.truetype(str(ROOT/'assets/space-regular.ttf'),18)
for group in range(math.ceil(len(grid['beats'])/30)):
    indices=list(range(group*30,min((group+1)*30,len(grid['beats']))))
    sheet=Image.new('RGB',(1200,math.ceil(len(indices)/6)*390),'#D7D3CD');draw=ImageDraw.Draw(sheet)
    for j,i in enumerate(indices):
        with Image.open(folder/f'{i:03d}.png') as im:
            im=im.convert('RGB')
            im.resize((192,341),Image.Resampling.LANCZOS).save(folder/f'_thumb-{i:03d}.jpg')
            sheet.paste(im.resize((192,341),Image.Resampling.LANCZOS),(j%6*200,j//6*390))
        draw.text((j%6*200+5,j//6*390+347),f'beat {i:03d} · {grid["beats"][i]:.1f}s',font=font,fill='#10172B')
    sheet.save(folder/f'contact-{group+1}.jpg',quality=94)
    print(str(folder/f'contact-{group+1}.jpg'))
