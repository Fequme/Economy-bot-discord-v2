
import nextcord
from nextcord.ext import commands
import sqlite3
from config import *
import asyncio
from nextcord.ext import application_checks, commands, menus

class update(nextcord.ui.Modal):
    def __init__(self):
        super().__init__('Update')

        self.EmTitle = nextcord.ui.TextInput(label = 'Версия', min_length=1, max_length=20, required=True, placeholder='1.0.0 Beta')
        self.add_item(self.EmTitle)

        self.EmDescription = nextcord.ui.TextInput(label = 'Название обновления', min_length=1, max_length=120, required=True, placeholder='Магазин', style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.EmDescription)

        self.EmFooter = nextcord.ui.TextInput(label = 'Новые команды', min_length=1, max_length=2000, required=True, placeholder='Тут новые команды указываются', style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.EmFooter)

        self.EmImage = nextcord.ui.TextInput(label = 'Изменения:', min_length=1, max_length=2000, required=True, placeholder='Тут что было обновлено', style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.EmImage)

        self.EmImage1 = nextcord.ui.TextInput(label = 'Версия 2:', min_length=1, max_length=100, required=True, placeholder='Версия для удаления', style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.EmImage1)
        


        




    async def callback(self, interaction: nextcord.Interaction) -> None:
        up_db = sqlite3.connect('database/bot.db', timeout=10)
        up = up_db.cursor()        
        title = self.EmTitle.value
        description = self.EmDescription.value
        footer = self.EmFooter.value
        image = self.EmImage.value
        image1 = self.EmImage1.value
        emb = nextcord.Embed(description='Успешно добавила в базу данных!', color = 0x2b2d31)
        up.execute(f"INSERT INTO updates VALUES ('{title}', '{description}', '{footer}', '{image}', '{image1}')")
        up_db.commit()
        await interaction.send(embed=emb)

class updatedel(nextcord.ui.Modal):
    def __init__(self):
        super().__init__('Update delete')

        self.EmTitle = nextcord.ui.TextInput(label = 'Версия', min_length=1, max_length=20, required=True, placeholder='1.0.0 Beta')
        self.add_item(self.EmTitle)


        


        




    async def callback(self, interaction: nextcord.Interaction) -> None:
        up_db = sqlite3.connect('database/bot.db', timeout=10)
        up = up_db.cursor()        
        title = self.EmTitle.value
        emb = nextcord.Embed(description='Успешно удалила из базы данных!', color = 0x2b2d31)
        up.execute(
            f"DELETE FROM updates where version={title}")
        up_db.commit()
        await interaction.send(embed=emb) 

px = settings['prefix']

pr_db = sqlite3.connect('database/private.db', timeout=10)
pr = pr_db.cursor()

wl_db = sqlite3.connect('database/welcome.db', timeout=10)
wl = wl_db.cursor()
class CustomButtonMenuPages(menus.ButtonMenuPages, inherit_buttons=False):


    def __init__(self, source, timeout=60):
        super().__init__(source, timeout=timeout)


        self.add_item(menus.MenuPaginationButton(emoji=self.FIRST_PAGE, label=""))
        self.add_item(menus.MenuPaginationButton(emoji=self.PREVIOUS_PAGE, label=""))
        self.add_item(menus.MenuPaginationButton(emoji=self.NEXT_PAGE, label=""))
        self.add_item(menus.MenuPaginationButton(emoji=self.LAST_PAGE, label=""))


        self.children = self.children[1:] + self.children[:1]


        self._disable_unavailable_buttons()


    @nextcord.ui.button(emoji="\N{BLACK SQUARE FOR STOP}", label="")
    async def stop_button(self, button, interaction):
        await interaction.response.send_message("Пагинация успешна была остановлена.", ephemeral=True)
        self.stop()
