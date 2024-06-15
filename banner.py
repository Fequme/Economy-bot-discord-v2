from aiohttp import ClientSession
from PIL import Image, ImageFont, ImageDraw
import io
import textwrap

async def banner_dop(voice_count, member):

    background = Image.open('./assets/Gheto.png')

    draw = ImageDraw.Draw(background)


    myFont = ImageFont.truetype("./assets/234234.ttf", 120)
    myFont1 = ImageFont.truetype("./assets/234234.ttf", 100)
    

    draw.text((525, 340), f"{member}",font=myFont1, fill='#696969', stroke_fill=(0, 0, 0))


    draw.text((615, 100), f"{voice_count}", font=myFont, fill='#696969', stroke_fill=(0, 0, 0))


    f= open("./level.png", "wb") 
    background.save(f, "PNG", subsampling=0, quality=1000)
    return "./level.png"

