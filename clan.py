from aiohttp import ClientSession
from PIL import Image, ImageFont, ImageDraw
import io

def convert(count : int):
    mes = ""
    
    count = int(count)
    if count >= 100000000000:
        mes = f"{str(count)[:3]}{str(round(count / 100000000000, 1))[1:]}КKK"
    elif count >= 10000000000:
        mes = f"{str(count)[:2]}{str(round(count / 10000000000, 1))[1:]}КKK"
    elif count >= 1000000000:
        mes = f"{str(count)[:1]}{str(round(count / 1000000000, 1))[1:]}КKK"
    elif count >= 100000000:
        mes = f"{str(count)[:3]}{str(round(count / 100000000, 1))[1:]}КK"
    elif count >= 10000000:
        mes = f"{str(count)[:2]}{str(round(count / 10000000, 1))[1:]}КK"
    elif count >= 1000000:
        mes = f"{str(count)[:1]}{str(round(count / 1000000, 1))[1:]}КK"
    elif count >= 100000:
        mes = f"{str(count)[:3]}{str(round(count / 100000, 1))[1:]}К"
    elif count >= 10000:
        mes = f"{str(count)[:2]}{str(round(count / 10000, 1))[1:]}К"
    elif count >= 1000:
        mes = f"{str(count)[:1]}{str(round(count / 1000, 1))[1:]}К"

    else:
        mes = str(count)

    return mes

async def clan_owner(banner, awa_owner, datesbor, balance, members, voicetime, name, awa_clan, lvl, max_members):

    async with ClientSession() as client:
        async with client.get(awa_clan) as response:
            awa_clan = await response.read()
    awa_clan = Image.open(io.BytesIO(awa_clan)).resize((310,310))

    async with ClientSession() as client:
        async with client.get(awa_owner) as wait:
            awa_owner = await wait.read()
    awa_owner = Image.open(io.BytesIO(awa_owner)).resize((310,310))

    background = Image.open('assets/clan.png') 

    clan = Image.open("assets/mask.png").convert('L').resize((310,310))
    background.paste(awa_clan, (158, 156), clan)

    owner = Image.open("assets/mask.png").convert('L').resize((310,310))
    background.paste(awa_owner, (223, 632), owner)

    draw = ImageDraw.Draw(background)

    

    myFont = ImageFont.truetype("./assets/gilroy-black.ttf",50)
    myFont1 = ImageFont.truetype("./assets/gilroy-black.ttf",40)
    myFont2 = ImageFont.truetype("./assets/gilroy-black.ttf",35)
    myFont3 = ImageFont.truetype("./assets/gilroy-black.ttf",170)
    myFont4 = ImageFont.truetype("./assets/gilroy-black.ttf",90)
    myFont5 = ImageFont.truetype("./assets/gilroy-black.ttf",120)
    myFont6 = ImageFont.truetype("./assets/gilroy-black.ttf",120)
    myFont7 = ImageFont.truetype("./assets/gilroy-black.ttf",100)
    myFont8 = ImageFont.truetype("./assets/gilroy-black.ttf",50)
    myFont9 = ImageFont.truetype("./assets/gilroy-black.ttf",50)
    
    


    draw.text((500, 240), f"{name}",font=myFont7, fill="#ffffff", stroke_width=1,stroke_fill=(0, 0, 0))
    draw.text((1380, 588), f"{members}",font=myFont5, fill="#ffffff", stroke_width=1,stroke_fill=(0, 0, 0))
    draw.text((1730, 588), f"{max_members}",font=myFont6, fill="#ffffff", stroke_width=1,stroke_fill=(0, 0, 0))

    draw.text((1532, 382), f"{datesbor}",font=myFont9, fill="#bdbdbd", stroke_width=1,stroke_fill=(0, 0, 0))
    draw.text((1368, 847), f"{convert(balance)}",font=myFont4, fill="#ffffff", stroke_width=1,stroke_fill=(0, 0, 0))
    draw.text((1532, 192), f"{voicetime}",font=myFont8, fill="#bdbdbd", stroke_width=1,stroke_fill=(0, 0, 0))

    if lvl == 0:
        draw.text((840, 681), f"{lvl}",font=myFont3, fill="#ffffff", stroke_width=1,stroke_fill=(0, 0, 0))
    elif lvl == 1:
        draw.text((853, 681), f"{lvl}",font=myFont3, fill="#ffffff", stroke_width=1,stroke_fill=(0, 0, 0))
    elif lvl == 2:
        draw.text((851, 681), f"{lvl}",font=myFont3, fill="#ffffff", stroke_width=1,stroke_fill=(0, 0, 0))
    elif lvl == 3:
        draw.text((851, 681), f"{lvl}",font=myFont3, fill="#ffffff", stroke_width=1,stroke_fill=(0, 0, 0))
    



    f= open("clan.png", "wb") 
    background.save(f, "PNG", subsampling=0, quality=1000)
    return "clan.png"

