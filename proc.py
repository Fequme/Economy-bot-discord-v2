from aiohttp import ClientSession
from PIL import Image, ImageFont, ImageDraw
import io
import textwrap

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
        

async def proc(avatar, username, voice, chat, balance, about, pc, vk, tg, inst, days, top, level, marry_avatar = None, marry_user = None, club_avatar = None, club_name = None):

    async with ClientSession() as client:
        async with client.get(avatar) as response:
            avatar = await response.read()
    avatar = Image.open(io.BytesIO(avatar)).resize((316,316))


    background = Image.open('./assets/profile.png')

    draw = ImageDraw.Draw(background)




    mask_im = Image.open("./assets/mask.png").convert('L').resize((316,316))
    background.paste(avatar, (786, 145), mask_im)

    

    myFont = ImageFont.truetype("./assets/gilroy-black.ttf",64)
    myFont1 = ImageFont.truetype("./assets/gilroy-black.ttf",64)
    myFont2 = ImageFont.truetype("./assets/Rostov.ttf",50)
    myFont3 = ImageFont.truetype("./assets/gilroy-black.ttf",50)
    myFont4 = ImageFont.truetype("./assets/Rostov.ttf",27)

    
    mask_im3 = Image.open("./assets/mask.png").convert('L').resize((80,80))

    ###### НИК #######

    if len(username) > 12:
        username = f"{username[:12]}..."

    text_width, text_height = myFont.getsize(username)
    text_x = (1880 - text_width) // 2
    text_y = (1150 - text_height) // 2
  
    draw.text((text_x, text_y), f"{username}",font=myFont,stroke_fill=(0, 0, 0))

    ###### LVL #######

    text_width1, text_height1 = myFont1.getsize(str(level))
    text_x1 = (1885 - text_width1) // 2
    text_y1 = (1600 - text_height1) // 2

    draw.text((text_x1, text_y1), f"{level}",font=myFont1, stroke_fill=(0, 0, 0))

    ###### ГОЛОСОВОЙ ОНЛАЙН #######

    draw.text((429, 623), f"{convert(voice)} ч.",font=myFont3,stroke_fill=(0, 0, 0))

    ###### ЧАТОВЫЙ ОНЛАЙН #######

    draw.text((479, 821), f"{convert(chat)}",font=myFont3,stroke_fill=(0, 0, 0))

    ###### ТОП ВСЕГО ОК #######

    text_width2, text_height2 = myFont3.getsize(str(top))
    text_x2 = (800 - text_width2) // 2
    text_y2 = (856 - text_height2) // 2

    if top == "Вне топа":
        draw.text((331, 401), f"{top}",font=myFont3,stroke_fill=(0, 0, 0))
    else:
        draw.text((text_x2, text_y2), f"{top}",font=myFont3,stroke_fill=(0, 0, 0))


    ###### БАЛАНС #######

    text_width3, text_height3 = myFont3.getsize(str(top))
    text_x3 = (2740 - text_width3) // 2
    text_y3 = (856 - text_height3) // 2


    draw.text((text_x3, text_y3), f"{convert(balance)}",font=myFont3,stroke_fill=(0, 0, 0))


    ###### ТВОЯ ПАРА #######

    if marry_user is None:
        pass
    else:
        async with ClientSession() as client:
            async with client.get(marry_avatar) as response:
                marry_avatar = await response.read()
        marry_avatar = Image.open(io.BytesIO(marry_avatar)).resize((115,115))

        mask_im1 = Image.open("./assets/mask.png").convert('L').resize((115,115))
        background.paste(marry_avatar, (1334, 598), mask_im1)

        if len(marry_user) > 9:
            marry_user = f'{marry_user[:9]}...'
        

        draw.text((1477, 630), f"{marry_user}",font=myFont2,stroke_fill=(0, 0, 0))

    ###### ТВОЙ КЛАН #######
    
    if club_avatar is None:
        pass
    else:
        async with ClientSession() as client:
            async with client.get(club_avatar) as response:
                club_avatar = await response.read()
        club_avatar = Image.open(io.BytesIO(club_avatar)).resize((116,115))

        mask_im1 = Image.open("./assets/mask.png").convert('L').resize((116,115))
        background.paste(club_avatar, (1334, 792), mask_im1)

        if len(club_name) > 9:
            club_name = f'{club_name[:9]}...'
        

        draw.text((1477, 830), f"{club_name}",font=myFont2,stroke_fill=(0, 0, 0))


    
    

    f= open("./profile.png", "wb") 
    background.save(f, "PNG", subsampling=0, quality=1000)
    return "./profile.png"

