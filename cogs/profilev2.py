import nextcord
import sqlite3
from nextcord.ext import commands
import sqlite3
from datetime import datetime, date, time, timedelta
from nextcord.ui import Button, View
from config import *
from proc import love, proc, proc2
from dateutil.relativedelta import relativedelta

c_db = sqlite3.connect('database/clan.db', timeout=10)
c = c_db.cursor()

mr_db = sqlite3.connect('database/marry.db', timeout=10)
mr = mr_db.cursor()

task_db = sqlite3.connect('database/tasks.db', timeout=10)
task = task_db.cursor()

lvl_db = sqlite3.connect('database/lvl.db', timeout=10)
lvl = lvl_db.cursor()

pec_db = sqlite3.connect('database/premium.db')
pec = pec_db.cursor()

ec_db = sqlite3.connect('database/economy.db', timeout=10)
ec = ec_db.cursor() 

class closs(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(label = 'Да', custom_id="yes", style = nextcord.ButtonStyle.green, row = False, disabled=True)
    async def yes(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        pass

    @nextcord.ui.button(label = 'Нет', custom_id="no", style = nextcord.ButtonStyle.red, row = False, disabled=True)
    async def no(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        pass       

class profileplus(nextcord.ui.Modal):
    def __init__(self):
        super().__init__('Установить статус')

        self.status = nextcord.ui.TextInput(label = 'Новый статус', min_length=1, max_length=150, required=True, placeholder='Только давай без пошлостей')
        self.add_item(self.status)


    async def callback(self, interaction: nextcord.Interaction) -> None:
        stat = self.status.value

        profile_db = sqlite3.connect('database/profile.db', timeout=10)
        profile = profile_db.cursor()

        profile.execute(f"UPDATE profile SET status='{stat}' where id={interaction.user.id} and guild_id={interaction.guild.id}")
        profile_db.commit()

        emb = nextcord.Embed(description=f'Ваш новый статус: `{stat}`', color = 0x2b2d31)
        emb.set_thumbnail(url=interaction.user.display_avatar)
        
        await interaction.send(embed=emb, ephemeral = True)
        

class profilev2(commands.Cog):

    def __init__(self, bot):
        self.bot = bot



    @nextcord.slash_command(description='Профиль')
    async def profile(self, interaction: nextcord.Interaction, mode : str = nextcord.SlashOption(name="категория-профиля", choices={"любовный": 'l', "обычный": 's'}, description='Укажи тип профиля для дальнейшей информации'),  member: nextcord.Member  = None):
        bot = self.bot
        owner = interaction.user
        user = member or interaction.user
        mr_db = sqlite3.connect('database/marry.db', timeout=10)
        mr = mr_db.cursor()
        ec_db = sqlite3.connect('database/economy.db', timeout=10)
        ec = ec_db.cursor()
        cost = settings['cost_marry']


        
        if mode == 's':


            profile_db = sqlite3.connect('database/profile.db', timeout=10)
            profile = profile_db.cursor()              
            

            class edit(nextcord.ui.View):
                def __init__(self):
                    super().__init__(timeout=60)
                    if profile.execute(f"SELECT vk FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 'none':
                        self.add_item(nextcord.ui.Button(style=nextcord.ButtonStyle.link, url=f'https://vk.com/{profile.execute(f"SELECT vk FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]}', label=" ", emoji='<:vk:1060921047572033536>', disabled=True))
                    else:
                        self.add_item(nextcord.ui.Button(style=nextcord.ButtonStyle.link, url=f'https://vk.com/{profile.execute(f"SELECT vk FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]}', label=" ", emoji='<:vk:1060921047572033536>', disabled=False))
                    
                    if profile.execute(f"SELECT tg FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 'none':
                        self.add_item(nextcord.ui.Button(style=nextcord.ButtonStyle.link, url=f'https://t.me/{profile.execute(f"SELECT tg FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]}', label=" ", emoji='<:tg:1060921043390316646>', disabled=True))
                    else:
                        self.add_item(nextcord.ui.Button(style=nextcord.ButtonStyle.link, url=f'https://t.me/{profile.execute(f"SELECT tg FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]}', label=" ", emoji='<:tg:1060921043390316646>', disabled=False))

                    if profile.execute(f"SELECT inst FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 'none':
                        self.add_item(nextcord.ui.Button(style=nextcord.ButtonStyle.link, url=f'https://www.instagram.com/{profile.execute(f"SELECT inst FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]}/', label=" ", emoji='<:inst:1060921976035737690>', disabled=True))
                    else:
                        self.add_item(nextcord.ui.Button(style=nextcord.ButtonStyle.link, url=f'https://www.instagram.com/{profile.execute(f"SELECT inst FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]}/', label=" ", emoji='<:inst:1060921976035737690>', disabled=False))
                

                if user.id != interaction.user.id:
                    @nextcord.ui.button(label = '', emoji='<:edit:1061207203790454794> ', style = nextcord.ButtonStyle.grey, disabled=True)
                    async def edit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        pass
                else:
                    @nextcord.ui.button(label = '', emoji='<:edit:1061207203790454794> ', style = nextcord.ButtonStyle.grey)
                    async def edit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if owner.id == interaction.user.id:

                            class tg(nextcord.ui.Modal):
                                def __init__(self):
                                    super().__init__('Установка TG')

                                    self.vk = nextcord.ui.TextInput(label = 'Укажи id своего TG', min_length=1, max_length=50, required=True, placeholder='Пример: roozzz1m', style=nextcord.TextInputStyle.paragraph)
                                    self.add_item(self.vk)

                                async def callback(self, interaction: nextcord.Interaction) -> None:
                                    vk = self.vk.value
                                    profile.execute(f'UPDATE profile SET tg = "{vk}" where id={interaction.user.id} and guild_id = {interaction.guild.id}')
                                    profile_db.commit()

                                    embed=nextcord.Embed(description=f"Вы успешно установили свой VK - https://t.me/{vk}", color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)
                                    await interaction.send(embed=embed, ephemeral=True)

                            class inst(nextcord.ui.Modal):
                                def __init__(self):
                                    super().__init__('Установка инстаграмма')

                                    self.vk = nextcord.ui.TextInput(label = 'Укажи id своего инстаграмма', min_length=1, max_length=50, required=True, placeholder='Пример: roozzz1m', style=nextcord.TextInputStyle.paragraph)
                                    self.add_item(self.vk)

                                async def callback(self, interaction: nextcord.Interaction) -> None:
                                    vk = self.vk.value
                                    profile.execute(f'UPDATE profile SET inst = "{vk}" where id={interaction.user.id} and guild_id = {interaction.guild.id}')
                                    profile_db.commit()

                                    embed=nextcord.Embed(description=f"Вы успешно установили свой инстаграмм - https://www.instagram.com/{vk}/", color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)
                                    await interaction.send(embed=embed, ephemeral=True)

                            class vk(nextcord.ui.Modal):
                                def __init__(self):
                                    super().__init__('Установка VK')

                                    self.vk = nextcord.ui.TextInput(label = 'Укажи id своего VK', min_length=1, max_length=50, required=True, placeholder='Пример: roozzz1m', style=nextcord.TextInputStyle.paragraph)
                                    self.add_item(self.vk)

                                async def callback(self, interaction: nextcord.Interaction) -> None:
                                    vk = self.vk.value
                                    profile.execute(f'UPDATE profile SET vk = "{vk}" where id={interaction.user.id} and guild_id = {interaction.guild.id}')
                                    profile_db.commit()

                                    embed=nextcord.Embed(description=f"Вы успешно установили свой VK - https://vk.com/{vk}", color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)
                                    await interaction.send(embed=embed, ephemeral=True)

                            embed=nextcord.Embed(title="Редактирование профиля", color=0x2b2d31)
                            embed.set_footer(text='Чтобы повторно заменить свою соц сеть, нажмите на кнопку c иконкой нужной соц сети, а что бы удалить нажмите на иконку нужной соц сети с корзинкой')
                            embed.set_thumbnail(url=interaction.user.display_avatar)

                            class m(nextcord.ui.View):
                                def __init__(self):
                                    super().__init__(timeout=60)
                                    self.joy = 0
                                
                                @nextcord.ui.button(label = '', emoji='<:vk:1060921047572033536>',style = nextcord.ButtonStyle.grey, row = False)
                                async def setvk(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):

                                    if owner.id == interaction.user.id:
                                        await interaction.response.send_modal(vk())       
                                    else:
                                        embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)

                                @nextcord.ui.button(label = '', emoji='<:tg:1060921043390316646>',style = nextcord.ButtonStyle.grey, row = False)
                                async def settg(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                    if owner.id == interaction.user.id:
                                        await interaction.response.send_modal(tg())       
                                    else:
                                        embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)

                                @nextcord.ui.button(label = '', emoji='<:inst:1060921976035737690> ', style = nextcord.ButtonStyle.grey, row = False)
                                async def setinst(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                    if owner.id == interaction.user.id:
                                        await interaction.response.send_modal(inst())       
                                    else:
                                        embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)   





                                if profile.execute(f"SELECT vk FROM profile where id={owner.id} and guild_id={interaction.guild.id}").fetchone()[0] == 'none':
                                    
                                    @nextcord.ui.button(label = '', emoji='<:delvk:1060931020389617774>' , style = nextcord.ButtonStyle.grey, disabled=True, row = True)
                                    async def vkdel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                        pass
                                    
                                else:
                                    
                                    @nextcord.ui.button(label = '', emoji='<:delvk:1060931020389617774>', style = nextcord.ButtonStyle.grey, disabled=False, row = True)
                                    async def vkdel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                        
                                
                                        if owner.id == interaction.user.id:
                                            profile.execute(f'UPDATE profile SET vk = "none" where id={interaction.user.id} and guild_id = {interaction.guild.id}')
                                            profile_db.commit()

                                            embed=nextcord.Embed(description=f"Вы успешно удалили свой VK из профиля", color=0x2b2d31)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)
                                            await interaction.send(embed=embed, ephemeral=True)     
                                        else:
                                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                                            await interaction.send(embed=embed, ephemeral= True)   
                                            
                                if profile.execute(f"SELECT tg FROM profile where id={owner.id} and guild_id={interaction.guild.id}").fetchone()[0] == 'none':

                                    @nextcord.ui.button(label = '', emoji='<:deltg:1060931231920967791>', style = nextcord.ButtonStyle.grey, disabled=True, row = True)
                                    async def tgdel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                        pass
                                else:
                                    
                                    @nextcord.ui.button(label = '', emoji='<:deltg:1060931231920967791>', style = nextcord.ButtonStyle.grey, disabled=False, row = True)
                                    async def tgdel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                        if owner.id == interaction.user.id:
                                            profile.execute(f'UPDATE profile SET tg = "none" where id={interaction.user.id} and guild_id = {interaction.guild.id}')
                                            profile_db.commit()

                                            embed=nextcord.Embed(description=f"Вы успешно удалили свой TG из профиля", color=0x2b2d31)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)
                                            await interaction.send(embed=embed, ephemeral=True)     
                                        else:
                                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                                            await interaction.send(embed=embed, ephemeral= True)   

                                if profile.execute(f"SELECT inst FROM profile where id={owner.id} and guild_id={interaction.guild.id}").fetchone()[0] == 'none':
                                    
                                    @nextcord.ui.button(label = '', emoji='<:delinst:1060928439579857028>' , style = nextcord.ButtonStyle.grey, disabled=True, row = True)
                                    async def instdel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                        pass
                                else:
                                    
                                    @nextcord.ui.button(label = '', emoji='<:delinst:1060928439579857028>', style = nextcord.ButtonStyle.grey, disabled=False, row = True)
                                    async def instdel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                        if owner.id == interaction.user.id:
                                            profile.execute(f'UPDATE profile SET inst = "none" where id={interaction.user.id} and guild_id = {interaction.guild.id}')
                                            profile_db.commit()

                                            embed=nextcord.Embed(description=f"Вы успешно удалили свой INST из профиля", color=0x2b2d31)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)
                                            await interaction.send(embed=embed, ephemeral=True)     
                                        else:
                                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                                            await interaction.send(embed=embed, ephemeral= True)  

                                @nextcord.ui.button(label = '', emoji='<:update:1060919543968579594>', style = nextcord.ButtonStyle.gray, disabled=False, row = 3)
                                async def update(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):   
                                    if owner.id == interaction.user.id:


                                        
                                        
                                            
                                        author = interaction.user
                                        

                                        timestamp = datetime.now().timestamp()
                                        todate = datetime.utcfromtimestamp(timestamp).strftime('%m/%d/%Y')


                                        rdate = user.joined_at.strftime('%m/%d/%Y')
                                        

                                        date_format = "%m/%d/%Y"
                                        a1 = datetime.strptime(rdate, date_format) 
                                        b1 = datetime.strptime(todate, date_format)
                                        delta = b1 - a1

                                        def top(top : int):
                                            index = []
                                            for voice in profile.execute(f"SELECT id FROM profile where guild_id = {interaction.guild.id} ORDER BY voice DESC LIMIT {top}"):

                                                index.append(voice[0])

                                            try:
                                                score = index.index(interaction.user.id) + 1
                                                index.index(interaction.user.id) 
                                            except ValueError:
                                                score = "Вне топа"
                                            return score

                                        
                                            
                                        rt = relativedelta(seconds=profile.execute(f"SELECT voice FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0])
                                        voice = round(int(profile.execute(f"SELECT voice FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]) // 3600, 0)
                                        name = user.display_name
                                        avatar = user.display_avatar.url
                                        marry_user = interaction.guild.get_member(int(mr.execute(f"SELECT user FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],))
                                        
                                        for css in c.execute(f"SELECT owner_club FROM user WHERE id={user.id}"):
                                            if  mr.execute(f"SELECT user FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0 and css[0] == 0:
                                                
                                                ad = await proc(avatar, name, voice,
                                                str(profile.execute(f"SELECT txt FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                                                
                                                str(ec.execute(f"SELECT bal FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                                                
                                                profile.execute(f"SELECT status FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                                                
                                                str(pec.execute(f"SELECT bal FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                                                
                                                profile.execute(f"SELECT vk FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                                                
                                                profile.execute(f"SELECT tg FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 

                                                profile.execute(f"SELECT inst FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],

                                                delta.days,

                                                top(1000),

                                                lvl.execute(f"SELECT lvl FROM level WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0])

                                        

                                            elif  mr.execute(f"SELECT user FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0 and css[0] > 0:
                                                for css1 in c.execute(f"SELECT name, avatar FROM clan WHERE owner={css[0]}"):
                                                    ad = await proc2(avatar, name, voice,
                                                    str(profile.execute(f"SELECT txt FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                                                    
                                                    str(ec.execute(f"SELECT bal FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                                                    
                                                    profile.execute(f"SELECT status FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                                                    
                                                    str(pec.execute(f"SELECT bal FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                                                    
                                                    profile.execute(f"SELECT vk FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                                                    
                                                    profile.execute(f"SELECT tg FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 

                                                    profile.execute(f"SELECT inst FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],

                                                    delta.days,

                                                    top(1000),

                                                    lvl.execute(f"SELECT lvl FROM level WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],

                                                    str(css1[1]),

                                                    str(css1[0]))
                                                
                                                        
                                            elif  mr.execute(f"SELECT user FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] > 0 and css[0] == 0:

                                                ad = await proc(avatar, name, voice,
                                                str(profile.execute(f"SELECT txt FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                                                
                                                str(ec.execute(f"SELECT bal FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                                                
                                                profile.execute(f"SELECT status FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                                                
                                                str(pec.execute(f"SELECT bal FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                                                
                                                profile.execute(f"SELECT vk FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                                                
                                                profile.execute(f"SELECT tg FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 

                                                profile.execute(f"SELECT inst FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],

                                                delta.days,

                                                top(1000),

                                                lvl.execute(f"SELECT lvl FROM level WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],

                                                marry_user.display_avatar.url,

                                                marry_user.display_name,

                                                )

                                            
                                            elif  mr.execute(f"SELECT user FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] > 0 and css[0] > 0:
                                                for css1 in c.execute(f"SELECT name, avatar FROM clan WHERE owner={css[0]}"):
                                                    ad = await proc(avatar, name, voice,
                                                    str(profile.execute(f"SELECT txt FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                                                    
                                                    str(ec.execute(f"SELECT bal FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                                                    
                                                    profile.execute(f"SELECT status FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                                                    
                                                    str(pec.execute(f"SELECT bal FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                                                    
                                                    profile.execute(f"SELECT vk FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                                                    
                                                    profile.execute(f"SELECT tg FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 

                                                    profile.execute(f"SELECT inst FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],

                                                    delta.days,

                                                    top(1000),

                                                    lvl.execute(f"SELECT lvl FROM level WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],

                                                    marry_user.display_avatar.url,

                                                    marry_user.display_name,

                                                    str(css1[1]),

                                                    str(css1[0]))
                                                
                                            await interaction.response.defer()
                                            await interaction.send(file=nextcord.File(ad), view=edit())
                                                     
                                    else:
                                        embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)   
                                
                                @nextcord.ui.button(label = '', emoji="<:aboutme:1061250636475269150>", style = nextcord.ButtonStyle.grey, row = 3, disabled=True)
                                async def status(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                    if owner.id == interaction.user.id:
                                        await interaction.response.send_modal(profileplus())
                                        return
                                    else:
                                        embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)                

                                @nextcord.ui.button(label = '', emoji='<:exit:1060934325853507696>', style = nextcord.ButtonStyle.gray, disabled=False, row = 3)
                                async def exit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):                          
                                    if owner.id == interaction.user.id:
                                        await interaction.edit(embed=None, view=edit())
                                    else:
                                        embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)   


                            await interaction.edit(embed = embed, view=m())

                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)

                @nextcord.ui.button(label = '', emoji='<:104345:1081868463313793064>', style = nextcord.ButtonStyle.grey)
                async def info(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                    timestamp = datetime.now().timestamp()
                    todate = datetime.utcfromtimestamp(timestamp).strftime('%m/%d/%Y')


                    rdate = user.joined_at.strftime('%m/%d/%Y')
                    
                    

                    date_format = "%m/%d/%Y"
                    a1 = datetime.strptime(rdate, date_format) 
                    b1 = datetime.strptime(todate, date_format)
                    delta = b1 - a1
                    rt = relativedelta(seconds=profile.execute(f"SELECT voice FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0])
                    embed=nextcord.Embed(title="Подробная информация о профиле - {}".format(user), color=0x2b2d31)
                    embed.set_thumbnail(url=user.display_avatar)
                    embed.add_field(name=f"{settings['balance']} Баланс:", value="```{}```".format(ec.execute(f"SELECT bal FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), inline=True)
                    embed.add_field(name=f"{settings['premium']} Премиум баланс:", value="```{}```".format(pec.execute(f"SELECT bal FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), inline=True)
                    embed.add_field(name=f"{settings['voice_online']} Голосовой онлайн:", value='```{:01d} дн. {:01d} ч. {:01d} мин. {:01d} сек.```'.format(int(rt.days), int(rt.hours), int(rt.minutes), int(rt.seconds)), inline=False)
                    embed.add_field(name=f"{settings['text_online']} Текстовой онлайн:", value=f'```{profile.execute(f"SELECT txt FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]} сообщ.```', inline=True)
                    embed.add_field(name=f"{settings['lvl']} Уровень:", value=f'```{lvl.execute(f"SELECT lvl FROM level WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]} уровень | До нового уровня осталось {int(settings["max_xp"]) - int(lvl.execute(f"SELECT lvl FROM level WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0])} XP```', inline=False)
                    embed.add_field(name=f"{settings['top']} Топ:", value=f'```{top(1000)} место```', inline=True)
                    if  mr.execute(f"SELECT user FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                        embed.add_field(name=f"{settings['partner']} Пара:", value=f'```Отсутствует```', inline=False)
                    else:
                        marry_user = interaction.guild.get_member(int(mr.execute(f"SELECT user FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],))
                        embed.add_field(name=f"{settings['partner']} Пара:", value=f'```{marry_user}```', inline=False)
                    for mebi in c.execute(f"SELECT owner_club FROM user where id={author.id}"):
                        if mebi[0] == 0:
                            embed.add_field(name=f"{settings['club']} Клан:", value=f'```Отсутствует```', inline=False)
                        else: 
                            for mebi1 in c.execute(f"SELECT name FROM clan where owner={mebi[0]}"):
                                embed.add_field(name=f"{settings['club']} Клан:", value=f'```{mebi1[0]}```', inline=True)

                    embed.add_field(name=f"{settings['dney_server']} На сервере:", value=f'```{delta.days} дн.```', inline=False)
                    await interaction.send(embed=embed, ephemeral=True)

            
            author = interaction.user
            bot = self.bot

            timestamp = datetime.now().timestamp()
            todate = datetime.utcfromtimestamp(timestamp).strftime('%m/%d/%Y')


            rdate = user.joined_at.strftime('%m/%d/%Y')
            

            date_format = "%m/%d/%Y"
            a1 = datetime.strptime(rdate, date_format) 
            b1 = datetime.strptime(todate, date_format)
            delta = b1 - a1

            if member == None:
                def top(top : int):
                    index = []
                    for voice in profile.execute(f"SELECT id FROM profile where guild_id = {interaction.guild.id} ORDER BY voice DESC LIMIT {top}"):

                        index.append(voice[0])

                    try:
                        score = index.index(interaction.user.id) + 1
                        index.index(interaction.user.id) 
                    except ValueError:
                        score = "Вне топа"
                    return score
            else:
                def top(top : int):
                    index = []
                    for voice in profile.execute(f"SELECT id FROM profile where guild_id = {interaction.guild.id} ORDER BY voice DESC LIMIT {top}"):

                        index.append(voice[0])

                    try:
                        score = index.index(member.id) + 1
                        index.index(member.id) 
                    except ValueError:
                        score = "Вне топа"
                    return score

            
                
            rt = relativedelta(seconds=profile.execute(f"SELECT voice FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0])
            voice = round(int(profile.execute(f"SELECT voice FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]) // 3600, 0)
            name = user.display_name
            avatar = user.display_avatar.url
            marry_user = interaction.guild.get_member(int(mr.execute(f"SELECT user FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],))
            for css in c.execute(f"SELECT owner_club FROM user WHERE id={user.id}"):
                if  mr.execute(f"SELECT user FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0 and css[0] == 0:
                    
                    ad = await proc(avatar, name, voice,
                    str(profile.execute(f"SELECT txt FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                    
                    str(ec.execute(f"SELECT bal FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                    
                    profile.execute(f"SELECT status FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                    
                    str(pec.execute(f"SELECT bal FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                    
                    profile.execute(f"SELECT vk FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                    
                    profile.execute(f"SELECT tg FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 

                    profile.execute(f"SELECT inst FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],

                    delta.days,

                    top(1000),

                    lvl.execute(f"SELECT lvl FROM level WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0])

            

                elif  mr.execute(f"SELECT user FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0 and css[0] > 0:
                    for css1 in c.execute(f"SELECT name, avatar FROM clan WHERE owner={css[0]}"):
                        ad = await proc2(avatar, name, voice,
                        str(profile.execute(f"SELECT txt FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                        
                        str(ec.execute(f"SELECT bal FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                        
                        profile.execute(f"SELECT status FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                        
                        str(pec.execute(f"SELECT bal FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                        
                        profile.execute(f"SELECT vk FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                        
                        profile.execute(f"SELECT tg FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 

                        profile.execute(f"SELECT inst FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],

                        delta.days,

                        top(1000),

                        lvl.execute(f"SELECT lvl FROM level WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],

                        str(css1[1]),

                        str(css1[0]))
                    
                            
                elif  mr.execute(f"SELECT user FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] > 0 and css[0] == 0:

                    ad = await proc(avatar, name, voice,
                    str(profile.execute(f"SELECT txt FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                    
                    str(ec.execute(f"SELECT bal FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                    
                    profile.execute(f"SELECT status FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                    
                    str(pec.execute(f"SELECT bal FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                    
                    profile.execute(f"SELECT vk FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                    
                    profile.execute(f"SELECT tg FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 

                    profile.execute(f"SELECT inst FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],

                    delta.days,

                    top(1000),

                    lvl.execute(f"SELECT lvl FROM level WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],

                    marry_user.display_avatar.url,

                    marry_user.display_name

                    )

                
                elif  mr.execute(f"SELECT user FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] > 0 and css[0] > 0:
                    for css1 in c.execute(f"SELECT name, avatar FROM clan WHERE owner={css[0]}"):
                        ad = await proc(avatar, name, voice,
                        str(profile.execute(f"SELECT txt FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                        
                        str(ec.execute(f"SELECT bal FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                        
                        profile.execute(f"SELECT status FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                        
                        str(pec.execute(f"SELECT bal FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                        
                        profile.execute(f"SELECT vk FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                        
                        profile.execute(f"SELECT tg FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 

                        profile.execute(f"SELECT inst FROM profile WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],

                        delta.days,

                        top(1000),

                        lvl.execute(f"SELECT lvl FROM level WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],

                        marry_user.display_avatar.url,

                        marry_user.display_name,

                        str(css1[1]),

                        str(css1[0]))
                    
                await interaction.response.defer()
                await interaction.send(file=nextcord.File(ad), view=edit())
            
        
        else:

            
            if mr.execute(f"SELECT user FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0: 
                if interaction.user. id == user.id:
                    embed=nextcord.Embed(description="У вас нету пары", color=0x2b2d31)
                    embed.set_thumbnail(url=interaction.user.display_avatar)
                    embed.set_footer(text=f"Для заключения брака требуется {cost} коинов")
                    await interaction.send(embed=embed, ephemeral=True)
                else:
                    embed=nextcord.Embed(description=f"У {user.mention} нету пары", color=0x2b2d31)
                    embed.set_thumbnail(url=interaction.user.display_avatar)
                    embed.set_footer(text=f"Для заключения брака требуется {cost} коинов")
                    await interaction.send(embed=embed, ephemeral=True)                  
            else:

                name = user.display_name
                avatar = user.display_avatar.url
                marry_user = interaction.guild.get_member(int(mr.execute(f"SELECT user FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]))
                
                class edit(nextcord.ui.View):
                    def __init__(self):
                        super().__init__(timeout=60)
                        
                    

                    if user.id != interaction.user.id:
                        @nextcord.ui.button(label = '', emoji='<:edit:1061207203790454794> ', style = nextcord.ButtonStyle.grey, disabled=True)
                        async def edit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                            pass
                    else:
                        @nextcord.ui.button(label = '', emoji='<:edit:1061207203790454794> ', style = nextcord.ButtonStyle.grey)
                        async def edit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                            if owner.id == interaction.user.id:




                                class marryset(nextcord.ui.View):
                                    def __init__(self):
                                        super().__init__(timeout=60)

                                    
                                    @nextcord.ui.button(label = 'Установить цитату',style = nextcord.ButtonStyle.grey)
                                    async def status(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                        if owner.id == interaction.user.id:
                                            class profileplus(nextcord.ui.Modal):
                                                def __init__(self):
                                                    
                                                    super().__init__('Установить цитату')

                                                    self.status = nextcord.ui.TextInput(label = 'Укажи новую цитату', min_length=1, max_length=150, required=True, placeholder='Только давай без пошлостей')
                                                    self.add_item(self.status)


                                                async def callback(self, interaction: nextcord.Interaction) -> None:
                                                    stat = self.status.value



                                                    mr.execute(f"UPDATE marry SET quote='{stat}' where id={interaction.user.id} and guild_id={interaction.guild.id}")
                                                    mr_db.commit()

                                                    emb = nextcord.Embed(description=f'Ваша новая цитата: `{stat}`', color = 0x2b2d31)
                                                    emb.set_thumbnail(url=interaction.user.display_avatar)
                                                    
                                                    await interaction.send(embed=emb, ephemeral = True)
                                            
                                            await interaction.response.send_modal(profileplus())
                                            return
                                        else:
                                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                                            await interaction.send(embed=embed, ephemeral= True)

                                    @nextcord.ui.button(label = 'Установить баннер', style = nextcord.ButtonStyle.grey)
                                    async def banner(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                        if owner.id == interaction.user.id:
                                            class profileplus(nextcord.ui.Modal):
                                                def __init__(self):
                                                    super().__init__('Установить баннер')

                                                    self.status = nextcord.ui.TextInput(label = 'Укажи ссылку на новый баннер', min_length=1, max_length=2000, required=True, placeholder='Жду')
                                                    self.add_item(self.status)


                                                async def callback(self, interaction: nextcord.Interaction) -> None:
                                                    stat = self.status.value


                                                    mr.execute(f"UPDATE marry SET banner='{stat}' where id={interaction.user.id} and guild_id={interaction.guild.id}")
                                                    mr_db.commit()

                                                    emb = nextcord.Embed(description=f'Ваш новый баннер: `{stat}`', color = 0x2b2d31)
                                                    
                                                    emb.set_image(url=stat)
                                                    emb.set_thumbnail(url=interaction.user.display_avatar)
                                                    await interaction.send(embed=emb, ephemeral = True)

                                        
                                            await interaction.response.send_modal(profileplus())
                                            return
                                        else:
                                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                                            await interaction.send(embed=embed, ephemeral= True)                                
                                    
                                    if mr.execute(f"SELECT banner FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 'none':

                                        @nextcord.ui.button(label = 'Удалить баннер', style = nextcord.ButtonStyle.grey, disabled=True)
                                        async def deletebanner(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                            pass
                                    else:
                                        @nextcord.ui.button(label = 'Удалить баннер', style = nextcord.ButtonStyle.grey, disabled = False)
                                        async def deletebanner(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                            if owner.id == interaction.user.id:
                                                
                                                if mr.execute(f"SELECT banner FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 'none':
                                                    emb = nextcord.Embed(description=f'Баннер уже был удален', color = 0x2b2d31)
                                                    emb.set_thumbnail(url=interaction.user.display_avatar)
                                                    await interaction.send(embed=emb, ephemeral = True)
                                                else:
                                                    self.deletebanner.disabled = True
                                                    await interaction.response.edit_message(view=self)
                                                    mr.execute(f"UPDATE marry SET banner='none' where id={interaction.user.id} and guild_id={interaction.guild.id}")
                                                    mr_db.commit()

                                                    emb = nextcord.Embed(description=f'Вы успешно удалили баннер', color = 0x2b2d31)
                                                    emb.set_thumbnail(url=interaction.user.display_avatar)
                                                    await interaction.send(embed=emb, ephemeral = True)

                                                    
                                                    

                                                    
                                                
                                                
                                            else:
                                                embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                await interaction.send(embed=embed, ephemeral= True)                                             

                                    if mr.execute(f"SELECT quote FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 'none':

                                        @nextcord.ui.button(label = 'Удалить цитату', style = nextcord.ButtonStyle.grey, disabled=True)
                                        async def deletestatus(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                            pass
                                    else:
                                        @nextcord.ui.button(label = 'Удалить цитату', style = nextcord.ButtonStyle.grey, disabled=False)
                                        async def deletestatus(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                            if owner.id == interaction.user.id:

                                                self.deletestatus.disabled = True
                                                await interaction.response.edit_message(view=self)

                                                mr.execute(f"UPDATE marry SET quote='none' where id={interaction.user.id} and guild_id={interaction.guild.id}")
                                                mr_db.commit()

                                                emb = nextcord.Embed(description=f'Вы успешно удалили цитату', color = 0x2b2d31)
                                                emb.set_thumbnail(url=interaction.user.display_avatar)
                                                await interaction.send(embed=emb, ephemeral = True)

                                                    
                                                
                                                
                                            else:
                                                embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                await interaction.send(embed=embed, ephemeral= True)    

                                    @nextcord.ui.button(label = 'Пополнить баланс',style = nextcord.ButtonStyle.grey)
                                    async def pay(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                        if owner.id == interaction.user.id:
                                            class profileplus(nextcord.ui.Modal):
                                                def __init__(self):
                                                    super().__init__('Пополнить баланс')

                                                    self.status = nextcord.ui.TextInput(label = 'Укажи сумму пополнения', min_length=1, max_length=150, required=True, placeholder='100')
                                                    self.add_item(self.status)


                                                async def callback(self, interaction: nextcord.Interaction) -> None:
                                                    stat = self.status.value
                                                    var = stat.isdigit()
                                                    if var == True:

                                                        class god(nextcord.ui.View):
                                                            def __init__(self):
                                                                super().__init__(timeout=60)
                                                                
                                                            
                                                            @nextcord.ui.button(label = 'Да',style = nextcord.ButtonStyle.grey)
                                                            async def yes(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                                                if int(stat) > ec.execute("SELECT bal FROM balance where id = {} and guild_id = {}".format(interaction.user.id, interaction.guild.id)).fetchone()[0]:
                                                                    embed = nextcord.Embed(description = f'Недостаточно средств', color=0x2b2d31)
                                                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                                    await msg.edit(embed=embed, view=None)            
                                                                else:
                                                                    people_id = mr.execute("SELECT user FROM marry where id = {} and guild_id = {}".format(interaction.user.id, interaction.guild.id)).fetchone()[0]
                                                                    people = interaction.guild.get_member(people_id)
                                                                    mr.execute(f'UPDATE marry SET balance=balance+{int(stat)} where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                                                    mr.execute(f'UPDATE marry SET balance=balance+{int(stat)} where id={people.id} and guild_id={interaction.guild.id}')
                                                                    mr_db.commit()
                                                                    
                                                                    ec.execute(f'UPDATE balance SET bal=bal - {int(stat)} where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                                                    ec_db.commit()

                                                                    embed = nextcord.Embed(description = f'Вы успешно пополнили баланс своей пары на `{stat}` коинов', color=0x2b2d31)
                                                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                                    await msg.edit(embed=embed, view=None)

                                                            @nextcord.ui.button(label = 'Нет',style = nextcord.ButtonStyle.grey)
                                                            async def no(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                                                embed = nextcord.Embed(description = f'Действие обновлено: `"Ваша заявка на пополнения баланса была аннулирована"`', color=0x2b2d31)
                                                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                                await msg.edit(embed=embed, view=None)

                                                        embed = nextcord.Embed(description = f'Вы точно хотите, пополнить баланс своего любовного профиля на `{stat} коинов?`\r`Напоминаю вам`, после **пополнения** любовного баланса, вы больше не сможете **снять оттуда деньги** и по истечению срока, **если ваш брак не сможет быть продлен**, то данные деньги **сгорят**.', color=0x2b2d31)
                                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                        msg = await interaction.send(embed=embed, ephemeral= True, view=god())
                                                    else:
                                                        embed = nextcord.Embed(description = f'**Входные данные** должны быть в формате **целых чисел** и **положительных чисел**', color=0x2b2d31)
                                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                        await interaction.send(embed=embed, ephemeral= True)

                                                    
                                            
                                            await interaction.response.send_modal(profileplus())
                                            return
                                        else:
                                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                                            await interaction.send(embed=embed, ephemeral= True)

                                    @nextcord.ui.button(label = 'Назад', style = nextcord.ButtonStyle.red)
                                    async def back(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                        if owner.id == interaction.user.id:

                                            timestamp = datetime.now().timestamp()

                                            todate = datetime.utcfromtimestamp(timestamp).strftime('%m/%d/%Y')


                                            rdate = datetime.utcfromtimestamp(int(mr.execute(f"SELECT registration FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0])).strftime('%m/%d/%Y')
                                            

                                            date_format = "%m/%d/%Y"
                                            a1 = datetime.strptime(rdate, date_format) 
                                            b1 = datetime.strptime(todate, date_format)
                                            delta = b1 - a1

                                            a = await love(avatar, marry_user.display_avatar.url, str(mr.execute(f"SELECT balance FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), delta.days, registration

                                            )
                                            
                                            await interaction.response.defer()
                                            await main.edit(file=nextcord.File(a), embed=None, view=edit())
                                            
                                        else:
                                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                                            await interaction.send(embed=embed, ephemeral= True)          

                                emb=nextcord.Embed(description="Укажите свое действие:", color=0x2b2d31)
                                emb.set_thumbnail(url=interaction.user.display_avatar)
                                await main.edit(embed=emb, view=marryset())
                            else:
                                embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                await interaction.send(embed=embed, ephemeral= True)

                    @nextcord.ui.button(label = '', emoji='<:104345:1081868463313793064>', style = nextcord.ButtonStyle.grey)
                    async def info(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):

                        registration = datetime.utcfromtimestamp(int(mr.execute(f"SELECT registration FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0])).strftime('%d.%m.%Y')
                        dater = datetime.utcfromtimestamp(int(task.execute("SELECT date FROM tasks where id = {} and guild_id = {} and name= '{}'".format(interaction.user.id, interaction.guild.id, 'marry')).fetchone()[0])).strftime('%d.%m.%Y')
                        
                        timestamp = datetime.now().timestamp()

                        todate = datetime.utcfromtimestamp(timestamp).strftime('%m/%d/%Y')


                        rdate = datetime.utcfromtimestamp(int(mr.execute(f"SELECT registration FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0])).strftime('%m/%d/%Y')
                        

                        date_format = "%m/%d/%Y"
                        a1 = datetime.strptime(rdate, date_format) 
                        b1 = datetime.strptime(todate, date_format)
                        delta = b1 - a1


                        g = interaction.guild.get_member(mr.execute(f"SELECT user FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0])


                        wallet1 = bot.get_emoji(1070326206559424533) 
                        infinity1 = bot.get_emoji(1070333287588974622) 
                        notepad1 = bot.get_emoji(1070334403546456088) 
                        hearts1 = bot.get_emoji(1070336454175248465) 

                        embed=nextcord.Embed(title=f"Любовынй профиль пользователя —  {user}", color=0x2b2d31)
                        embed.add_field(name=f"{settings['partner']} Партнер", value=f"```{g}```", inline=False)
                        embed.add_field(name=f"{settings['regestration']} Регистрация", value=f"```{registration}```", inline=True)
                        embed.add_field(name=f"{settings['balance']} Баланс", value="```{}```".format(mr.execute(f"SELECT balance FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), inline=True)
                        embed.add_field(name=f"{settings['prodlenie']} Продление", value=f"```{dater}```", inline=True)
                        if mr.execute(f"SELECT quote FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] != 'none':
                            embed.add_field(name=f"{settings['citata']} Цитата", value='```{}```'.format(mr.execute(f"SELECT quote FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), inline=False)
                        else:
                            embed.add_field(name=f"{settings['citata']} Цитата", value=f'```Не установлена```', inline=False)
                        embed.add_field(name=f"{settings['dney_vmeste']} Всего вместе", value=f'```{delta.days} дн.```', inline=False)

                        if mr.execute(f"SELECT banner FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] != 'none':
                            embed.set_image(url=mr.execute(f"SELECT banner FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0])

                        embed.set_thumbnail(url=interaction.user.display_avatar)
                        await interaction.send(embed=embed, ephemeral=True)
        
                registration = datetime.utcfromtimestamp(int(mr.execute(f"SELECT registration FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0])).strftime('%d.%m.%Y')
                dater = datetime.utcfromtimestamp(int(task.execute("SELECT date FROM tasks where id = {} and guild_id = {} and name= '{}'".format(interaction.user.id, interaction.guild.id, 'marry')).fetchone()[0])).strftime('%d.%m.%Y')
                
                timestamp = datetime.now().timestamp()

                todate = datetime.utcfromtimestamp(timestamp).strftime('%m/%d/%Y')


                rdate = datetime.utcfromtimestamp(int(mr.execute(f"SELECT registration FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0])).strftime('%m/%d/%Y')
                

                date_format = "%m/%d/%Y"
                a1 = datetime.strptime(rdate, date_format) 
                b1 = datetime.strptime(todate, date_format)
                delta = b1 - a1

                a = await love(avatar, marry_user.display_avatar.url, str(mr.execute(f"SELECT balance FROM marry WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), delta.days, registration, dater)
                
                await interaction.response.defer()
                main = await interaction.send(file=nextcord.File(a), view=edit())


    @nextcord.slash_command(description="Начать отношения")
    async def marry(self, interaction: nextcord.Interaction, member: nextcord.Member):
        bot = self.bot
        owner = interaction.user
        guild = interaction.guild
        cost = settings['cost_marry']
        male = interaction.guild.get_role(settings['male'])
        female = interaction.guild.get_role(settings['female'])
        if int(cost) > ec.execute("SELECT bal FROM balance where id = {} and guild_id = {}".format(interaction.user.id, interaction.guild.id)).fetchone()[0]:
            embed=nextcord.Embed(description = f"Для заключения брака, тебе требуется {cost} коинов", color=0x2b2d31)
            await interaction.send(embed = embed, ephemeral=True)  
        else:
            
            bloop = datetime.now().timestamp()
            for m_user in mr.execute(f'SELECT user FROM marry where id = {member.id} and guild_id={interaction.guild.id}'):
                if m_user[0] == 0:
                    if member.id == interaction.user.id:
                        emb = nextcord.Embed(description=f'Нельзя выполнить данную команду на себе))', color = 0x2b2d31)
                        emb.set_thumbnail(url=interaction.user.display_avatar)
                        await interaction.send(embed=emb, ephemeral=True) 
                    elif member.id == bot.user.id:
                        emb = nextcord.Embed(description=f'Извини, но я уже в браке с девелопером))', color = 0x2b2d31)
                        emb.set_thumbnail(url=interaction.user.display_avatar)
                        await interaction.send(embed=emb, ephemeral=True) 
                    else:

                        
                        class action(nextcord.ui.View):
                            def __init__(self):
                                super().__init__(timeout=None)

                            @nextcord.ui.button(label = 'Да', style = nextcord.ButtonStyle.green, row = False)
                            async def yes(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):

                                if settings["loveroom_mode"] == "OFF":
                                    emb = nextcord.Embed(description=f'Ух ты... У нас новая пара', color = 0x2b2d31)
                                    await interaction.edit(embed=emb, view=None)

                                    mr.execute(f"UPDATE marry SET registration = {bloop} where id={owner.id} and guild_id={guild.id}")
                                    mr.execute(f"UPDATE marry SET registration = {bloop} where id={interaction.user.id} and guild_id={guild.id}")
                                    
                                    mr.execute(f"UPDATE marry SET user={interaction.user.id} where id={owner.id} and guild_id={guild.id}")
                                    mr.execute(f"UPDATE marry SET user={owner.id} where id={interaction.user.id} and guild_id={guild.id}")

                                    mr_db.commit()
                                    try:
                                        emb1 = nextcord.Embed(description=f'Мои поздравления, вы теперь с {interaction.user.mention} состоите в браке', color = 0x2b2d31)
                                        await owner.send(embed=emb1) 
                                    except:
                                        emb1 = nextcord.Embed(description=f'Ваш брак был заключен, но вот у твоей второй половинки закрыт лс. И из-за этого я не могу сообщить об этом. Пожалуйста, сделай это за меня))', color = 0x2b2d31)
                                        await interaction.send(embed=emb1)            
                                else:
                                    emb = nextcord.Embed(description=f'Ух ты... У нас новая пара. Так как на данном сервере включены любовные комнаты, то я для вас создала вашу Любовную Комнату', color = 0x2b2d31)
                                    await interaction.edit(embed=emb, view=None)
                                    
                                    mr.execute(f"UPDATE marry SET registration = {bloop} where id={owner.id} and guild_id={guild.id}")
                                    mr.execute(f"UPDATE marry SET registration = {bloop} where id={interaction.user.id} and guild_id={guild.id}")

                                    mr.execute(f"UPDATE marry SET user={interaction.user.id} where id={owner.id} and guild_id={guild.id}")
                                    mr.execute(f"UPDATE marry SET user={owner.id} where id={interaction.user.id} and guild_id={guild.id}")
                                    overwrites = {
                                        guild.default_role: nextcord.PermissionOverwrite(connect=False),
                                        
                                    }
                                    
                                    if settings["loveroom_mode"] == "OFF":
                                        voice = await guild.create_voice_channel(f"{interaction.user.name}・{owner.name}",overwrites = overwrites, category=None)
                                        await voice.set_permissions(owner, connect = True)
                                        await voice.set_permissions(interaction.user, connect = True)
                                        await voice.edit(user_limit=2)
                                        try:
                                            emb1 = nextcord.Embed(description=f'Мои поздравления, вы теперь с {interaction.user.mention} состоите в браке', color = 0x2b2d31)
                                            await owner.send(embed=emb1) 
                                        except:
                                            emb1 = nextcord.Embed(description=f'Ваш брак был заключен, но вот у твоей второй половинки закрыт лс. И из-за этого я не могу сообщить об этом. Пожалуйста, сделай это за меня))', color = 0x2b2d31)
                                            await interaction.send(embed=emb1)  
                                        mr.execute(f"UPDATE marry SET marry_channel={voice.id} where id={interaction.user.id} and guild_id={guild.id}")
                                        mr.execute(f"UPDATE marry SET marry_channel={voice.id} where id={owner.id} and guild_id={guild.id}")
                                        mr_db.commit()
                                    else:
                                        cat = nextcord.utils.get(guild.categories, id=int(settings["loverooms"]))
                                        voice = await guild.create_voice_channel(f"{interaction.user.name}・{owner.name}",overwrites = overwrites, category=cat)
                                        await voice.set_permissions(owner, connect = True)
                                        await voice.set_permissions(interaction.user, connect = True)
                                        await voice.edit(user_limit=2)
                                        try:
                                            emb1 = nextcord.Embed(description=f'Мои поздравления, вы теперь с {interaction.user.mention} состоите в браке', color = 0x2b2d31)
                                            await owner.send(embed=emb1) 
                                        except:
                                            emb1 = nextcord.Embed(description=f'Ваш брак был заключен, но вот у твоей второй половинки закрыт лс. И из-за этого я не могу сообщить об этом. Пожалуйста, сделай это за меня))', color = 0x2b2d31)
                                            await interaction.send(embed=emb1) 
                                            
                                        mr.execute(f"UPDATE marry SET marry_channel={voice.id} where id={interaction.user.id} and guild_id={guild.id}")
                                        mr.execute(f"UPDATE marry SET marry_channel={voice.id} where id={owner.id} and guild_id={guild.id}")
                                        mr_db.commit()
                                floot = (datetime.now() + timedelta(days=30)).timestamp()
                                
                                task.execute(f"INSERT INTO tasks VALUES ('marry','{floot}','{interaction.user.id}', '{guild.id}')")
                                task.execute(f"INSERT INTO tasks VALUES ('marry','{floot}','{owner.id}', '{guild.id}')")
                                task_db.commit()
                                await m.edit(view=closs()) 

                            @nextcord.ui.button(label = 'Нет', custom_id="no", style = nextcord.ButtonStyle.red, row = False, disabled=False)
                            async def no(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                await m.edit(view=closs())
                                emb = nextcord.Embed(description=f'Жалко, но я передам ваш ответ', color = 0x2b2d31)
                                await interaction.send(embed=emb)
                                
                                try:
                                    emb1 = nextcord.Embed(description=f'{interaction.user.mention} отказал(а) вам браке', color = 0x2b2d31)
                                    await owner.send(embed=emb1) 
                                except:
                                    emb1 = nextcord.Embed(description=f'Я не смогла сообщить об вашем отказе, так как у {owner.name} закрыт лс. Сделайте это за меня, пожалуйста', color = 0x2b2d31)
                                    await interaction.send(embed=emb1)                   
                            

                        emb = nextcord.Embed(description=f'Пользователь {interaction.user.mention} предложил(а) вам начать отношения, вы согласны?', color = 0x2b2d31)
                        global m
                        m = await member.send(embed=emb, view=action())
                        ec.execute("UPDATE balance SET bal = bal - {} where id = {} and guild_id = {}".format(600, interaction.user.id, interaction.guild.id))
                        try:
                            emb1 = nextcord.Embed(description=f'Я отправила ваше сообщение. Теперь ждем ответа', color = 0x2b2d31)
                            emb1.set_thumbnail(url=interaction.user.display_avatar)
                            await interaction.send(embed=emb1, ephemeral=True) 
                        except:
                            emb1 = nextcord.Embed(description=f'Я не смогла отправить ваше сообщение, так как у данного человека закрыт лс. И из-за этого ваш брак не может быть заключен (', color = 0x2b2d31)
                            await interaction.send(embed=emb1, ephemeral=True) 
                        ec_db.commit()
                else: 
                    er=nextcord.Embed(description="Ну так не годится! Пользователь уже состоит в браке", color=0x2b2d31)
                    er.set_thumbnail(url=interaction.user.display_avatar)
                    
                    await interaction.send(embed=er, ephemeral = True)    
     
    @nextcord.slash_command(description="Разорвать отношения")
    async def unmarry(self, interaction: nextcord.Interaction):
        class unmarry(nextcord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)
            

            @nextcord.ui.button(label = 'Да', style = nextcord.ButtonStyle.grey, disabled=False)
            async def yes(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                marry_user = interaction.guild.get_member(int(mr.execute(f"SELECT user FROM marry WHERE id={interaction.user.id} and guild_id={interaction.guild.id} ").fetchone()[0]))
                marry_channel = interaction.guild.get_channel(int(mr.execute(f"SELECT marry_channel FROM marry WHERE id={interaction.user.id} and guild_id={interaction.guild.id} ").fetchone()[0]))
                await marry_channel.delete()
                mr.execute(f"DELETE FROM marry where user={interaction.user.id}")
                mr.execute(f"DELETE FROM marry where user={marry_user.id}")

                task.execute(f"DELETE FROM tasks where id={marry_user.id} and name= 'marry'")
                task.execute(f"DELETE FROM tasks where id={interaction.user.id} and name= 'marry'")

                mr.execute(f"INSERT INTO marry VALUES ('{marry_user.id}', '{interaction.guild.id}', 0, 0, 0, 0, 'none', 'none', 0)")
                mr.execute(f"INSERT INTO marry VALUES ('{interaction.user.id}', '{interaction.guild.id}', 0, 0, 0, 0, 'none', 'none', 0)")

                er=nextcord.Embed(description="Вы успешно расстались со своей парой", color=0x2b2d31)
                er.set_thumbnail(url=interaction.user.display_avatar)

                er1=nextcord.Embed(description="Ваша вторая половинка, решила расстаться с вами (", color=0x2b2d31)
                er1.set_thumbnail(url=interaction.user.display_avatar)
                try:
                    await marry_user.send(embed=er1)
                except:
                    pass

                await main.edit(embed=er, view=None)   

                task_db.commit()
                mr_db.commit()



            @nextcord.ui.button(label = 'Нет', style = nextcord.ButtonStyle.grey, disabled=False)
            async def no(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                er=nextcord.Embed(description="Команда была отменена", color=0x2b2d31)
                er.set_thumbnail(url=interaction.user.display_avatar)
                
                await main.edit(embed=er,view=None)   

        er=nextcord.Embed(description="Вы точно хотите расстаться со своей парой?", color=0x2b2d31)
        er.set_thumbnail(url=interaction.user.display_avatar)
                
        main =await interaction.send(embed=er, view=unmarry(), ephemeral = True)         






                   
def setup(bot):
    bot.add_cog(profilev2(bot))