class embedmodule(nextcord.ui.Modal):
    def __init__(self):
        super().__init__('Создание Embed для Welcome')

        self.EmTitle = nextcord.ui.TextInput(label = 'Title', min_length=1, max_length=124, required=False, placeholder='Оставь пустым, если не хочешь включать')
        self.add_item(self.EmTitle)

        self.EmDescription = nextcord.ui.TextInput(label = 'Description', min_length=1, max_length=4000, required=False, placeholder='Оставь пустым, если не хочешь включать', style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.EmDescription)

        self.EmFooter = nextcord.ui.TextInput(label = 'Footer', min_length=1, max_length=25, required=False, placeholder='Оставь пустым, если не хочешь включать', style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.EmFooter)

        self.EmImage = nextcord.ui.TextInput(label = 'Image', min_length=1, max_length=4000, required=False, placeholder='Url (Оставь пустым, если не хочешь включать)', style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.EmImage)
        




        




    async def callback(self, interaction: nextcord.Interaction) -> None:
        title = self.EmTitle.value
        description = self.EmDescription.value
        footer = self.EmFooter.value
        image = self.EmImage.value
        emb = nextcord.Embed(title=title, description=description, color = 0x2b2d31)
        emb.set_footer(text=footer)
        emb.set_image(url=image)
        wl.execute(f"UPDATE embed SET title='{title}' where guild_id={interaction.guild.id}")
        wl.execute(f"UPDATE embed SET description='{description}' where guild_id={interaction.guild.id}")
        wl.execute(f"UPDATE embed SET footer='{footer}' where guild_id={interaction.guild.id}")
        wl.execute(f"UPDATE embed SET image='{image}' where guild_id={interaction.guild.id}")
        wl_db.commit()
        emb1 = nextcord.Embed(description='Ваш welcome будет выглять вот так (вместо упоминания вас, будет упоминаться новый участник):', color = 0x2b2d31)
        await interaction.send(embed=emb1)
        await interaction.channel.send(interaction.user.mention, embed=emb)

class limka(nextcord.ui.Modal):
    def __init__(self):
        super().__init__('Смена лимита')

        self.limit = nextcord.ui.TextInput(label = 'Укажи новый лимит. 0 что бы снять лимит.', min_length=1, max_length=3, required=True, placeholder='жду^^', style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.limit)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        title = self.limit.value
        for row in pr.execute(f"SELECT channel, mode FROM private where id={interaction.user.id}"):
            channel = interaction.guild.get_channel(row[0])
            await channel.edit(user_limit=title)
        
class name(nextcord.ui.Modal):
    def __init__(self):
        super().__init__('Смена названия')

        self.limit = nextcord.ui.TextInput(label = 'Укажи новые название', min_length=1, max_length=45, required=True, placeholder='жду^^', style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.limit)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        title = self.limit.value
        for row in pr.execute(f"SELECT channel, mode FROM private where id={interaction.user.id}"):
            channel = interaction.guild.get_channel(row[0])
            await channel.edit(name=title)