async def proc2(avatar, username, voice, chat, balance, about, pc, vk, tg, inst, days, top, level, club_avatar = None, club_name = None):

    async with ClientSession() as client:
        async with client.get(avatar) as response:
            avatar = await response.read()
    avatar = Image.open(io.BytesIO(avatar)).resize((316,316))


    background = Image.open('./assets/profile.png')

    draw = ImageDraw.Draw(background)




    mask_im = Image.open("./assets/mask.png").convert('L').resize((316,316))
    background.paste(avatar, (786, 145), mask_im)

    

    myFont = ImageFont.truetype("./assets/gilroy-black.ttf",64)
    myFont1 = ImageFont.truetype("./assets/gilroy-black.ttf",64)
    myFont2 = ImageFont.truetype("./assets/Rostov.ttf",50)
    myFont3 = ImageFont.truetype("./assets/gilroy-black.ttf",50)
    myFont4 = ImageFont.truetype("./assets/Rostov.ttf",27)

    
    mask_im3 = Image.open("./assets/mask.png").convert('L').resize((80,80))

    ###### НИК #######

    if len(username) > 12:
        username = f"{username[:12]}..."

    text_width, text_height = myFont.getsize(username)
    text_x = (1880 - text_width) // 2
    text_y = (1150 - text_height) // 2
  
    draw.text((text_x, text_y), f"{username}",font=myFont,stroke_fill=(0, 0, 0))

    ###### LVL #######

    text_width1, text_height1 = myFont1.getsize(str(level))
    text_x1 = (1885 - text_width1) // 2
    text_y1 = (1600 - text_height1) // 2

    draw.text((text_x1, text_y1), f"{level}",font=myFont1, stroke_fill=(0, 0, 0))

    ###### ГОЛОСОВОЙ ОНЛАЙН #######

    draw.text((429, 623), f"{convert(voice)} ч.",font=myFont3,stroke_fill=(0, 0, 0))

    ###### ЧАТОВЫЙ ОНЛАЙН #######

    draw.text((479, 821), f"{convert(chat)}",font=myFont3,stroke_fill=(0, 0, 0))

    ###### ТОП ВСЕГО ОК #######

    text_width2, text_height2 = myFont3.getsize(str(top))
    text_x2 = (800 - text_width2) // 2
    text_y2 = (856 - text_height2) // 2

    if top == "Вне топа":
        draw.text((331, 401), f"{top}",font=myFont3,stroke_fill=(0, 0, 0))
    else:
        draw.text((text_x2, text_y2), f"{top}",font=myFont3,stroke_fill=(0, 0, 0))


    ###### БАЛАНС #######

    text_width3, text_height3 = myFont3.getsize(str(top))
    text_x3 = (2740 - text_width3) // 2
    text_y3 = (856 - text_height3) // 2


    draw.text((text_x3, text_y3), f"{convert(balance)}",font=myFont3,stroke_fill=(0, 0, 0))


    ###### ТВОЙ КЛАН #######
    
    if club_avatar is None:
        pass
    else:
        async with ClientSession() as client:
            async with client.get(club_avatar) as response:
                club_avatar = await response.read()
        club_avatar = Image.open(io.BytesIO(club_avatar)).resize((116,115))

        mask_im1 = Image.open("./assets/mask.png").convert('L').resize((116,115))
        background.paste(club_avatar, (1334, 792), mask_im1)

        if len(club_name) > 9:
            club_name = f'{club_name[:9]}...'
        

        draw.text((1477, 830), f"{club_name}",font=myFont2,stroke_fill=(0, 0, 0))


    
    

    f= open("./profile.png", "wb") 
    background.save(f, "PNG", subsampling=0, quality=1000)
    return "./profile.png"