class settings(commands.Cog):
    """ Модуль `настройки` | Команды данного модуля """

    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description="Настройка бота", guild_ids = [int(settings["Guild_ID"])])
    @application_checks.has_permissions(administrator=True)
    async def settings(self, interaction: nextcord.Interaction):
        bot = self.bot
        global owner
        owner = interaction.user.id

        overwrites = {
            interaction.guild.default_role: nextcord.PermissionOverwrite(send_messages=True),
            }
        

        class moduleeconomy(nextcord.ui.View):

            def __init__(self):
                super().__init__(timeout=60)

            @nextcord.ui.button(label = 'Изменить валюту', style = nextcord.ButtonStyle.grey)
            async def currency(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if owner == interaction.user.id:
                    ec_db = sqlite3.connect('database/economy.db', timeout=10)
                    ec = ec_db.cursor()    
                    embed = nextcord.Embed(title="Установка валюты",
                                        description=f'Укажи id эмодзи', color=0x2b2d31)
                    
                    await interaction.send(embed=embed)
                    
                    try:
                        msg = await bot.wait_for('message', timeout= 30, check=lambda m: m.author.id == interaction.user.id)
                        s1 = msg.content
                        id1 = int(s1)
                        try:
                            t133 = bot.get_emoji(id1)
                            ec.execute(f"UPDATE settings SET currency='{id1}' where guild_id={interaction.guild.id}")
                            

                            embed = nextcord.Embed(
                                title="Установка валюты", description=f'Эмодзи {t133} теперь является новой валютой сервера', color=0x2b2d31)
                            
                            await interaction.send(embed=embed)       
                            ec_db.commit()
                        except Exception as E: 
                            embed = nextcord.Embed(
                                title="Установка валюты", description=f'Неизвестная ошибка. Скорее всего ты пытаешься поставить эмодзи которой нету на сервере или вовсе это не **id emoji**', color=0x2b2d31)
                            
                            await interaction.send(embed=embed)   
                    except asyncio.exceptions.TimeoutError:
                        await interaction.send("Действия команды были отменены.")  
                else:
                    pass

            ec_db = sqlite3.connect('database/economy.db', timeout=10)
            ec = ec_db.cursor()     
            for rrr in ec.execute(f"SELECT currency FROM settings where guild_id={interaction.guild.id}"):
                if rrr[0] == 990154974019346522:
                    @nextcord.ui.button(label = 'Сбросить валюту', style = nextcord.ButtonStyle.grey, disabled=True)
                    async def remcurrency(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        pass
                else:
                    @nextcord.ui.button(label = 'Сбросить валюту', style = nextcord.ButtonStyle.grey, disabled=False)
                    async def remcurrency(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if owner == interaction.user.id:
                            ec_db = sqlite3.connect('database/economy.db', timeout=10)
                            ec = ec_db.cursor()  
                            ec.execute(f"UPDATE settings SET currency='990154974019346522' where guild_id={interaction.guild.id}")
                            embed = nextcord.Embed(
                                title="Сброс валюты", description=f'Валюта была успешно сброшена', color=0x2b2d31)
                            
                            await interaction.send(embed=embed)       
                            ec_db.commit()       
                        else:
                            pass                

            @nextcord.ui.button(label = 'Настройка команды /timely', style = nextcord.ButtonStyle.grey)
            async def settimely(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if owner == interaction.user.id:
                    ec_db = sqlite3.connect('database/economy.db', timeout=10)
                    ec = ec_db.cursor()
                    embed = nextcord.Embed(
                        title="Настройка команды /timely", description=f'Укажи минимальное количество валюты, которое будет даваться за использование команды', color=0x2b2d31)
                            
                    await interaction.send(embed=embed)   

                    try:
                        msg = await bot.wait_for('message', timeout= 30, check=lambda m: m.author.id == interaction.user.id)
                        s1 = msg.content
                        ot = int(s1)

                        embed = nextcord.Embed(
                            title="Настройка команды /timely", description=f'Укажи максимальное количество валюты, которое будет даваться за использование команды', color=0x2b2d31)
                                
                        await interaction.send(embed=embed)  

                        msg = await bot.wait_for('message', timeout= 30, check=lambda m: m.author.id == interaction.user.id)
                        s12 = msg.content
                        do = int(s12)
                    
                        for em in ec.execute(f'SELECT currency FROM settings where guild_id={interaction.guild.id}'):
                            t1 = bot.get_emoji(em[0])
                            
                            if do < 0 or ot < 0:
                                embed = nextcord.Embed(
                                    title="Установка диапозона", description=f'Числа не должны быть меньше нолика ^^', color=0x2b2d31)
                                
                                await interaction.send(embed=embed)
                            else:
                                ec.execute(
                                    f"UPDATE settings SET timely_ot='{ot}' where guild_id={interaction.guild.id}")
                                ec.execute(
                                    f"UPDATE settings SET timely_do='{do}' where guild_id={interaction.guild.id}")
                                ec_db.commit()
                                embed = nextcord.Embed(
                                    title="Установка диапозона", description=f'Диапозон для команды `/timely` был усталовен успешно! Теперь игроки будут получать от {ot} до {do} {t1}', color=0x2b2d31)
                                
                                await interaction.send(embed=embed)

                    except asyncio.exceptions.TimeoutError:
                        await interaction.send("Действия команды были отменены.")  
                else:
                    pass

            @nextcord.ui.button(label = 'Настройка команды /work', style = nextcord.ButtonStyle.grey)
            async def setwork(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if owner == interaction.user.id:
                    ec_db = sqlite3.connect('database/economy.db', timeout=10)
                    ec = ec_db.cursor()
                    embed = nextcord.Embed(
                        title="Настройка команды /work", description=f'Укажи минимальное количество валюты, которое будет даваться за использование команды', color=0x2b2d31)
                            
                    await interaction.send(embed=embed)   

                    try:
                        msg = await bot.wait_for('message', timeout= 30, check=lambda m: m.author.id == interaction.user.id)
                        s1 = msg.content
                        ot = int(s1)

                        embed = nextcord.Embed(
                            title="Настройка команды /work", description=f'Укажи максимальное количество валюты, которое будет даваться за использование команды', color=0x2b2d31)
                                
                        await interaction.send(embed=embed)  

                        msg = await bot.wait_for('message', timeout= 30, check=lambda m: m.author.id == interaction.user.id)
                        s12 = msg.content
                        do = int(s12)
                    
                        for em in ec.execute(f'SELECT currency FROM settings where guild_id={interaction.guild.id}'):
                            t1 = bot.get_emoji(em[0])
                            
                            if do < 0 or ot < 0:
                                embed = nextcord.Embed(
                                    title="Установка диапозона", description=f'Числа не должны быть меньше нолика ^^', color=0x2b2d31)
                                
                                await interaction.send(embed=embed)
                            else:
                                ec.execute(
                                    f"UPDATE settings SET work_ot='{ot}' where guild_id={interaction.guild.id}")
                                ec.execute(
                                    f"UPDATE settings SET work_do='{do}' where guild_id={interaction.guild.id}")
                                ec_db.commit()
                                embed = nextcord.Embed(
                                    title="Установка диапозона", description=f'Диапозон для команды `/work` был усталовен успешно! Теперь игроки будут получать от {ot} до {do} {t1}', color=0x2b2d31)
                                
                                await interaction.send(embed=embed)

                    except asyncio.exceptions.TimeoutError:
                        await interaction.send("Действия команды были отменены.")  
                else:
                    pass
            @nextcord.ui.button(label = 'Настройка команды /transfer', style = nextcord.ButtonStyle.grey)
            async def commision(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if owner == interaction.user.id:
                    ec_db = sqlite3.connect('database/economy.db', timeout=10)
                    ec = ec_db.cursor()
                    embed = nextcord.Embed(
                        title="Настройка команды /transfer", description=f'Укажи коммисию для команды /transfer. Но помни что 100% максимум', color=0x2b2d31)
                            
                    await interaction.send(embed=embed)   

                    try:
                        msg = await bot.wait_for('message', timeout= 30, check=lambda m: m.author.id == interaction.user.id)
                        s1 = msg.content
                        commission = int(s1)
                        ec_db = sqlite3.connect('database/economy.db', timeout=10)
                        ec = ec_db.cursor()
                        if commission > 100:
                            embed = nextcord.Embed(
                                title="Установка комиссии", description=f'Комиссия не может быть больше 100%', color=0x2b2d31)
                            
                            await interaction.send(embed=embed)
                        else:
                            if commission < 0:
                                embed = nextcord.Embed(
                                    title="Установка комиссии", description=f'Комиссия не может быть меньше 0%', color=0x2b2d31)
                                
                                await interaction.send(embed=embed)
                            else:
                                if commission < 10:
                                    dd = f'0.0{commission}'
                                    ec.execute(
                                        f"UPDATE settings SET com='{dd}' where guild_id={interaction.guild.id}")
                                    ec.execute(
                                        f"UPDATE settings SET com_info='{commission}' where guild_id={interaction.guild.id}")
                                    ec_db.commit()
                                    embed = nextcord.Embed(
                                        title="Установка комиссии", description=f'Комиссия для команды `/transfer` была усталовен успешно! Теперь игроки будут переводить валюту с коммисией - {commission}%', color=0x2b2d31)
                                    
                                    await interaction.send(embed=embed)
                                elif commission == 100:
                                    dd = f'1'
                                    ec.execute(
                                        f"UPDATE settings SET com='{dd}' where guild_id={interaction.guild.id}")
                                    ec.execute(
                                        f"UPDATE settings SET com_info='{commission}' where guild_id={interaction.guild.id}")
                                    ec_db.commit()
                                    embed = nextcord.Embed(
                                        title="Установка комиссии", description=f'Комиссия для команды `/transfer` была усталовен успешно! Теперь игроки будут переводить валюту с коммисией - {commission}%', color=0x2b2d31)
                                    
                                    await interaction.send(embed=embed)
                                else:
                                    dd = f'0.{commission}'
                                    ec.execute(
                                        f"UPDATE settings SET com='{dd}' where guild_id={interaction.guild.id}")
                                    ec.execute(
                                        f"UPDATE settings SET com_info='{commission}' where guild_id={interaction.guild.id}")
                                    ec_db.commit()
                                    embed = nextcord.Embed(
                                        title="Установка комиссии", description=f'Комиссия для команды `/transfer` была усталовен успешно! Теперь игроки будут переводить валюту с коммисией - {commission}%', color=0x2b2d31)
                                    
                                    await interaction.send(embed=embed)
                        
                        
                    except asyncio.exceptions.TimeoutError:
                        await interaction.send("Действия команды были отменены.")
                else:
                    pass

            @nextcord.ui.button(label = 'Назад', style = nextcord.ButtonStyle.red)
            async def quit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if owner == interaction.user.id:
                    await message.edit(embed=embed, view=settingsmodule()) 
                else:
                    pass

        class modulerp(nextcord.ui.View):

            def __init__(self):
                super().__init__(timeout=60)            
            @nextcord.ui.button(label = 'Включить/Выключить платные команды реакций', style = nextcord.ButtonStyle.grey)
            async def rpvkl(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if owner == interaction.user.id:
                    ec_db = sqlite3.connect('database/economy.db', timeout=10)
                    ec = ec_db.cursor()
                    for em in ec.execute(f'SELECT currency FROM settings where guild_id={interaction.guild.id}'):
                        t1 = bot.get_emoji(em[0])
                        for rp in ec.execute(f'SELECT rp FROM settings where guild_id={interaction.guild.id}'):
                            if rp[0] == 0:
                                ec.execute(
                                    f"UPDATE settings SET rp='1' where guild_id={interaction.guild.id}")
                                ec_db.commit()
                                embed = nextcord.Embed(title="Включение платных команд взаимодействий", 
                                    description=f'На данном сервере были включены платные команды взаимодействия. Дефолт цена состовляет - 10 {t1}. Изменить стоимость вы можете кнопкой выше!', color=0x2b2d31)
                                
                                await interaction.send(embed=embed)    
                            else:
                                ec.execute(
                                    f"UPDATE settings SET rp='0' where guild_id={interaction.guild.id}")
                                ec.execute(
                                    f"UPDATE settings SET rp_cost='10' where guild_id={interaction.guild.id}")
                                ec_db.commit()
                                embed = nextcord.Embed(title="Выключение платных команд взаимодействий", 
                                    description=f'На данном сервере были отключены платные команды взаимодействия', color=0x2b2d31)
                                
                                await interaction.send(embed=embed)    
                else:
                    pass


            ec_db = sqlite3.connect('database/economy.db', timeout=10)
            ec = ec_db.cursor()
            for rp in ec.execute(f'SELECT rp FROM settings where guild_id={interaction.guild.id}'):
                if rp[0] == 0:        
                    @nextcord.ui.button(label = 'Установить стоимость для команд реакций', style = nextcord.ButtonStyle.grey, disabled=True)
                    async def rpcost(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        pass
                else:       
                    @nextcord.ui.button(label = 'Установить стоимость для команд реакций', style = nextcord.ButtonStyle.grey, disabled=False)
                    async def rpcost(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if owner == interaction.user.id:
                            ec_db = sqlite3.connect('database/economy.db', timeout=10)
                            ec = ec_db.cursor()
                            embed = nextcord.Embed(
                                title="Настройка платных команд взаимодействий", description=f'Укажи cтоимость', color=0x2b2d31)
                                    
                            await interaction.send(embed=embed)   

                            try:
                                msg = await bot.wait_for('message', timeout= 30, check=lambda m: m.author.id == interaction.user.id)
                                s1 = msg.content
                                cost = int(s1)
                                
                                ec_db = sqlite3.connect('database/economy.db', timeout=10)
                                ec = ec_db.cursor()
                                for em in ec.execute(f'SELECT currency FROM settings where guild_id={interaction.guild.id}'):
                                    t1 = bot.get_emoji(em[0])
                                    if cost < 1:
                                        embed = nextcord.Embed(title="Настройка платных команд взаимодействий", 
                                            description=f'**Стоимость не может быть меньше 1 {t1} ^^', color=0x2b2d31)
                                        
                                        await interaction.send(embed=embed)    
                                    else:
                                        
                                        ec.execute(
                                            f"UPDATE settings SET rp_cost='{cost}' where guild_id={interaction.guild.id}")
                                        ec_db.commit()
                                        embed = nextcord.Embed(title="Настройка платных команд взаимодействий", 
                                            description=f'На данном сервере теперь все команды взаимодействия будут использоваться за {cost} {t1}', color=0x2b2d31)
                                        
                                        await interaction.send(embed=embed)    
                
                                
                            except asyncio.exceptions.TimeoutError:
                                await interaction.send("Действия команды были отменены.")
                        else:
                            pass

            @nextcord.ui.button(label = 'Назад', style = nextcord.ButtonStyle.red)
            async def quit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if owner == interaction.user.id:
                    await message.edit(embed=embed, view=settingsmodule()) 
                else:
                    pass



        
        class settingsmodule(nextcord.ui.View):

            def __init__(self):
                super().__init__(timeout=60)
            
            @nextcord.ui.button(label = 'Модуль "Экономика"', style = nextcord.ButtonStyle.grey)
            async def moduleec(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                ec_db = sqlite3.connect('database/economy.db', timeout=10)
                ec = ec_db.cursor()                
                embed = nextcord.Embed(title = 'Модуль `Экономика`', description="Настройки бота:", color=0x2b2d31)
                for ec1 in ec.execute(f"SELECT timely_ot, timely_do, work_ot, work_do, com_info, rp, rp_cost FROM settings where guild_id={interaction.guild.id}"):
                
                    embed.add_field(
                        name="Экономика:", value=f'・`bf` - множитель x2\n・`timely` - {ec1[0]} - {ec1[1]}; Cooldown - 24 часа.\n・`work` - {ec1[2]} - {ec1[3]}; Cooldown - 180 сек.\n・`transfer` - Комиссия - {ec1[4]}%', inline=False)
                        
                   
                await message.edit(embed=embed, view=moduleeconomy())

            @nextcord.ui.button(label = 'Модуль "Реакции"', style = nextcord.ButtonStyle.grey)
            async def modulerp(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                embed = nextcord.Embed(title = 'Модуль `Реакции`', description="Настройки бота:", color=0x2b2d31)

                ec_db = sqlite3.connect('database/economy.db', timeout=10)
                ec = ec_db.cursor()

                
                for ec1 in ec.execute(f"SELECT rp, rp_cost FROM settings where guild_id={interaction.guild.id}"):
                    if ec1[0] == 0:
                            
                        embed.add_field(
                            name="Команды взаимодействия:", value=f'Бесплатные', inline=False)
                            
                    else:
                        
                        embed.add_field(
                            name="Команды взаимодействия:", value=f'Платные - {ec1[1]}', inline=False)
                        

                await message.edit(embed=embed, view=modulerp())




        global message
        embed = nextcord.Embed(description="Настройки бота:", color=0x2b2d31)
        message = await interaction.send(embed=embed, view = settingsmodule())



            



        



    @settings.error
    async def settings_error(self, interaction: nextcord.Interaction, error):
        if isinstance(error, nextcord.ext.application_checks.errors.ApplicationMissingPermissions):
            embed = nextcord.Embed(
                title=f"Settings: Error", description=f"Не хватает прав.", color=0x2b2d31)

            await interaction.send(embed=embed)


















def setup(bot):
    bot.add_cog(settings(bot))