async def love(avatar, marry_avatar, balance, days, data, dater):

    async with ClientSession() as client:
        async with client.get(avatar) as response:
            avatar = await response.read()
    avatar = Image.open(io.BytesIO(avatar)).resize((219,219))


    background = Image.open('./assets/loveprofile.png')

    draw = ImageDraw.Draw(background)




    mask_im = Image.open("./assets/mask.png").convert('L').resize((219,219))
    background.paste(avatar, (662, 114), mask_im)

    

    myFont2 = ImageFont.truetype("./assets/gilroy-black.ttf",50)
    myFont3 = ImageFont.truetype("./assets/gilroy-black.ttf",64)

    


    
    async with ClientSession() as client:
        async with client.get(marry_avatar) as response:
            marry_avatar = await response.read()
    marry_avatar = Image.open(io.BytesIO(marry_avatar)).resize((219,219))

    mask_im1 = Image.open("./assets/mask.png").convert('L').resize((219,219))
    background.paste(marry_avatar, (985, 114), mask_im1)

    ### датта регистрации ###
    text_width4, text_height4 = myFont3.getsize(str(data))
    text_x4 = (3020 - text_width4) // 2
    text_y4 = (682- text_height4) // 2

    draw.text((text_x4, text_y4), f"{data}",font=myFont2,stroke_fill=(0, 0, 0))

    ### ВМЕСТЕ ###
    text_width1, text_height1 = myFont3.getsize(str(days))
    text_x1 = (683 - text_width1) // 2
    text_y1 = (682 - text_height1) // 2
    
    draw.text((text_x1, text_y1), f"{days} дн",font=myFont2,stroke_fill=(0, 0, 0))

    ### БАЛИК ###
    text_width, text_height = myFont3.getsize(str(convert(balance)))
    text_x = (756 - text_width) // 2
    text_y = (1160 - text_height) // 2

    draw.text((text_x, text_y), f"{convert(balance)}",font=myFont2,stroke_fill=(0, 0, 0))

    ### ДАТТА СПИСАНИЯ ###
    text_width2, text_height2 = myFont3.getsize(str(dater))
    text_x2 = (3020 - text_width2) // 2
    text_y2 = (1160- text_height2) // 2

    draw.text((text_x2, text_y2), f"{dater}",font=myFont2,stroke_fill=(0, 0, 0))




    f= open("./loveprofile.png", "wb") 
    background.save(f, "PNG", subsampling=0, quality=1000)
    return "./loveprofile.png"


async def timely(money, avatar):

    async with ClientSession() as client:
        async with client.get(avatar) as response:
            avatar = await response.read()
    avatar = Image.open(io.BytesIO(avatar)).resize((316,316))
    
    background = Image.open('./assets/timely.png')
    draw = ImageDraw.Draw(background)

    mask_im1 = Image.open("./assets/mask.png").convert('L').resize((316,316))
    background.paste(avatar, (148, 97), mask_im1)

    myFont3 = ImageFont.truetype("./assets/gilroy-black.ttf",90)

    text_width4, text_height4 = myFont3.getsize(str(money))
    text_x4 = (610 - text_width4) // 2
    text_y4 = (1302- text_height4) // 2


    draw.text((text_x4, text_y4), f"{money}",font=myFont3, stroke_fill=(0, 0, 0))

    f= open("./timely.png", "wb") 
    background.save(f, "PNG", subsampling=0, quality=1000)
    return "./timely.png"

async def balance(money, money_premium, avatar, name, x2):

    async with ClientSession() as client:
        async with client.get(avatar) as response:
            avatar = await response.read()
    avatar = Image.open(io.BytesIO(avatar)).resize((322,323))
    
    background = Image.open('./assets/balance.png')
    draw = ImageDraw.Draw(background)

    mask_im1 = Image.open("./assets/mask.png").convert('L').resize((322,323))
    background.paste(avatar, (615, 75), mask_im1)

    myFont1 = ImageFont.truetype("./assets/gilroy-black.ttf",50)
    myFont2 = ImageFont.truetype("./assets/gilroy-black.ttf",70)
    myFont3 = ImageFont.truetype("./assets/gilroy-black.ttf",65)

    text_width6, text_height6 = myFont1.getsize(str(x2))
    text_x6 = (520 - text_width6) // 2
    text_y6 = (270 - text_height6) // 2


    draw.text((text_x6, text_y6), f"{x2}",font=myFont1, stroke_fill=(0, 0, 0), fill='#FF0000')

    draw.text((200, 255), f"{convert(money)}",font=myFont2, stroke_fill=(0, 0, 0))
    draw.text((200, 445), f"{convert(money_premium)}",font=myFont2, stroke_fill=(0, 0, 0))

    if len(name) > 9:
        name = f"{name[:9]}..."

    text_width5, text_height5 = myFont3.getsize(str(name))
    text_x5 = (1550 - text_width5) // 2
    text_y5 = (985 - text_height5) // 2

    draw.text((text_x5, text_y5), f"{name}",font=myFont3, stroke_fill=(0, 0, 0))

    f= open("./balance.png", "wb") 
    background.save(f, "PNG", subsampling=0, quality=1000)
    return "./balance.png"


