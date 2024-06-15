import asyncio
import re
from nextcord.ui import Button, View
import asyncio
import random
import pandas as pd
import nextcord
from datetime import datetime, date, time, timedelta
from nextcord.ext import commands
import sqlite3
import math
import cooldowns
from dateutil.relativedelta import relativedelta
from config import *
from nextcord.ext import application_checks, commands, menus
from humanfriendly import format_timespan
from proc import timely, balance
import time

px = settings['prefix']

pec_db = sqlite3.connect('database/premium.db')
pec = pec_db.cursor()

task_db = sqlite3.connect('database/tasks.db', timeout=10)
task = task_db.cursor()
    
  



class economy(commands.Cog):
    """ Модуль `экономика` | Команды данного модуля"""

    def __init__(self, bot):
        self.bot = bot

    ### None ###
    
    @nextcord.slash_command(description="Баланс пользователя", guild_ids = [int(settings["Guild_ID"])])
    async def balance(self, interaction: nextcord.Interaction, member: nextcord.Member = None):
        """・`$/bal/b <member (optional)>`\n・Узнать баланс"""
        ec_db = sqlite3.connect('database/economy.db', timeout=10)
        ec = ec_db.cursor()
        owner = interaction.user
        user = member or interaction.user      

        multipliermode = 'Отсутствует'

        if ec.execute(f"SELECT multiplier FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] != "None":
            if ec.execute(f"SELECT multiplier FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == "2x":
                multipliermode = "2x".format(math.trunc(task.execute(f"SELECT date FROM tasks WHERE id={user.id} and guild_id = {interaction.guild.id} and name = 'multiplier'").fetchone()[0]))
            elif ec.execute(f"SELECT multiplier FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == "3x":
                multipliermode = "3x".format(math.trunc(task.execute(f"SELECT date FROM tasks WHERE id={user.id} and guild_id = {interaction.guild.id} and name = 'multiplier'").fetchone()[0]))
            elif ec.execute(f"SELECT multiplier FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == "5x":
                multipliermode = "5x".format(math.trunc(task.execute(f"SELECT date FROM tasks WHERE id={user.id} and guild_id = {interaction.guild.id} and name = 'multiplier'").fetchone()[0]))



        a = await balance((ec.execute(f"SELECT bal FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), (pec.execute(f"SELECT bal FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), user.display_avatar.url, user.name, multipliermode)
        await interaction.send(file=nextcord.File(a))

    @nextcord.slash_command(description="Таблица лидеров", guild_ids = [int(settings["Guild_ID"])])
    async def leaderboard(self, interaction: nextcord.Interaction, mode : str = nextcord.SlashOption(
        name="mode",
        choices={
        "Войсы": 'в', 
        "Сообщений": 'сб',
        "Денюшек": 'д',
        "Уровеней": 'ур',
        "Кланы": 'кл'      
        })):

        lvl_db = sqlite3.connect('database/lvl.db', timeout=10)
        lvl = lvl_db.cursor()

        ec_db = sqlite3.connect('database/economy.db', timeout=10)
        ec = ec_db.cursor()

        profile_db = sqlite3.connect('database/profile.db', timeout=10)
        profile = profile_db.cursor()

        c_db = sqlite3.connect('database/clan.db', timeout=10)
        c = c_db.cursor()

        if mode == 'д':
            embed = nextcord.Embed(title = 'Лидеры по денюшкам', color=0x2b2d31)
            
            counter = 0
            for em in ec.execute(f'SELECT currency FROM settings where guild_id={interaction.guild.id}'):
                t1 = self.bot.get_emoji(em[0]) 
                for row in ec.execute("SELECT bal, id FROM balance WHERE guild_id = {} ORDER BY bal DESC LIMIT 10".format(interaction.guild.id)):
                    counter += 1
                    embed.add_field(
                        name = f'{counter} место',
                        value = f'<@{row[1]}> | {row[0]} {t1}',
                        inline = False
                    )        
                await interaction.send(embed = embed)

        elif mode == 'сб':
            embed = nextcord.Embed(title = 'Лидеры по сообщениям', color=0x2b2d31)
            
            counter = 0
            for row in profile.execute("SELECT txt, id FROM profile WHERE guild_id = {} ORDER BY txt DESC LIMIT 10".format(interaction.guild.id)):
                counter += 1
                embed.add_field(
                    name = f'{counter} место',
                    value = f'<@{row[1]}> | {row[0]} сообщ.',
                    inline = False
                )
            await interaction.send(embed = embed)  

        elif mode == 'в':
            embed = nextcord.Embed(title = 'Лидеры по войсам', color=0x2b2d31)
            
            counter = 0

            for row in profile.execute("SELECT voice, id FROM profile WHERE guild_id = {} ORDER BY voice DESC LIMIT 10".format(interaction.guild.id)):

                rt = relativedelta(seconds=row[0])
                counter += 1
                embed.add_field(
                    name = f'{counter} место',
                    value = '<@{}> | ```{:01d} дн. {:01d} ч. {:01d} мин. {:01d} сек.```'.format(row[1], int(rt.days), int(rt.hours), int(rt.minutes), int(rt.seconds)),
                    inline = False
                )
        
            await interaction.send(embed = embed)
        elif mode == 'ур':
            embed = nextcord.Embed(title = 'Лидеры по уровням', color=0x2b2d31)
            
            counter = 0

            for row in lvl.execute("SELECT lvl, id FROM level WHERE guild_id = {} ORDER BY lvl DESC LIMIT 10".format(interaction.guild.id)):

                rt = relativedelta(seconds=row[0])
                counter += 1
                embed.add_field(
                    name = f'{counter} место',
                    value = f'<@{row[1]}> | {row[0]} уровень',
                    inline = False
                )
        
            await interaction.send(embed = embed) 

        elif mode == 'кл':
            embed = nextcord.Embed(title = 'Лидеры по кланам', color=0x2b2d31)
            
            counter = 0
        
            for row in c.execute("SELECT name, balance FROM clan WHERE id = {} ORDER BY balance DESC LIMIT 10".format(interaction.guild.id)):
                counter += 1
                embed.add_field(
                    name = f'{counter} место',
                    value = f'**{row[0]}** | {row[1]} <:club:1086336199133773954>',
                    inline = False
                )        
            await interaction.send(embed = embed)  
    
    ### Admin ###

    @nextcord.slash_command(name = 'add-item', description="Добавить роль в магазин", guild_ids = [int(settings["Guild_ID"])])
    @application_checks.has_permissions(administrator=True)
    async def add(self, interaction: nextcord.Interaction, role: nextcord.Role, cost: int ):

                
        ec_db = sqlite3.connect('database/economy.db', timeout=10)
        ec = ec_db.cursor()
        if cost < 0:
            embed=nextcord.Embed(description = "Ну так не годится, стоимость не может быть равна 0 или быть меньше ^-^", color=0x2b2d31)
            
            await interaction.send(embed = embed)
        else:
            ec.execute(f"SELECT role_id FROM shop where id = {interaction.guild.id} and role_id={role.id}")
            if ec.fetchone() is None:
                ec.execute(f"SELECT num FROM shop where id = {interaction.guild.id}")
                if ec.fetchone() is None:
                    ec.execute("INSERT INTO shop VALUES ({}, {}, {}, {}, {}, {})".format(1, role.id, cost, interaction.guild.id, 0, interaction.user.id))
                    ec_db.commit()

                    embed = nextcord.Embed(description = f'**Роль:** {role.mention}\n\n**Цена:** {cost}\n\n**Персональное ID:** {role.id}\n\n**Слот №:** 1', color=0x2b2d31)
                    embed.set_thumbnail(url=interaction.user.display_avatar)
                    await interaction.send(embed=embed)
                else:
                    for n in ec.execute(f"SELECT num FROM shop where id = {interaction.guild.id} order by num desc limit 1"):
                        ec.execute("INSERT INTO shop VALUES ({}, {}, {}, {}, {}, {})".format(n[0]+1, role.id, cost, interaction.guild.id, 0, interaction.user.id))
                        ec_db.commit()

                        embed = nextcord.Embed(description = f'**Роль:** {role.mention}\n\n**Цена:** {cost}\n\n**Персональное ID:** {role.id}\n\n**Слот №:** {n[0]+1}', color=0x2b2d31)
                        embed.set_thumbnail(url=interaction.user.display_avatar)
                        await interaction.send(embed=embed)

            else:
                embed=nextcord.Embed(description = "Данный товар уже находится на продаже", color=0x2b2d31)
                
                await interaction.send(embed = embed)
 
    @nextcord.slash_command(description="Выдать пользователю деньги", guild_ids = [int(settings["Guild_ID"])])
    @application_checks.has_permissions(administrator=True)
    async def give(self, interaction: nextcord.Interaction, money:int, member: nextcord.Member = None):
        """・`give <money> <member>`\n・Необходимы права администратора\n・Выдача денежных средств пользователю"""
        ec_db = sqlite3.connect('database/economy.db', timeout=10)
        ec = ec_db.cursor()

        for em in ec.execute(f'SELECT currency FROM settings where guild_id={interaction.guild.id}'):
            t1 = self.bot.get_emoji(em[0]) 

            if 0 >= money:
                embed=nextcord.Embed(description = "Сумма не может быть отрицательной или равна 0^^", color=0x2b2d31)
                embed.set_thumbnail(url=interaction.user.display_avatar)
                await interaction.send(embed = embed)   
            else:  
                if member is None:
                    for bal1 in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                        ec.execute(f'UPDATE balance SET bal={bal1[0] + money} where id={interaction.user.id} and guild_id={interaction.guild.id}')
                    embed=nextcord.Embed(title=f"**Выдача денег**", description = "Выдача денег пользователю", color=0x2b2d31)
                    embed.add_field(name = 'Пользователь:', value=interaction.user.mention, inline=True)
                    embed.add_field(name = 'Администратор:', value=interaction.user.mention, inline=True)
                    embed.add_field(name = 'Сумма:', value=f'{money} {t1}', inline=True)
                    embed.set_thumbnail(url=interaction.user.display_avatar)
                    await interaction.send(embed = embed)  

                else:      
                    for bal1 in ec.execute(f'SELECT bal FROM balance where id={member.id} and guild_id={interaction.guild.id}'):
                        ec.execute(f'UPDATE balance SET bal={bal1[0] + money} where id={member.id} and guild_id={interaction.guild.id}')
                    embed=nextcord.Embed(title=f"**Выдача денег**", description = "Выдача денег пользователю", color=0x2b2d31)
                    embed.add_field(name = 'Пользователь:', value=member.mention, inline=True)
                    embed.add_field(name = 'Администратор:', value=interaction.user.mention, inline=True)
                    embed.add_field(name = 'Сумма:', value=f'{money} {t1}', inline=True)
                    embed.set_thumbnail(url=interaction.user.display_avatar)
                    await interaction.send(embed = embed)  

                    embed1=nextcord.Embed(title=f"**Поступление денюшек**", description = "Комиссия отстуствует", color=0x2b2d31)
                    embed1.add_field(name = 'Пользователь:', value=member.mention, inline=False)
                    embed1.add_field(name = 'Администратор:', value=interaction.user.mention, inline=False)
                    embed1.add_field(name = 'Сумма:', value=f'{money} {t1}', inline=False)
                    embed1.set_thumbnail(url=interaction.user.display_avatar)
                    await member.send(embed = embed1)
        ec_db.commit()

    @nextcord.slash_command(description="Выдать пользователю премиум деньги", guild_ids = [int(settings["Guild_ID"])])
    @application_checks.has_permissions(administrator=True)
    async def awardp(self, interaction: nextcord.Interaction, money:int, member: nextcord.Member = None):
        """・`awardp <money> <member>`\n・Необходимы права администратора\n・Выдача денежных средств пользователю"""
        ec_db = sqlite3.connect('database/premium.db', timeout=10)
        ec = ec_db.cursor()

        for em in ec.execute(f'SELECT currency FROM settings where guild_id={interaction.guild.id}'):
            t1 = self.bot.get_emoji(em[0]) 

            if 0 >= money:
                embed=nextcord.Embed(description = "Сумма не может быть отрицательной или равна **0**", color=0x2b2d31)
                embed.set_thumbnail(url=interaction.user.display_avatar)
                await interaction.send(embed = embed)   
            else:  
                if member is None:
                    for bal1 in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                        ec.execute(f'UPDATE balance SET bal={bal1[0] + money} where id={interaction.user.id} and guild_id={interaction.guild.id}')
                    embed=nextcord.Embed(title=f"**Выдача прем-денег**", description = "Выдача прем-денег пользователю", color=0x2b2d31)
                    embed.add_field(name = 'Пользователь:', value=interaction.user.mention, inline=True)
                    embed.add_field(name = 'Администратор:', value=interaction.user.mention, inline=True)
                    embed.add_field(name = 'Сумма:', value=f'{money} {t1}', inline=True)
                    embed.set_thumbnail(url=interaction.user.display_avatar)
                    await interaction.send(embed = embed)  

                else:      
                    for bal1 in ec.execute(f'SELECT bal FROM balance where id={member.id} and guild_id={interaction.guild.id}'):
                        ec.execute(f'UPDATE balance SET bal={bal1[0] + money} where id={member.id} and guild_id={interaction.guild.id}')
                    embed=nextcord.Embed(title=f"**Выдача прем-денег**", description = "Выдача денег пользователю", color=0x2b2d31)
                    embed.add_field(name = 'Пользователь:', value=member.mention, inline=True)
                    embed.add_field(name = 'Администратор:', value=interaction.user.mention, inline=True)
                    embed.add_field(name = 'Сумма:', value=f'{money} {t1}', inline=True)
                    embed.set_thumbnail(url=interaction.user.display_avatar)
                    await interaction.send(embed = embed)  

                    embed1=nextcord.Embed(title=f"**Поступление прем-денюшек**", description = "Комиссия отстуствует", color=0x2b2d31)
                    embed1.add_field(name = 'Пользователь:', value=member.mention, inline=False)
                    embed1.add_field(name = 'Администратор:', value=interaction.user.mention, inline=False)
                    embed1.add_field(name = 'Сумма:', value=f'{money} {t1}', inline=False)
                    embed1.set_thumbnail(url=interaction.user.display_avatar)
                    await member.send(embed = embed1)
        ec_db.commit()

    @nextcord.slash_command(description="Забрать деньги у участника", guild_ids = [int(settings["Guild_ID"])])
    @application_checks.has_permissions(administrator=True)
    async def take(self, interaction: nextcord.Interaction, money:int, member: nextcord.Member = None):
        """・`give <money> <member>`\n・Необходимы права администратора\n・Выдача денежных средств пользователю"""
        ec_db = sqlite3.connect('database/economy.db', timeout=10)
        ec = ec_db.cursor()
        for em in ec.execute(f'SELECT currency FROM settings where guild_id={interaction.guild.id}'):
            t1 = self.bot.get_emoji(em[0]) 

            if 0 > money:
                embed=nextcord.Embed(description = "Нельзя забрать cумму которая ниже нолика(", color=0x2b2d31)
                embed.set_thumbnail(url=interaction.user.display_avatar)
                await interaction.send(embed = embed)   
            else:  
                if member is None:
                    for balance in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                        if balance[0] < money:
                            embed=nextcord.Embed(description = "Нельзя, забрать у себя больше коинов чем на твоем балансе(", color=0x2b2d31)
                            embed.set_thumbnail(url=interaction.user.display_avatar)
                            await interaction.send(embed = embed)  
                        else:
                            for bal1 in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                ec.execute(f'UPDATE balance SET bal={bal1[0] - money} where id={interaction.user.id} and guild_id={interaction.guild.id}')
                            embed=nextcord.Embed(title=f"**Снятие коинов**", color=0x2b2d31)
                            embed.add_field(name = 'Пользователь:', value=interaction.user.mention, inline=True)
                            embed.add_field(name = 'Администратор:', value=interaction.user.mention, inline=True)
                            embed.add_field(name = 'Сумма:', value=f'{money} {t1}', inline=True)
                            embed.set_thumbnail(url=interaction.user.display_avatar)
                            await interaction.send(embed = embed)  
                else:
                    if interaction.user.id == member.id:
                        for balance1 in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                            if balance1[0] < money:
                                embed=nextcord.Embed(description = "Нельзя, забрать коинов больше чем на твоем балансе(", color=0x2b2d31)
                                embed.set_thumbnail(url=interaction.user.display_avatar)
                                await interaction.send(embed = embed)  
                            else:
                                for bal1 in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                    ec.execute(f'UPDATE balance SET bal={bal1[0] - money} where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                embed=nextcord.Embed(title=f"**Снятие коинов**", description = "Снятие валюты", color=0x2b2d31)
                                embed.add_field(name = 'Пользователь:', value=interaction.user.mention, inline=True)
                                embed.add_field(name = 'Администратор:', value=interaction.user.mention, inline=True)
                                embed.add_field(name = 'Сумма:', value=f'{money} {t1}', inline=True)
                                embed.set_thumbnail(url=interaction.user.display_avatar)
                                await interaction.send(embed = embed)
                    else:  
                        for balance in ec.execute(f'SELECT bal FROM balance where id={member.id} and guild_id={interaction.guild.id}'):
                            if balance[0] < money:
                                embed=nextcord.Embed(description = "Баланс данного участника больше чем, сумма которую ты хочешь снять", color=0x2b2d31)
                                embed.set_thumbnail(url=interaction.user.display_avatar)
                                await interaction.send(embed = embed)  
                            else:
                                
                                for bal1 in ec.execute(f'SELECT bal FROM balance where id={member.id} and guild_id={interaction.guild.id}'):
                                    ec.execute(f'UPDATE balance SET bal={bal1[0] - money} where id={member.id} and guild_id={interaction.guild.id}')
                                embed=nextcord.Embed(title=f"**Снятие коинов**", color=0x2b2d31)
                                embed.add_field(name = 'Пользователь:', value=member.mention, inline=True)
                                embed.add_field(name = 'Админ-злодей:', value=interaction.user.mention, inline=True)
                                embed.add_field(name = 'Сумма:', value=f'{money} {t1}', inline=True)
                                embed.set_thumbnail(url=interaction.user.display_avatar)
                                await interaction.send(embed = embed)  
                                ec_db.commit()

                                embed1=nextcord.Embed(title=f"**Снятие коинов**", description = "С твоего баланса были сняты коины", color=0x2b2d31)
                                embed1.add_field(name = 'Пользователь:', value=member.mention, inline=False)
                                embed1.add_field(name = 'Админ-злодей:', value=interaction.user.mention, inline=False)
                                embed1.add_field(name = 'Сумма:', value=f'{money} {t1}', inline=False)
                                embed.set_thumbnail(url=interaction.user.display_avatar)
                                await member.send(embed = embed1)
        ec_db.commit()    
          

    @nextcord.slash_command(description='Игра дуэль', guild_ids = [int(settings["Guild_ID"])])
    async def duel(self, interaction: nextcord.Interaction, count: int):
        ec_db = sqlite3.connect('database/economy.db', timeout=10)
        ec = ec_db.cursor() 
        owner = interaction.user
        guild = interaction.guild
        for em in ec.execute(f'SELECT currency FROM settings where guild_id={interaction.guild.id}'):
            t1 = self.bot.get_emoji(em[0]) 

            if 50 >= count:
                embed=nextcord.Embed(description = "Cумма ставки не может быть меньше **50**", color=0x2b2d31)
                embed.set_thumbnail(url=interaction.user.display_avatar)
                await interaction.send(embed = embed)     
            elif ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}').fetchone()[0] < count:
                embed=nextcord.Embed(description = "Слишком большая ставка. У тебя не хватает средств^^", color=0x2b2d31)
                embed.set_thumbnail(url=interaction.user.display_avatar)
                await interaction.send(embed = embed, ephemeral=True)      
            else:                   
                
                embed1=nextcord.Embed(description="Действие **данной команды** были **завершены**. Денежные средства были **возвращены** на ваш счет.", color=0x2b2d31)
                embed1.set_thumbnail(url=interaction.user.display_avatar)

                class duel(nextcord.ui.View):
                    def __init__(self):
                        super().__init__(timeout=None)

                    @nextcord.ui.button(label = 'Присоединиться', style = nextcord.ButtonStyle.blurple, disabled=False)
                    async def join(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        member = interaction.user
                        if owner.id == interaction.user.id:
                            embed=nextcord.Embed(description="Ты не **можешь** сам с собой **играть**^^".format(interaction.user.display_name, count, t1), color=0x2b2d31)
                            embed.set_thumbnail(url=interaction.user.display_avatar)
                            await interaction.send(embed=embed, ephemeral=True)
                        else:
                            if ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}').fetchone()[0] < count:
                                embed=nextcord.Embed(description = "Слишком большая ставка. Тебе эта игра не по карману^^", color=0x2b2d31)
                                embed.set_thumbnail(url=interaction.user.display_avatar)
                                await interaction.send(embed = embed, ephemeral=True) 
                            else:
                                for row in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                    ec.execute(f'UPDATE balance SET bal={row[0] - count}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                ec_db.commit()   
                                emb=nextcord.Embed(description = f"**{interaction.user.display_name}** x **{owner.display_name}**\r\r**3**", color=0x2b2d31)
                                emb.set_thumbnail(url=interaction.user.display_avatar)
                                emb.set_image(url="https://media.discordapp.net/attachments/1070337148949115011/1083027149998522488/bae92ce18019ca3bc8ccaec6eb21acc1.png?width=625&height=336")
                                await interaction.edit(embed = emb, view = None) 
                                await asyncio.sleep(1)  
                                emb=nextcord.Embed(description = f"**{interaction.user.display_name}** x **{owner.display_name}**\r\r**2**", color=0x2b2d31)
                                emb.set_thumbnail(url=interaction.user.display_avatar)
                                emb.set_image(url="https://media.discordapp.net/attachments/1070337148949115011/1083027149998522488/bae92ce18019ca3bc8ccaec6eb21acc1.png?width=625&height=336")
                                await interaction.edit(embed = emb, view = None) 
                                await asyncio.sleep(1)  
                                emb=nextcord.Embed(description = f"**{interaction.user.display_name}** x **{owner.display_name}**\r\r**1**", color=0x2b2d31)
                                emb.set_thumbnail(url=interaction.user.display_avatar)
                                emb.set_image(url="https://media.discordapp.net/attachments/1070337148949115011/1083027054200627290/bae92ce18019ca3bc8ccaec6eb21acc1.gif?width=625&height=336")
                                await interaction.edit(embed = emb, view = None)  
                                await asyncio.sleep(0.8)  
                                    
                                userlist = [owner.id, interaction.user.id]
                                module = random.choice(userlist)
                                print(module)

                                if owner.id == int(module):
                                    embed=nextcord.Embed(description = f"{owner.mention} **стреляет** и его пуля **убивает** {interaction.user.mention}", color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)
                                    embed.set_footer(text='Сумма выигрыша: {}'.format(count*2))
                                    await interaction.edit(embed = embed)  
                                    for row in ec.execute(f'SELECT bal FROM balance where id={owner.id} and guild_id={interaction.guild.id}'):
                                        ec.execute(f'UPDATE balance SET bal={row[0] + int(count*2)}  where id={owner.id} and guild_id={interaction.guild.id}')
                                    ec_db.commit()
                                elif interaction.user.id == int(module):
                                    embed=nextcord.Embed(description = f"{interaction.user.mention} **стреляет** и его пуля **убивает** {owner.mention}", color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)
                                    embed.set_footer(text='Сумма выигрыша: {}'.format(count*2))
                                    await interaction.edit(embed = embed)  
                                    for row in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                        ec.execute(f'UPDATE balance SET bal={row[0] + int(count*2)}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                    ec_db.commit()          
                                        
                                return
                                            
                                                                                       

                    @nextcord.ui.button(label = 'Отменить', style = nextcord.ButtonStyle.red, disabled=False)
                    async def stop(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if owner.id == interaction.user.id:
                            embed=nextcord.Embed(description="Ты **отменил** игру, все коины были **возвращены** назад^^".format(interaction.user.display_name, count, t1), color=0x2b2d31)
                            embed.set_thumbnail(url=interaction.user.display_avatar)
                            await interaction.edit(embed=embed, view = None)
                            for row in ec.execute(f'SELECT bal FROM balance where id={owner.id} and guild_id={interaction.guild.id}'):
                                ec.execute(f'UPDATE balance SET bal={row[0] + count}  where id={owner.id} and guild_id={interaction.guild.id}')
                            ec_db.commit() 
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)      

                for row in ec.execute(f'SELECT bal FROM balance where id={owner.id} and guild_id={interaction.guild.id}'):
                    ec.execute(f'UPDATE balance SET bal={row[0] - count}  where id={owner.id} and guild_id={interaction.guild.id}')
                ec_db.commit()         

                embed=nextcord.Embed(title="Дуэль", description="**{}**, начал дуэль, со **ставкой:** {} {}".format(interaction.user.display_name, count, t1), color=0x2b2d31)
                embed.set_thumbnail(url=interaction.user.display_avatar)
                msg = await interaction.send(embed=embed, view=duel())


    @nextcord.slash_command(description='Сборник иконок для личных ролей', guild_ids = [int(settings["Guild_ID"])])
    async def iconpack(self, interaction: nextcord.Interaction):
        bot = self.bot
        class CustomButtonMenuPages(menus.ButtonMenuPages, inherit_buttons=False):


            def __init__(self, source, timeout=60):
                super().__init__(source, timeout=timeout)


                self.PREVIOUS_PAGE = '<:leftarrow:1029123761179475968>'
                self.NEXT_PAGE = '<:rightarrow:1029123757740138517>'



                self.add_item(menus.MenuPaginationButton(emoji=self.PREVIOUS_PAGE, label=""))
                self.add_item(menus.MenuPaginationButton(emoji=self.NEXT_PAGE, label=""))



                self._disable_unavailable_buttons()

        

        icon = []   
        for emoji in self.bot.emojis:
            icon.append((f'<:{emoji.name}:{emoji.id}> ', emoji.id))


        class MyEmbedFieldPageSource(menus.ListPageSource):
            def __init__(self, data):
                super().__init__(data, per_page=10)

            async def format_page(self, menu, entries):
                embed = nextcord.Embed(title="Набор иконок", color=0x2b2d31)
                embed.set_thumbnail(url=interaction.user.display_avatar)
                for entry in entries:
                    emoji = bot.get_emoji(entry[1])
                    embed.add_field(name='⠀⠀', value=f'{emoji} - `{entry[1]}`', inline=False)
                embed.set_footer(text=f"Страница {menu.current_page + 1}/{self.get_max_pages()}")
                return embed

        pages = CustomButtonMenuPages(source=MyEmbedFieldPageSource(icon))
        await pages.start(interaction = interaction, ephemeral=True)

    @nextcord.slash_command(description="Меню управления личной ролью", guild_ids = [int(settings["Guild_ID"])])
    async def role_manager(self, interaction: nextcord.Interaction):  
        cost = int(settings['cost_role'])
        backup = int(settings['percent']) * 0.01 * cost
        owner = interaction.user
        bot = self.bot
        ec_db = sqlite3.connect('database/economy.db', timeout=10)
        ec = ec_db.cursor()   
        ec.execute(f"SELECT id FROM role where id={interaction.user.id} and guild_id={interaction.guild.id}")
        if ec.fetchone() is None:
            embed = nextcord.Embed(description = f'У тебя нету своей личной роли', color=0x2b2d31)
            embed.set_thumbnail(url=interaction.user.display_avatar)       
            await interaction.send(embed=embed, ephemeral= True)           
        else:
            for role1 in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                
                r1 = interaction.guild.get_role(int(role1[0]))
                for close in ec.execute(f"SELECT status FROM role WHERE id = {interaction.user.id} and guild_id = {interaction.guild.id}"):
                    if 'close' == close[0]:
                        if r1 is None:
                            ec.execute(f"DELETE FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}")
                            ec.execute(f"DELETE FROM shop where owner={interaction.user.id}")
                            ec_db.commit()

                            embed = nextcord.Embed(description = f'У тебя нету своей личной роли', color=0x2b2d31)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)         
                        else:
                            delete = Button(label="! Удалить роль !", style=nextcord.ButtonStyle.red)
                            buy = Button(label=f"Оплатить [{cost} коинов]", style=nextcord.ButtonStyle.gray)
                            
                            
                            async def buy_callback(interaction: nextcord.Interaction):
                                if owner.id == interaction.user.id:  
                                    for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):

                                        if bal[0] < cost:
                                            embed=nextcord.Embed(description = "Тебе нужно **{}** монет для оплаты личной роли ^^".format(cost), color=0x2b2d31)
                                            await interaction.send(embed = embed,ephemeral=True)      
                                        else:   
                                            task.execute(f"DELETE FROM tasks where id={interaction.user.id} and guild_id = {interaction.guild.id} and name='role'")
                                            task.execute(f"DELETE FROM tasks where id={interaction.user.id} and guild_id = {interaction.guild.id} and name='deleterole'")
                                            task_db.commit()
                                            bloop = (datetime.now() + timedelta(days=30)).timestamp()


                                            task.execute(f"INSERT INTO tasks VALUES ('role','{bloop}','{interaction.user.id}', '{interaction.guild.id}')")
                                            task_db.commit()

                                            ec.execute(f'UPDATE role SET status = "open" where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                            ec.execute(f'UPDATE balance SET bal={bal[0] - cost}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                            ec_db.commit()
                                            embed=nextcord.Embed(description = "Ты успешно продлил личную роль^^", color=0x2b2d31)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)
                                            await interaction.edit(embed = embed, view=None)   
                                else:
                                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)   

                            async def delete_callback(interaction: nextcord.Interaction):
                                if owner.id == interaction.user.id:  
                                    ec_db = sqlite3.connect('database/economy.db', timeout=10)
                                    ec = ec_db.cursor() 
                                    class dress(nextcord.ui.View):
                                        def __init__(self):
                                            super().__init__(timeout=60)

                                        @nextcord.ui.button(label = 'Да', style = nextcord.ButtonStyle.red, disabled=False)
                                        async def yes(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):   
                                            if owner.id == interaction.user.id:  
                                                for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                    r = interaction.guild.get_role(role[0])
                                                    name = r.name
                                                    await r.delete()
                                                    for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                                        task.execute(f"DELETE FROM tasks where id={interaction.user.id} and guild_id = {interaction.guild.id} and name='deleterole'")
                                                        task_db.commit()
                                                        ec.execute(f"DELETE FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}")
                                                        ec.execute(f"DELETE FROM shop where owner={interaction.user.id}")

                                                        embed=nextcord.Embed(description = f"Ты успешно удалил свою личную роль: {name}.", color=0x2b2d31)
                                                        embed.set_thumbnail(url=interaction.user.display_avatar)
                                                        await interaction.edit(embed = embed, view=None) 
                                                    ec_db.commit() 
                                            else:
                                                embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                await interaction.send(embed=embed, ephemeral= True)    

                                        @nextcord.ui.button(label = 'Нет', style = nextcord.ButtonStyle.grey, disabled=False)
                                        async def no(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):  
                                            if owner.id == interaction.user.id:  
                                                embed = nextcord.Embed(description = f'Действия для данной команды было отменено', color=0x2b2d31)
                                                embed.set_footer(text='Через 5 секунд, данное сообщение будет удалено')
                                                await interaction.edit(embed=embed, view = None)
                                                await asyncio.sleep(5)
                                                await interaction.message.delete()
                                            else:
                                                embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                await interaction.send(embed=embed, ephemeral= True)    

                                    embed = nextcord.Embed(description = f'Данное действие нельзя будет потом отменить. Ты уверен что ты хочешь продолжить?', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)
                                    await interaction.edit(embed=embed, view=dress())


                                else:
                                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)                        
                                
                            delete.callback = delete_callback
                            buy.callback = buy_callback
                            view = View()

                            view.add_item(buy)
                            view.add_item(delete)

                            bloop = (datetime.now() + timedelta(days=3)).timestamp()
                            for row in task.execute(f"SELECT date FROM tasks WHERE id={interaction.user.id} and guild_id = {interaction.guild.id} and name = 'deleterole'"):
                                embed=nextcord.Embed(title = 'Меню управления ролью', description=f'Твоя роль: {r1.mention} \r\rCрок действия твоего товара закончился.\n・<t:{math.trunc(row[0])}:R> роль будет удалена, если не будет внесена оплата.', color=0x2b2d31)
                                for bal in ec.execute(f"SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}"):
                                    embed.set_footer(text=f'Баланс: {bal[0]}')
                                embed.set_thumbnail(url=interaction.user.display_avatar)
                                
                                await interaction.send(embed = embed, view=view)    

                    else:
                            


                        class reset(nextcord.ui.View):
                            def __init__(self):
                                super().__init__(timeout=60)

                            ec.execute(f"SELECT role_id FROM shop where owner = {interaction.user.id}")
                            if ec.fetchone() is None:       
                                @nextcord.ui.button(label = 'Выложить роль в магазин', style = nextcord.ButtonStyle.grey, disabled=False)
                                async def shop(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                    ec_db = sqlite3.connect('database/economy.db', timeout=10)
                                    ec = ec_db.cursor()   
                                    if owner.id == interaction.user.id:
                                        for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):

                            
                                            if bal[0] < 900:
                                                embed=nextcord.Embed(description = "Стоимость данной функции 900 монет", color=0x2b2d31)
                                                await interaction.send(embed = embed, ephemeral=True)      
                                            else:                              
                                                ec_db = sqlite3.connect('database/economy.db', timeout=10)
                                                ec = ec_db.cursor() 
                                                

                                                try:
                                                    for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                        embed1=nextcord.Embed(description=f"Укажи cтоимость роли", color=0x2b2d31)
                                                        await interaction.edit(embed=embed1, view = None)
                                                        msg = await bot.wait_for('message', timeout= 30, check=lambda m: m.author.id == interaction.user.id)
                                                        try:

                                                            r = interaction.guild.get_role(role[0])
                                                            
                                                            
                                                            cost = int(msg.content)
                                                            
                                                            await msg.delete()
                                                            ec.execute(f"SELECT num FROM shop where id = {interaction.guild.id}")
                                                            if ec.fetchone() is None:
                                                                ec.execute(f"UPDATE balance SET bal = bal - 900 where id={interaction.user.id} and guild_id = {interaction.guild.id}")
                                                                ec.execute("INSERT INTO shop VALUES ({}, {}, {}, {}, {}, {})".format(1, r.id, cost, interaction.user.id, 0, interaction.user.id))
                                                                ec_db.commit()
                                        
                                                                embed = nextcord.Embed(description = f'**Роль:** {r.mention}\n\n**Цена:** {cost}\n\n**Персональное ID:** {r.id}\n\n**Слот №:** 1', color=0x2b2d31)
                                                                embed.set_thumbnail(url=interaction.user.display_avatar)
                                                                await interaction.edit(embed=embed, view = None)
                                                            else:
                                                                for n in ec.execute(f"SELECT num FROM shop where id = {interaction.guild.id} order by num desc limit 1"):
                                                                    ec.execute("INSERT INTO shop VALUES ({}, {}, {}, {}, {}, {})".format(n[0]+1, r.id, cost, interaction.user.id, 0, interaction.user.id))
                                                                    ec_db.commit()
                                                
                                                                    embed = nextcord.Embed(description = f'**Роль:** {r.mention}\n\n**Цена:** {cost}\n\n**Персональное ID:** {r.id}\n\n**Слот №:** {n[0]+1}', color=0x2b2d31)
                                                                    embed.set_thumbnail(url=interaction.user.display_avatar)
                                                                    await interaction.edit(embed=embed, view = None)
                                                        except:
                                                            await msg.delete()
                                                            embed = nextcord.Embed(description = f'Ошибка в конвертирование str в int. Скорее всего ты пытаешься **str(**{msg.content}**)** конвертировать в **int(**{msg.content}**)**.\n\n"Входные данные не является числом | Ты указал не число, а что то другое"', color=0x2b2d31)
                                                            embed.set_footer(text='Через 5 секунды, ты будешь отправлен в главное меню')
                                                            await interaction.edit(embed=embed, view = None)
                                                            await asyncio.sleep(5)
                                                            for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                                embed1=nextcord.Embed(title = 'Меню управления ролью', description='Твоя роль: <@&{}>'.format(role[0]), color=0x2b2d31)
                                                                embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                                embed1.set_footer(text='/role_manager - меню управления личной ролью')
                                                                await interaction.send(embed = embed1, view=reset()) 

                                                except asyncio.exceptions.TimeoutError:
                                                    embed = nextcord.Embed(description = f'Время на выполнения данной команды вышло', color=0x2b2d31)
                                                    embed.set_footer(text='Через 5 секунды, ты будешь отправлен в главное меню')
                                                    await interaction.edit(embed=embed, view = None)
                                                    await asyncio.sleep(5)
                                                    for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                        embed1=nextcord.Embed(title = 'Меню управления ролью', description='Твоя роль: <@&{}>'.format(role[0]), color=0x2b2d31)
                                                        embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                        embed1.set_footer(text='/role_manager - меню управления личной ролью')
                                                        await interaction.send(embed = embed1, view=reset())  

                                                        


                                    else:
                                        embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                            else:
                                @nextcord.ui.button(label = 'Удалить роль из магазина', style = nextcord.ButtonStyle.grey, disabled=False)
                                async def shop(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                    if owner.id == interaction.user.id:
                                        ec.execute(f"DELETE FROM shop where owner={interaction.user.id}")
                                        ec_db.commit()
                                        for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                            r = interaction.guild.get_role(role[0])
                                            embed = nextcord.Embed(description = f'Роль {r.mention} успешно была удалена из магазина', color=0x2b2d31)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)
                                            await interaction.edit(embed=embed, view = None)
                                    else:
                                        embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)

                            if r1 in interaction.user.roles:
                                @nextcord.ui.button(label = 'Снять', style = nextcord.ButtonStyle.grey, disabled=False)
                                async def on(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                    if owner.id == interaction.user.id:
                                        for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                            r = interaction.guild.get_role(role[0])
                                            await interaction.user.remove_roles(r)
                                            embed = nextcord.Embed(description = f'Роль {r.mention} успешно, была снята с участника {interaction.user.mention}', color=0x2b2d31)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)
                                            await interaction.edit(embed=embed, view = None)
                                    else:
                                        embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                            else:
                                
                                

                                @nextcord.ui.button(label = 'Надеть', style = nextcord.ButtonStyle.grey, disabled=False)
                                async def on(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                    if owner.id == interaction.user.id:
                                        ec.execute(f"DELETE FROM shop where owner={interaction.user.id}")
                                        ec_db.commit()
                                        for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                            r = interaction.guild.get_role(role[0])
                                            await interaction.user.add_roles(r)
                                            embed = nextcord.Embed(description = f'Роль {r.mention} успешно, была надета на участника {interaction.user.mention}', color=0x2b2d31)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)
                                            await interaction.edit(embed=embed, view = None)
                                    else:
                                        embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)

                            @nextcord.ui.button(label = 'Автооплата', style = nextcord.ButtonStyle.grey, disabled=False)
                            async def autos(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                if owner.id == interaction.user.id:
                                    if ec.execute(f"SELECT auto FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}").fetchone()[0] == 'off':
                                        for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                            ec.execute(f'UPDATE role SET auto = "on" where id={interaction.user.id} and guild_id = {interaction.guild.id}')
                                            ec_db.commit()
                                            embed = nextcord.Embed(description = f'Вы успешно включили `Автооплату`\rПо истечению срока действия товара, с вашего баланса спишется {cost} коинов. Если на вашем балансе не будет хватать средств, то ваша роль заблокируется и вам придется продливать предмет вручную', color=0x2b2d31)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)
                                            await interaction.edit(embed=embed, view = None)
                                    else:
                                            ec.execute(f'UPDATE role SET auto = "off" where id={interaction.user.id} and guild_id = {interaction.guild.id}')
                                            ec_db.commit()
                                            embed = nextcord.Embed(description = f'Вы успешно отключили `Автооплату`', color=0x2b2d31)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)
                                            await interaction.edit(embed=embed, view = None)                           
                                else:
                                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)

                            @nextcord.ui.button(label = 'Переименовать', style = nextcord.ButtonStyle.grey, disabled=False)
                            async def rename(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                if owner.id == interaction.user.id:
                                    for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):

                        
                                        if bal[0] < 250:
                                            embed=nextcord.Embed(description = "Стоимость данной функции 250 монет", color=0x2b2d31)
                                            await interaction.send(embed = embed, ephemeral=True)      
                                        else:                        
                                        
                                            class rename(nextcord.ui.Modal):
                                                def __init__(self):
                                                    super().__init__('Cмена названия роли')

                                                    self.Name = nextcord.ui.TextInput(label = 'New Name', min_length=1, max_length=70, required=False, placeholder='Например: Трахну небо, стану богом', style=nextcord.TextInputStyle.paragraph)
                                                    self.add_item(self.Name)

                                                async def callback(self, interaction: nextcord.Interaction) -> None:
                                                    name = self.Name.value
                                                    for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                        r = interaction.guild.get_role(role[0])
                                                        
                                                        await r.edit(name = name)
                                                        ec.execute(f'UPDATE balance SET bal={bal[0] - 250}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                                        ec_db.commit() 
                                                        embed = nextcord.Embed(description = f'Ты успешно переименовал свою роль.\n\nНовое название: **{name}**', color=0x2b2d31)
                                                        embed.set_thumbnail(url=interaction.user.display_avatar)
                                                        await interaction.send(embed=embed, ephemeral= True)
                                            await interaction.response.send_modal(rename())

                                else:
                                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)

                            @nextcord.ui.button(label = 'Выдать роль', style = nextcord.ButtonStyle.grey, disabled=False)
                            async def give(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                if owner.id == interaction.user.id:
                                    for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):

                                    
                                        if bal[0] < 100:
                                            embed=nextcord.Embed(description = "Стоимость данной функции 100 монет", color=0x2b2d31)
                                            await interaction.send(embed = embed, ephemeral=True)      
                                        else:     
                                                        
                                            if owner.id == interaction.user.id:
                                                er=nextcord.Embed(description="Укажи **человека** или его **id** которому хочешь дать свою роль^^", color=0x2b2d31)
                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                
                                                await interaction.edit(embed=er, view = None)

                                                try:
                                                    msg = await bot.wait_for('message', check=lambda m: m.author.id == interaction.user.id, timeout = 30)
                                                    s = msg.content

                                                    member = re.sub("[<@!>]","",s)
                                                    try:
                                                        user =   interaction.guild.get_member(int(member))
                                                        if r1 in user.roles:  
                                                            await msg.delete()
                                                            embed = nextcord.Embed(description = f'У {user.mention} уже есть твоя роль', color=0x2b2d31)
                                                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                            embed.set_footer(text='Через 5 секунды, ты будешь отправлен в главное меню')
                                                            await interaction.edit(embed=embed, view = None)
                                                            await asyncio.sleep(5)
                                                            for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                                embed1=nextcord.Embed(title = 'Меню управления ролью', description='Твоя роль: <@&{}>'.format(role[0]), color=0x2b2d31)
                                                                embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                                embed1.set_footer(text='/role_manager - меню управления личной ролью')
                                                                await interaction.send(embed = embed1, view=reset())
                                                                            

                                                        else:
                                                            for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                                await msg.delete()
                                                                r = interaction.guild.get_role(role[0])
                                                                ec.execute(f'UPDATE balance SET bal={bal[0] - 100}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                                                ec_db.commit() 
                                                                await user.add_roles(r)
                                                                embed = nextcord.Embed(description = f'Роль {r.mention} успешно, была одета на участника {user.mention}', color=0x2b2d31)
                                                                embed.set_thumbnail(url=interaction.user.display_avatar)
                                                                await interaction.edit(embed=embed, view = None)     

                                                                embed1 = nextcord.Embed(description = f'На вас была одета роль {r.name}', color=0x2b2d31)
                                                                embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                                await user.send(embed=embed1)       
                                                            
                                                    except:
                                                        await msg.delete()
                                                        embed = nextcord.Embed(description = f'Ошибка в конвертирование str в member. Скорее всего ты пытаешься **str(**{msg.content}**)** конвертировать в **member(**{msg.content}**)**.\n\n"Входные данные не является id или mention user | Ты не указал id или mention user"', color=0x2b2d31)
                                                        embed.set_footer(text='Через 5 секунды, ты будешь отправлен в главное меню')
                                                        await interaction.edit(embed=embed, view = None)
                                                        await asyncio.sleep(5)
                                                        for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                            embed1=nextcord.Embed(title = 'Меню управления ролью', description='Твоя роль: <@&{}>'.format(role[0]), color=0x2b2d31)
                                                            embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                            embed1.set_footer(text='/role_manager - меню управления личной ролью')
                                                            await interaction.send(embed = embed1, view=reset()) 
                                                            
                                                except asyncio.exceptions.TimeoutError:
                                                    embed = nextcord.Embed(description = f'Время на выполнения данной команды вышло', color=0x2b2d31)
                                                    embed.set_footer(text='Через 5 секунды, ты будешь отправлен в главное меню')
                                                    await interaction.edit(embed=embed, view = None)
                                                    await asyncio.sleep(5)
                                                    for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                        embed1=nextcord.Embed(title = 'Меню управления ролью', description='Твоя роль: <@&{}>'.format(role[0]), color=0x2b2d31)
                                                        embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                        embed1.set_footer(text='/role_manager - меню управления личной ролью')
                                                        await interaction.send(embed = embed1, view=reset())
                                else:
                                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)  

                            @nextcord.ui.button(label = 'Cнять роль', style = nextcord.ButtonStyle.grey, disabled=False)
                            async def remove(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                if owner.id == interaction.user.id:
                                    for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):


                                        if bal[0] < 100:
                                            embed=nextcord.Embed(description = "Стоимость данной функции 100 монет", color=0x2b2d31)
                                            await interaction.send(embed = embed, ephemeral=True)      
                                        else:                            
                            
                            
                            
                                            
                                                er=nextcord.Embed(description="Укажи **человека** или его **id** c которого хочешь снять свою роль^^", color=0x2b2d31)
                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                
                                                await interaction.edit(embed=er, view = None)

                                                try:
                                                    msg = await bot.wait_for('message', check=lambda m: m.author.id == interaction.user.id, timeout = 30)
                                                    s = msg.content

                                                    member = re.sub("[<@!>]","",s)
                                                    try:
                                                        user =   interaction.guild.get_member(int(member))
                                                        if r1 in user.roles:  
                                                            for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                                await msg.delete()
                                                                r = interaction.guild.get_role(role[0])
                                                                ec.execute(f'UPDATE balance SET bal={bal[0] - 100}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                                                ec_db.commit() 
                                                                await user.remove_roles(r)
                                                                embed = nextcord.Embed(description = f'Роль {r.mention} успешно, была снята с участника {user.mention}', color=0x2b2d31)
                                                                embed.set_thumbnail(url=interaction.user.display_avatar)
                                                                await interaction.edit(embed=embed, view = None)        

                                                                embed1 = nextcord.Embed(description = f'Владелец роли {r.name}, решил забрать у тебя эту роль.', color=0x2b2d31)
                                                                embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                                await user.send(embed=embed1)                           
                                                        
                                                        else:       
                                                            await msg.delete()
                                                            embed = nextcord.Embed(description = f'У {user.mention} нету твоей роли', color=0x2b2d31)
                                                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                            embed.set_footer(text='Через 5 секунды, ты будешь отправлен в главное меню')
                                                            await interaction.edit(embed=embed, view = None)
                                                            await asyncio.sleep(5)
                                                            for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                                embed1=nextcord.Embed(title = 'Меню управления ролью', description='Твоя роль: <@&{}>'.format(role[0]), color=0x2b2d31)
                                                                embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                                embed1.set_footer(text='/role_manager - меню управления личной ролью')
                                                                await interaction.send(embed = embed1, view=reset())                       
                                                            

                                                    except:
                                                        await msg.delete()
                                                        embed = nextcord.Embed(description = f'Ошибка в конвертирование str в member. Скорее всего ты пытаешься **str(**{msg.content}**)** конвертировать в **member(**{msg.content}**)**.\n\n"Входные данные не является id или mention user | Ты не указал id или mention user"', color=0x2b2d31)
                                                        embed.set_footer(text='Через 5 секунды, ты будешь отправлен в главное меню')
                                                        await interaction.edit(embed=embed, view = None)
                                                        await asyncio.sleep(5)
                                                        for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                            embed1=nextcord.Embed(title = 'Меню управления ролью', description='Твоя роль: <@&{}>'.format(role[0]), color=0x2b2d31)
                                                            embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                            embed1.set_footer(text='/role_manager - меню управления личной ролью')
                                                            await interaction.send(embed = embed1, view=reset()) 
                                                            
                                                except asyncio.exceptions.TimeoutError:
                                                    embed = nextcord.Embed(description = f'Время на выполнения данной команды вышло', color=0x2b2d31)
                                                    embed.set_footer(text='Через 5 секунды, ты будешь отправлен в главное меню')
                                                    await interaction.edit(embed=embed, view = None)
                                                    await asyncio.sleep(5)
                                                    for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                        embed1=nextcord.Embed(title = 'Меню управления ролью', description='Твоя роль: <@&{}>'.format(role[0]), color=0x2b2d31)
                                                        embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                        embed1.set_footer(text='/role_manager - меню управления личной ролью')
                                                        await interaction.send(embed = embed1, view=reset())  
                                else:
                                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)

                            @nextcord.ui.button(label = 'Список участников', style = nextcord.ButtonStyle.grey, disabled=False)
                            async def list(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                if owner.id == interaction.user.id:
                                    class quit(nextcord.ui.View):
                                        def __init__(self):
                                            super().__init__(timeout=60)
                                            
                                        @nextcord.ui.button(label = 'Назад', style = nextcord.ButtonStyle.red, disabled=False)
                                        async def quit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                            if owner.id == interaction.user.id:
                                                for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                    embed=nextcord.Embed(title = 'Меню управления ролью', description='Твоя роль: <@&{}>'.format(role[0]), color=0x2b2d31)
                                                    embed.set_thumbnail(url=interaction.user.display_avatar)
                                                    embed.set_footer(text='/role_manager - меню управления личной ролью')
                                                    await interaction.edit(embed = embed, view=reset())   
                                            else:
                                                embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                await interaction.send(embed=embed, ephemeral= True)

                                    data = "\n".join([(member.name or member.nick) for member in r1.members])
                                    embed=nextcord.Embed(title=f"Список участников с вашей ролью\n", description=f"{data}\n", color=0x2b2d31)
                                    await interaction.edit(embed=embed, view = quit())
                                else:
                                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)

                            @nextcord.ui.button(label = 'Сменить цвет', style = nextcord.ButtonStyle.grey, disabled=False)
                            async def color(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                if owner.id == interaction.user.id:  
                                    ec_db = sqlite3.connect('database/economy.db', timeout=10)
                                    ec = ec_db.cursor()   
                                    for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):

                                            if bal[0] < 250:
                                                embed=nextcord.Embed(description = "Стоимость данной функции 250 монет", color=0x2b2d31)
                                                await interaction.send(embed = embed, ephemeral=True)      
                                            else:     
                                                
                                                    ec_db = sqlite3.connect('database/economy.db', timeout=10)
                                                    ec = ec_db.cursor() 
                                                    class color(nextcord.ui.Modal):
                                                        def __init__(self):
                                                            super().__init__('Настройка личной роли')
                                                            
                                                            self.Color = nextcord.ui.TextInput(label = 'Цвет роли в HEX коде:', min_length=6, max_length=6, required=True, placeholder='Пример: 912f41', style=nextcord.TextInputStyle.paragraph)
                                                            self.add_item(self.Color)



                                                            




                                                        async def callback(self, interaction: nextcord.Interaction) -> None:
                                                            color = self.Color.value

                                                            for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                                r = interaction.guild.get_role(role[0])
                                                                ec.execute(f'UPDATE balance SET bal={bal[0] - 250}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                                                ec_db.commit() 
                                                                await r.edit(color = int(color, 16))
                                                                embed = nextcord.Embed(description = f'Ты успешно сменил цвет своей роли.\n\nНовый цвет сейчас применен к рамке данного embed', color=int(color, 16))
                                                                embed.set_thumbnail(url=interaction.user.display_avatar)
                                                                await interaction.send(embed=embed, ephemeral= True)

                                                    await interaction.response.send_modal(color())
                                else:
                                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)

                            @nextcord.ui.button(label = 'Сменить иконку', style = nextcord.ButtonStyle.grey, disabled=True)
                            async def icon(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):

                                if owner.id == interaction.user.id:  
                                    ec_db = sqlite3.connect('database/economy.db', timeout=10)
                                    ec = ec_db.cursor() 
                                    for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):

                                    
                                        if bal[0] < 750:
                                            embed=nextcord.Embed(description = "Стоимость данной функции 750 монет", color=0x2b2d31)
                                            await interaction.send(embed = embed, ephemeral=True)      
                                        else:     
                                            embed = nextcord.Embed(description=f'Укажи id эмодзи (ID доступных иконок, ты можешь узнать по команде /iconpack)', color=0x2b2d31)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)
                                            await interaction.send(embed=embed, ephemeral= True)
                                    
                                            try:
                                                msg = await bot.wait_for('message', timeout= 30, check=lambda m: m.author.id == interaction.user.id)
                                                s1 = msg.content
                                                id1 = int(s1)
                                                await msg.delete()
                                                try:
                                                    emoji = bot.get_emoji(id1)
                                                    for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                        r = interaction.guild.get_role(role[0])
                                                        
                                                        await r.edit(icon=emoji)
                                                        embed = nextcord.Embed(description = f'Ты успешно сменил иконку своей роли\n\nНовая иконка: {emoji}', color=0x2b2d31)
                                                        embed.set_thumbnail(url=interaction.user.display_avatar)
                                                        await interaction.send(embed=embed, ephemeral= True)
                                                        

                                                except Exception as E: 
                                                    embed = nextcord.Embed(description=f'Неизвестная ошибка. Скорее всего ты пытаешься поставить эмодзи которой нету на сервере или вовсе это не **id emoji**', color=0x2b2d31)
                                                    embed.set_thumbnail(url=interaction.user.display_avatar)
                                                    await interaction.send(embed=embed, ephemeral= True)  

                                            except asyncio.exceptions.TimeoutError:
                                                embed = nextcord.Embed(description=f'Действия команды были отменены.', color=0x2b2d31)
                                                embed.set_thumbnail(url=interaction.user.display_avatar)
                                                await interaction.send(embed=embed,ephemeral= True)  


                                


                                else:
                                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)

                            @nextcord.ui.button(label = '! Удалить !', style = nextcord.ButtonStyle.red, disabled=False)
                            async def deleterole(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                if owner.id == interaction.user.id:  
                                    ec_db = sqlite3.connect('database/economy.db', timeout=10)
                                    ec = ec_db.cursor() 
                                    class dress(nextcord.ui.View):
                                        def __init__(self):
                                            super().__init__(timeout=60)

                                        @nextcord.ui.button(label = 'Да', style = nextcord.ButtonStyle.red, disabled=False)
                                        async def yes(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):   
                                            if owner.id == interaction.user.id:  
                                                for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                    r = interaction.guild.get_role(role[0])
                                                    name = r.name
                                                    await r.delete()
                                                    for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                                        ec.execute(f'UPDATE balance SET bal={bal[0] + int(backup)}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                                        ec.execute(f"DELETE FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}")
                                                        ec.execute(f"DELETE FROM shop where owner={interaction.user.id}")
                                                        task.execute(f"DELETE FROM tasks where id={interaction.user.id} and guild_id = {interaction.guild.id} and name='role'")
                                                        task_db.commit()
                                                        embed=nextcord.Embed(description = f"Ты успешно удалил свою личную роль: {name}.", color=0x2b2d31)
                                                        embed.set_thumbnail(url=interaction.user.display_avatar)
                                                        await interaction.edit(embed = embed, view=None) 
                                                    ec_db.commit() 
                                            else:
                                                embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                await interaction.send(embed=embed, ephemeral= True)    

                                        @nextcord.ui.button(label = 'Нет', style = nextcord.ButtonStyle.grey, disabled=False)
                                        async def no(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):  
                                            if owner.id == interaction.user.id:  
                                                embed = nextcord.Embed(description = f'Действия для данной команды было отменено', color=0x2b2d31)
                                                embed.set_footer(text='Через 5 секунды, ты будешь отправлен в главное меню')
                                                await interaction.edit(embed=embed, view = None)
                                                await asyncio.sleep(5)
                                                for role in ec.execute(f"SELECT role FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                    embed1=nextcord.Embed(title = 'Меню управления ролью', description='Твоя роль: <@&{}>'.format(role[0]), color=0x2b2d31)
                                                    embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                    embed1.set_footer(text='/role_manager - меню управления личной ролью')
                                                    await interaction.send(embed = embed1, view=reset())  
                                            else:
                                                embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                await interaction.send(embed=embed, ephemeral= True)    

                                    embed = nextcord.Embed(description = f'Данное действие нельзя будет потом отменить. Ты уверен что ты хочешь продолжить?', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)
                                    embed.set_footer(text='После продажи данного товара, ты получишь 30% от стоимости товара')
                                    await interaction.edit(embed=embed, view=dress())


                                else:
                                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)                        

                            @nextcord.ui.button(label = 'Назад', style = nextcord.ButtonStyle.red, disabled=False)
                            async def delete(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                if owner.id == interaction.user.id:
                                    await interaction.message.delete()
                                    embed = nextcord.Embed(description = f'Сообщение успешно было удалено.', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)
                                else:
                                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)



                        if r1 is None:
                            class refund(nextcord.ui.View):
                                def __init__(self):
                                    super().__init__(timeout=60)

                                @nextcord.ui.button(label = 'Вернуть денежные средства', style = nextcord.ButtonStyle.red, disabled=False)
                                async def restore(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                    if owner.id == interaction.user.id:  
                                        
                                        for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                            ec.execute(f"DELETE FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}")
                                            ec.execute(f"DELETE FROM shop where owner={interaction.user.id}")
                                            task.execute(f"DELETE FROM tasks where id={interaction.user.id} and guild_id = {interaction.guild.id} and name='role'")
                                            task_db.commit()
                                            ec_db.commit() 
                                            embed=nextcord.Embed(description = f"Ты успешно **оформил** **возврат денежных средств** за **удаленный** товар\nВ течение **минуты** деньги поступят на твой счет", color=0x2b2d31)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)
                                            await interaction.edit(embed = embed, view=None) 
                                            time = random.randint(10, 60)
                                            print(time)
                                            await asyncio.sleep(time)
                                            ec.execute(f'UPDATE balance SET bal={bal[0] + int(backup)}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                            emb=nextcord.Embed(title=f"**Поступление монет**", description = f"Комиссия с перевода: Отсутсвтует", color=0x2b2d31)
                                            emb.add_field(name = 'Получатель:', value=interaction.user.mention, inline=False)
                                            emb.add_field(name = 'Отправитель:', value=interaction.guild.name, inline=False)
                                            emb.add_field(name = 'Комментарий:', value='**Возврат** денежных **средств** за товар: `Личная роль`', inline=False)
                                            emb.add_field(name = 'Сумма', value=f'{backup}', inline=False)
                                            await interaction.user.send(embed=emb)
                                        ec_db.commit() 
                                    else:
                                        embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)

                            embed=nextcord.Embed(title = 'Меню управления ролью', description='~~Твоя роль: None~~\n\nТвоя роль **не была найдена**, в списке **ролей**. Для вас доступна **функция** возврата **денежных средств.**', color=0x2b2d31)
                            for bal in ec.execute(f"SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}"):
                                embed.set_footer(text=f'Баланс: {bal[0]}')
                            embed.set_thumbnail(url=interaction.user.display_avatar)
                            
                            await interaction.send(embed = embed, view=refund())



                        else:

                            for row in task.execute(f"SELECT date FROM tasks WHERE id={interaction.user.id} and guild_id = {interaction.guild.id} and name = 'role'"):
                                

                                embed=nextcord.Embed(title = 'Меню управления ролью', description='Твоя роль: {}\n\nСрок действия предмета истекает <t:{}:R>'.format(r1.mention, math.trunc(row[0])), color=0x2b2d31)
                                for bal in ec.execute(f"SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}"):
                                    embed.set_footer(text=f'Баланс: {bal[0]} | Автооплата: {ec.execute(f"SELECT auto FROM role where id={interaction.user.id} and guild_id = {interaction.guild.id}").fetchone()[0]}')
                                embed.set_thumbnail(url=interaction.user.display_avatar)
                                
                                await interaction.send(embed = embed, view=reset())

    @nextcord.slash_command(description="Посмотреть свой инвентарь", guild_ids = [int(settings["Guild_ID"])])
    async def inventory(self, interaction: nextcord.Interaction, member : nextcord.Member = None):
        user = member or interaction.user
        owner = interaction.user
        ec_db = sqlite3.connect('database/economy.db', timeout=10)
        ec = ec_db.cursor() 

        def money(amount : int, case1 : str):
            ec.execute(f'UPDATE balance SET bal=bal+{amount}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
            ec_db.commit()
            embed=nextcord.Embed(title = 'Ваш приз:', description=f"Вам выпало **{amount} коинов**, валюта уже была зачислена на ваш аккаунт", color=0x2b2d31)
            embed.add_field(name="Кейсы:", value="```Обычный кейс - {} шт.\rПремиум кейс - {} шт.\rОнлайн кейс - {} шт.\rЛюбовный кейс - {} шт.```".format(
                ec.execute(f"SELECT case_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
                ec.execute(f"SELECT casepremium_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
                ec.execute(f"SELECT caseonline_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
                ec.execute(f"SELECT casemarry_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), inline=False)
            embed.set_thumbnail(url=user.display_avatar)
            embed.set_footer(text=f"Вы открыли - {case1} кейс")
            return main.edit(embed=embed, view = case()) 
        
        def multiplier(multiplier : int, case1: str):
            if multiplier == 2:
                ec.execute(f'UPDATE inventory SET multiplier2x_=multiplier2x_+1  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                ec_db.commit()
                embed=nextcord.Embed(title = 'Ваш приз:', description="Вам выпал **Множитель 2x коинов на час**, предмет уже был добавлен в ваш инвентарь", color=0x2b2d31)
                embed.add_field(name="Кейсы:", value="```Обычный кейс - {} шт.\rПремиум кейс - {} шт.\rОнлайн кейс - {} шт.\rЛюбовный кейс - {} шт.```".format(
                    ec.execute(f"SELECT case_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
                    ec.execute(f"SELECT casepremium_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
                    ec.execute(f"SELECT caseonline_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
                    ec.execute(f"SELECT casemarry_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), inline=False)
                embed.set_thumbnail(url=user.display_avatar)
                embed.set_footer(text=f"Вы открыли - {case1} кейс")
                return main.edit(embed=embed, view = case()) 
            elif multiplier == 3:
                ec.execute(f'UPDATE inventory SET multiplier3x_=multiplier3x_+1  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                ec_db.commit()
                embed=nextcord.Embed(title = 'Ваш приз:', description="Вам выпал **Множитель 3x коинов на час**, предмет уже был добавлен в ваш инвентарь", color=0x2b2d31)
                embed.add_field(name="Кейсы:", value="```Обычный кейс - {} шт.\rПремиум кейс - {} шт.\rОнлайн кейс - {} шт.\rЛюбовный кейс - {} шт.```".format(
                    ec.execute(f"SELECT case_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
                    ec.execute(f"SELECT casepremium_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
                    ec.execute(f"SELECT caseonline_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
                    ec.execute(f"SELECT casemarry_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), inline=False)

                embed.set_thumbnail(url=user.display_avatar)
                embed.set_footer(text=f"Вы открыли - {case1} кейс")
                return main.edit(embed=embed, view = case()) 
            elif multiplier == 5:
                ec.execute(f'UPDATE inventory SET multiplier5x_=multiplier5x_+1  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                ec_db.commit()
                embed=nextcord.Embed(title = 'Ваш приз:', description="Вам выпал **Множитель 5x коинов на час**, предмет уже был добавлен в ваш инвентарь", color=0x2b2d31)
                embed.add_field(name="Кейсы:", value="```Обычный кейс - {} шт.\rПремиум кейс - {} шт.\rОнлайн кейс - {} шт.\rЛюбовный кейс - {} шт.```".format(
                    ec.execute(f"SELECT case_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
                    ec.execute(f"SELECT casepremium_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
                    ec.execute(f"SELECT caseonline_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
                    ec.execute(f"SELECT casemarry_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), inline=False)

                embed.set_thumbnail(url=user.display_avatar)
                embed.set_footer(text=f"Вы открыли - {case1} кейс")
                return main.edit(embed=embed, view = case()) 
            
        def custom(type : str, case1: str):
            if type == "role":
                ec.execute(f'UPDATE inventory SET customrole_= customrole_ + 1  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                ec_db.commit()
                embed=nextcord.Embed(title = 'Ваш приз:', description="Вам выпало **Личная комната**, предмет уже был добавлен в ваш инвентарь", color=0x2b2d31)
                embed.add_field(name="Кейсы:", value="```Обычный кейс - {} шт.\rПремиум кейс - {} шт.\rОнлайн кейс - {} шт.\rЛюбовный кейс - {} шт.```".format(
                    ec.execute(f"SELECT case_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
                    ec.execute(f"SELECT casepremium_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
                    ec.execute(f"SELECT caseonline_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
                    ec.execute(f"SELECT casemarry_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), inline=False) 
                embed.set_thumbnail(url=user.display_avatar)
                embed.set_footer(text=f"Вы открыли - {case1} кейс")
                return main.edit(embed=embed, view = case())  
            elif type == "channel":
                ec.execute(f'UPDATE inventory SET customchannel_= customchannel_ + 1  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                ec_db.commit()
                embed=nextcord.Embed(title = 'Ваш приз:', description="Вам выпала **Личная комната**, предмет уже был добавлен в ваш инвентарь", color=0x2b2d31)
                embed.add_field(name="Кейсы:", value="```Обычный кейс - {} шт.\rПремиум кейс - {} шт.\rОнлайн кейс - {} шт.\rЛюбовный кейс - {} шт.```".format(
                    ec.execute(f"SELECT case_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
                    ec.execute(f"SELECT casepremium_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
                    ec.execute(f"SELECT caseonline_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
                    ec.execute(f"SELECT casemarry_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), inline=False)

                embed.set_thumbnail(url=user.display_avatar)
                embed.set_footer(text=f"Вы открыли - {case1} кейс")
                return main.edit(embed=embed, view = case()) 

        class case(nextcord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)
                self.add_item(category())

            if ec.execute(f"SELECT case_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:       
                @nextcord.ui.button(label = 'Открыть обычный кейс', style = nextcord.ButtonStyle.blurple, disabled=True)
                async def item1_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                    pass
            else:
                @nextcord.ui.button(label = 'Открыть обычный кейс', style = nextcord.ButtonStyle.blurple, disabled=False)
                async def item1_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                    if owner.id == interaction.user.id: 
                        if ec.execute(f"SELECT case_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] <= 0:
                            embed = nextcord.Embed(description = f'У вас нет обычных кейсов', color=0x2b2d31)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                        else:
                            percent = random.randint(1, 100)
                            ec.execute(f'UPDATE inventory SET case_=case_-1  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                            ec_db.commit()
                            print(percent)
                            if percent >= 1 and percent <= 50:
                                await money(100, "Обычный")
                            elif percent >= 51 and percent <= 79:
                                await money(250, "Обычный")
                            elif percent >= 80 and percent <= 94:

                                item = random.randint(1, 2)
                                if item == 1:
                                    await money(600, "Обычный") 
                                elif item == 2:
                                    await multiplier(2, "Обычный")
                                        
                            elif percent >= 95 and percent <= 100:
                                item = random.randint(1, 2)
                                if item == 1:
                                    await custom('role', "Обычный")
                                elif item == 2:
                                    await custom('channel', "Обычный")

                        
                            if ec.execute(f"SELECT case_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                self.item1_.disabled = True
                            if ec.execute(f"SELECT casepremium_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0: 
                                self.item2_.disabled = True                
                            if ec.execute(f"SELECT caseonline_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                self.item3_.disabled = True
                            if ec.execute(f"SELECT casemarry_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                self.item4_.disabled = True
                            await interaction.response.edit_message(view=self)  
                    else:
                        embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                        await interaction.send(embed=embed, ephemeral= True)
            if ec.execute(f"SELECT casepremium_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:       
                @nextcord.ui.button(label = 'Открыть премиум кейс', style = nextcord.ButtonStyle.blurple, disabled=True)
                async def item2_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                    pass
            else:
                @nextcord.ui.button(label = 'Открыть премиум кейс', style = nextcord.ButtonStyle.blurple, disabled=False)
                async def item2_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                    if owner.id == interaction.user.id: 
                        if ec.execute(f"SELECT casepremium_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] <= 0: 
                            embed = nextcord.Embed(description = f'У вас нет премиум кейсов', color=0x2b2d31)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                        else:
                            percent = random.randint(1, 100)
                            ec.execute(f'UPDATE inventory SET casepremium_=casepremium_-1  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                            ec_db.commit()
                            if percent >= 1 and percent <= 40:
                                await money(300, "Премиум")
                            elif percent >= 41 and percent <= 74:
                                await multiplier(2, "Премиум")
                            elif percent >= 75 and percent <= 89:

                                item = random.randint(1, 2)
                                if item == 1:
                                    await money(1000, "Премиум")
                                elif item == 2:
                                    await multiplier(3, "Премиум")                                 
                            elif percent >= 90 and percent <= 100:
                                item = random.randint(1, 3)
                                if item == 1:
                                    await custom("role", "Премиум")
                                elif item == 2:
                                    await custom("channel", "Премиум")
                                elif item == 3:
                                    await multiplier(5, "Премиум")       

                            
                            if ec.execute(f"SELECT case_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                self.item1_.disabled = True
                            if ec.execute(f"SELECT casepremium_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0: 
                                self.item2_.disabled = True                
                            if ec.execute(f"SELECT caseonline_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                self.item3_.disabled = True
                            if ec.execute(f"SELECT casemarry_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                self.item4_.disabled = True
                            await interaction.response.edit_message(view=self)           
                    else:
                        embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                        await interaction.send(embed=embed, ephemeral= True)
            if ec.execute(f"SELECT caseonline_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:       
                @nextcord.ui.button(label = 'Открыть онлайн кейс', style = nextcord.ButtonStyle.blurple, disabled=True)
                async def item3_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                    pass
            else:
                @nextcord.ui.button(label = 'Открыть онлайн кейс', style = nextcord.ButtonStyle.blurple, disabled=False)
                async def item3_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                    if owner.id == interaction.user.id:
                        if ec.execute(f"SELECT caseonline_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] <= 0: 
                            embed = nextcord.Embed(description = f'У вас нет онлайн кейсов', color=0x2b2d31)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                        else:
                            percent = random.randint(1, 100)
                            ec.execute(f'UPDATE inventory SET caseonline_=caseonline_-1  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                            ec_db.commit()
                            if percent >= 1 and percent <= 50:
                                await money(20, "Онлайн") 
                            elif percent >= 51 and percent <= 79:
                                await money(150, "Онлайн") 
                            elif percent >= 80 and percent <= 94:
                                await money(310, "Онлайн")                                
                            elif percent >= 95 and percent <= 100:
                                await custom("channel", "Онлайн") 
                                    

                            if ec.execute(f"SELECT case_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                self.item1_.disabled = True
                            if ec.execute(f"SELECT casepremium_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0: 
                                self.item2_.disabled = True                
                            if ec.execute(f"SELECT caseonline_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                self.item3_.disabled = True
                            if ec.execute(f"SELECT casemarry_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                self.item4_.disabled = True
                            await interaction.response.edit_message(view=self)
                    else:
                        embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                        await interaction.send(embed=embed, ephemeral= True)  

            if ec.execute(f"SELECT casemarry_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:       
                @nextcord.ui.button(label = 'Открыть любовный кейс', style = nextcord.ButtonStyle.blurple, disabled=True)
                async def item4_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                    pass
            else:
                @nextcord.ui.button(label = 'Открыть любовный кейс', style = nextcord.ButtonStyle.blurple, disabled=False)
                async def item4_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                    if owner.id == interaction.user.id:    
                        if ec.execute(f"SELECT casemarry_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] <= 0:
                            embed = nextcord.Embed(description = f'У вас нет любовных кейсов', color=0x2b2d31)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                        else:
                            percent = random.randint(1, 100)
                            ec.execute(f'UPDATE inventory SET casemarry_=casemarry_-1  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                            ec_db.commit()
                            if percent >= 1 and percent <= 40:
                                await money(200, "Любовный") 
                            elif percent >= 41 and percent <= 75:
                                await multiplier(2, "Любовный") 
                            elif percent >= 76 and percent <= 89:
                                item = random.randint(1, 2)
                                if item == 1:
                                    await money(500, "Любовный")
                                elif item == 2:
                                    await multiplier(3, "Любовный")                                
                            elif percent >= 90 and percent <= 100:
                                await multiplier(5, "Любовный")  
                                

                            if ec.execute(f"SELECT case_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                self.item1_.disabled = True
                            if ec.execute(f"SELECT casepremium_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0: 
                                self.item2_.disabled = True                
                            if ec.execute(f"SELECT caseonline_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                self.item3_.disabled = True
                            if ec.execute(f"SELECT casemarry_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                self.item4_.disabled = True
                            await interaction.response.edit_message(view=self)  
                    else:
                        embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                        await interaction.send(embed=embed, ephemeral= True)
            
            @nextcord.ui.button(label = '', emoji="<:question1:1082220951250403349>", style = nextcord.ButtonStyle.gray, disabled=False)
            async def info(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                embed=nextcord.Embed(title="Информация о кейсах", color=0x2b2d31)
                embed.add_field(name="Обычный кейс:", value="```100 коинов - 50%\r250 коинов - 30%\r600 коинов/2x на час - 15%\rЛичная роль/Личная комната - 5%\r\rПамятка: С каждых 100 кейсов гарантированно выпадет: Личная комната/Личная роль```", inline=False)
                embed.add_field(name="Онлайн кейс:", value="```20 коинов - 50%\r150 коинов - 30%\r310 коинов - 15%\rЛичная роль - 5%\r\rПамятка: С каждых 100 кейсов гарантированно выпадет: Личная роль```", inline=False)
                embed.add_field(name="Премиум кейс:", value="```300 коинов - 40%\r2x на час - 35%\r1000 коинов/3x на час - 15%\rЛичная роль/Личная комната/5x на час - 10%\r\rПамятка: С каждых 100 кейсов гарантированно выпадет: Личная комната/Личная роль/5x на час```", inline=False)
                embed.add_field(name="Любовный кейс:", value="```200 коинов - 40%\r2x на час - 35%\r500 коинов/3x на час - 15%\r5x на час - 10%\r\rПамятка: С каждых 100 кейсов гарантированно выпадет: 5x на час```", inline=False)
                embed.set_thumbnail(url=user.display_avatar)
                await interaction.send(embed=embed, ephemeral=True)
                                 
        class item(nextcord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)
                self.add_item(category())

            if ec.execute(f"SELECT customrole_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:       
                @nextcord.ui.button(label = 'Активировать Личную роль', style = nextcord.ButtonStyle.blurple, disabled=True)
                async def item1_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                    pass
            else:
                @nextcord.ui.button(label = 'Активировать Личную роль', style = nextcord.ButtonStyle.blurple, disabled=False)
                async def item1_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                    if owner.id == interaction.user.id:
                        ec_db = sqlite3.connect('database/economy.db', timeout=10)
                        ec = ec_db.cursor()
                        if ec.execute(f"SELECT customrole_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] <= 0: 
                            embed = nextcord.Embed(description = f'У вас нет личных ролей', color=0x2b2d31)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                        else:
                            category_role = interaction.guild.get_role(int(settings["custom_role_category"]))
                            member = interaction.user
                            ec_db = sqlite3.connect('database/economy.db', timeout=10)
                            ec = ec_db.cursor() 
                            cost = int(settings['cost_role'])
                            ec.execute(f"SELECT id FROM role where id={interaction.user.id} and guild_id={interaction.guild.id}")
                            if ec.fetchone() is None:

                                class color(nextcord.ui.Modal):
                                    def __init__(self):
                                        super().__init__('Создание личной роли')
                                        
                                        self.Name = nextcord.ui.TextInput(label = 'Название роли:', min_length=1, max_length=50, required=True, placeholder='Пример: я люблю рутика', style=nextcord.TextInputStyle.paragraph)
                                        self.add_item(self.Name)

                                        self.Color = nextcord.ui.TextInput(label = 'Цвет роли в HEX коде:', min_length=6, max_length=6, required=True, placeholder='Пример: 912f41', style=nextcord.TextInputStyle.paragraph)
                                        self.add_item(self.Color)



                                        




                                    async def callback(self, interaction: nextcord.Interaction) -> None:
                                        name = self.Name.value
                                        color = self.Color.value

                                        role = await interaction.guild.create_role(name=name, color=int(color, 16))
                                        
                                        ec.execute(f"INSERT INTO role VALUES ('{member.id}', '{interaction.guild.id}', '{role.id}', 0, 'open', 'off')")
                                        await role.edit(position=category_role.position-1)
                                        for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):

                                            bloop = (datetime.now() + timedelta(days=30)).timestamp()
                                            task.execute(f"INSERT INTO tasks VALUES ('role','{bloop}','{interaction.user.id}', '{interaction.guild.id}')")
                                            task_db.commit()

                                            ec.execute(f'UPDATE inventory SET customrole_=customrole_-1  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                            await member.add_roles(role)
                                            embed=nextcord.Embed(title = 'Создание личной роли', description = f"Ты успешно создал роль {role.mention}", color=0x2b2d31)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)
                                            embed.set_footer(text='/role_manager - меню управления личной ролью')
                                            await interaction.send(embed = embed) 
                                        ec_db.commit() 
                                        if ec.execute(f"SELECT customchannel_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                            item().item1_.disabled = True
                                        if ec.execute(f"SELECT customrole_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0: 
                                            item().item1_.disabled = True                
                                        await interaction.response.edit_message(view=self)  
                                
                                if ec.execute(f"SELECT customrole_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                    embed=nextcord.Embed( description = f"Данный предмет закончился (", color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar) 
                                    await interaction.send(embed = embed, ephemeral=True)
                                else:    
                                    await interaction.response.send_modal(color())

                            else:        
                                embed = nextcord.Embed(description = f'У тебя уже имеется личная роль. Данный слот можно, будет Продать/Подарить или использовать для продления текущей роли^^', color=0x2b2d31)
                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                await interaction.send(embed=embed, ephemeral= True)   
                    else:
                        embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                        await interaction.send(embed=embed, ephemeral= True)           
                    

            if ec.execute(f"SELECT customchannel_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:       
                @nextcord.ui.button(label = 'Активировать Личную комнату', style = nextcord.ButtonStyle.blurple, disabled=True)
                async def item2_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                    pass
            else:
                @nextcord.ui.button(label = 'Активировать Личную комнату', style = nextcord.ButtonStyle.blurple, disabled=False)
                async def item2_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                    if owner.id == interaction.user.id:
                        ec_db = sqlite3.connect('database/economy.db', timeout=10)
                        ec = ec_db.cursor()
                        if ec.execute(f"SELECT customchannel_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] <= 0:
                            embed = nextcord.Embed(description = f'У вас нет личных комнат', color=0x2b2d31)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                        else:
                            member = interaction.user
                            ec_db = sqlite3.connect('database/economy.db', timeout=10)
                            ec = ec_db.cursor() 
                            cost = int(settings['cost_channel'])
                            ec.execute(f"SELECT id FROM channel where id={interaction.user.id} and guild_id={interaction.guild.id}")
                            if ec.fetchone() is None:

                                class color(nextcord.ui.Modal):
                                    def __init__(self):
                                        super().__init__('Создание личного войса')
                                        
                                        self.Name = nextcord.ui.TextInput(label = 'Название канала:', min_length=1, max_length=50, required=True, placeholder='Пример: zxc', style=nextcord.TextInputStyle.paragraph)
                                        self.add_item(self.Name)





                                        




                                    async def callback(self, interaction: nextcord.Interaction) -> None:
                                        name = self.Name.value
                                        overwrites = {
                                            interaction.guild.default_role: nextcord.PermissionOverwrite(connect = False),
                                            interaction.user: nextcord.PermissionOverwrite(connect = True),
                                        }
                                        category = nextcord.utils.get(interaction.guild.categories, id=int(settings['private_room']))
                                        channel = await interaction.guild.create_voice_channel(name=name, overwrites=overwrites, category=category)
                                        
                                        ec.execute(f"INSERT INTO channel VALUES ('{channel.id}','{member.id}', '{interaction.guild.id}', '0', 'open', 'off')")
                                        ec_db.commit()

                                        bloop = (datetime.now() + timedelta(days=30)).timestamp()
                                        task.execute(f"INSERT INTO tasks VALUES ('channel','{bloop}','{interaction.user.id}', '{interaction.guild.id}')")
                                        task_db.commit()

        
                                        ec.execute(f'UPDATE inventory SET  customchannel_=customchannel_-1   where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                        embed=nextcord.Embed(title = 'Создание личного войса', description = f"Ты успешно создал личный войс - {channel.mention}", color=0x2b2d31)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)
                                        embed.set_footer(text='/voice_manager - меню управления личным войсом')
                                        ec_db.commit() 
                                        await interaction.send(embed = embed)


                                if ec.execute(f"SELECT customchannel_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                    embed=nextcord.Embed( description = f"Данный предмет закончился (", color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar) 
                                    await interaction.send(embed = embed, ephemeral=True)
                                else:    
                                    await interaction.response.send_modal(color())


            
                            else:        
                                embed = nextcord.Embed(description = f'У тебя уже имеется личный канал. Данный слот можно, будет Продать/Подарить или использовать для продления текущего канала^^', color=0x2b2d31)
                                embed.set_thumbnail(url=interaction.user.display_avatar)      
                                embed.set_footer(text='/voice_manager - меню управления личной ролью') 
                                await interaction.send(embed=embed, ephemeral= True)           
                    else:
                        embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                        await interaction.send(embed=embed, ephemeral= True)

        class multiplier_(nextcord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)
                self.add_item(category())

            if ec.execute(f"SELECT multiplier2x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:       
                @nextcord.ui.button(label = 'Активировать 2x', style = nextcord.ButtonStyle.blurple, disabled=True)
                async def item1_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                    pass
            else:
                @nextcord.ui.button(label = 'Активировать 2x', style = nextcord.ButtonStyle.blurple, disabled=False)
                async def item1_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                    if owner.id == interaction.user.id:
                        if ec.execute(f"SELECT multiplier2x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] <= 0:
                            embed = nextcord.Embed(description = f'У вас нет 2х множителей', color=0x2b2d31)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                        else:
                            if ec.execute(f"SELECT multiplier FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == "None":
                                floot = (datetime.now() + timedelta(hours=1)).timestamp()
                                task.execute(f"INSERT INTO tasks VALUES ('multiplier','{floot}','{user.id}', '{interaction.guild.id}')")
                                ec.execute(f'UPDATE inventory SET multiplier3x_ = multiplier3x_ - 1  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                ec.execute(f'UPDATE balance SET multiplier = "3x"  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                ec_db.commit()
                                task_db.commit()

                                embed=nextcord.Embed(description=f"Ты успешно активировал(-a) **множитель 3x на час**", color=0x2b2d31)
                                embed.set_thumbnail(url=user.display_avatar)
                                await interaction.send(embed=embed, ephemeral=True)

                                embed=nextcord.Embed(title="Инвентарь пользователя - {}".format(user.name), color=0x2b2d31)
                                embed.set_thumbnail(url=user.display_avatar)
                                embed.add_field(name="Множители:", value="```5x на час - {} шт.\r3x на час - {} шт.\r2x на час - {} шт.```".format(
                                    ec.execute(f"SELECT multiplier5x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                                    ec.execute(f"SELECT multiplier3x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                                    ec.execute(f"SELECT multiplier2x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                                    inline=False)
                                await main.edit(embed=embed, view = multiplier())

                                if ec.execute(f"SELECT multiplier2x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                    self.item1_.disabled = True     
                                if ec.execute(f"SELECT multiplier3x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                    self.item2_.disabled = True    
                                if ec.execute(f"SELECT multiplier5x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                    self.item3_.disabled = True    
                                await interaction.response.edit_message(view=self) 
                            else:
                                embed=nextcord.Embed(description=f"У вас уже есть активный множитель", color=0x2b2d31)
                                embed.set_thumbnail(url=user.display_avatar)
                                await interaction.send(embed=embed, ephemeral=True) 
                    else:
                        embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                        await interaction.send(embed=embed, ephemeral= True)

            if ec.execute(f"SELECT multiplier3x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:       
                @nextcord.ui.button(label = 'Активировать 3x', style = nextcord.ButtonStyle.blurple, disabled=True)
                async def item2_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                    pass
            else:
                @nextcord.ui.button(label = 'Активировать 3x', style = nextcord.ButtonStyle.blurple, disabled=False)
                async def item2_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                    if owner.id == interaction.user.id:
                        if ec.execute(f"SELECT multiplier3x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] <= 0:
                            embed = nextcord.Embed(description = f'У вас нет 3х множителей', color=0x2b2d31)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                        else:
                            if ec.execute(f"SELECT multiplier FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == "None":
                                floot = (datetime.now() + timedelta(hours=1)).timestamp()
                                task.execute(f"INSERT INTO tasks VALUES ('multiplier','{floot}','{user.id}', '{interaction.guild.id}')")
                                ec.execute(f'UPDATE inventory SET multiplier3x_ = multiplier3x_ - 1  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                ec.execute(f'UPDATE balance SET multiplier = "3x"  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                ec_db.commit()
                                task_db.commit()

                                embed=nextcord.Embed(description=f"Ты успешно активировал(-a) **множитель 3x на час**", color=0x2b2d31)
                                embed.set_thumbnail(url=user.display_avatar)
                                await interaction.send(embed=embed, ephemeral=True)

                                embed=nextcord.Embed(title="Инвентарь пользователя - {}".format(user.name), color=0x2b2d31)
                                embed.set_thumbnail(url=user.display_avatar)
                                embed.add_field(name="Множители:", value="```5x на час - {} шт.\r3x на час - {} шт.\r2x на час - {} шт.```".format(
                                    ec.execute(f"SELECT multiplier5x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                                    ec.execute(f"SELECT multiplier3x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                                    ec.execute(f"SELECT multiplier2x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                                    inline=False)
                                await main.edit(embed=embed, view = multiplier())

                                if ec.execute(f"SELECT multiplier2x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                    self.item1_.disabled = True     
                                if ec.execute(f"SELECT multiplier3x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                    self.item2_.disabled = True    
                                if ec.execute(f"SELECT multiplier5x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                    self.item3_.disabled = True    
                                await interaction.response.edit_message(view=self) 
                            else:
                                embed=nextcord.Embed(description=f"У вас уже есть активный множитель", color=0x2b2d31)
                                embed.set_thumbnail(url=user.display_avatar)
                                await interaction.send(embed=embed, ephemeral=True) 
                    else:
                        embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                        await interaction.send(embed=embed, ephemeral= True)

            if ec.execute(f"SELECT multiplier5x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:       
                @nextcord.ui.button(label = 'Активировать 5x', style = nextcord.ButtonStyle.blurple, disabled=True)
                async def item3_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                    pass
            else:
                @nextcord.ui.button(label = 'Активировать 5x', style = nextcord.ButtonStyle.blurple, disabled=False)
                async def item3_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                    if owner.id == interaction.user.id:
                        if ec.execute(f"SELECT multiplier5x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] <= 0:
                            embed = nextcord.Embed(description = f'У вас нет 5х множителей', color=0x2b2d31)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                        else:
                            if ec.execute(f"SELECT multiplier FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == "None":
                                floot = (datetime.now() + timedelta(hours=1)).timestamp()
                                task.execute(f"INSERT INTO tasks VALUES ('multiplier','{floot}','{user.id}', '{interaction.guild.id}')")
                                ec.execute(f'UPDATE inventory SET multiplier5x_ = multiplier5x_ - 1  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                ec.execute(f'UPDATE balance SET multiplier = "5x"  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                ec_db.commit()
                                task_db.commit()

                                embed=nextcord.Embed(description=f"Ты успешно активировал(-a) **множитель 5x на час**", color=0x2b2d31)
                                embed.set_thumbnail(url=user.display_avatar)
                                await interaction.send(embed=embed, ephemeral=True)

                                embed=nextcord.Embed(title="Инвентарь пользователя - {}".format(user.name), color=0x2b2d31)
                                embed.set_thumbnail(url=user.display_avatar)
                                embed.add_field(name="Множители:", value="```5x на час - {} шт.\r3x на час - {} шт.\r2x на час - {} шт.```".format(
                                    ec.execute(f"SELECT multiplier5x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                                    ec.execute(f"SELECT multiplier3x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                                    ec.execute(f"SELECT multiplier2x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                                    inline=False)
                                await main.edit(embed=embed, view = multiplier())

                                if ec.execute(f"SELECT multiplier2x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                    self.item1_.disabled = True     
                                if ec.execute(f"SELECT multiplier3x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                    self.item2_.disabled = True    
                                if ec.execute(f"SELECT multiplier5x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == 0:
                                    self.item3_.disabled = True    
                                await interaction.response.edit_message(view=self) 
                            else:
                                embed=nextcord.Embed(description=f"У вас уже есть активный множитель", color=0x2b2d31)
                                embed.set_thumbnail(url=user.display_avatar)
                                await interaction.send(embed=embed, ephemeral=True)   
                    else:
                        embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                        await interaction.send(embed=embed, ephemeral= True)

        rolemode = None
        channelmode = None
        multipliermode = 'Отсутствует'
        ec.execute(f"SELECT id FROM role where id={user.id} and guild_id={interaction.guild.id}")
        if ec.fetchone() is None:
            rolemode = "Отсутствует"
        else:
            rolemode = "Присутствует"

        if ec.execute(f"SELECT multiplier FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] != "None":
            if ec.execute(f"SELECT multiplier FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == "2x":
                multipliermode = "2x истекает <t:{}:R>".format(math.trunc(task.execute(f"SELECT date FROM tasks WHERE id={user.id} and guild_id = {interaction.guild.id} and name = 'multiplier'").fetchone()[0]))
            elif ec.execute(f"SELECT multiplier FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == "3x":
                multipliermode = "3x истекает <t:{}:R>".format(math.trunc(task.execute(f"SELECT date FROM tasks WHERE id={user.id} and guild_id = {interaction.guild.id} and name = 'multiplier'").fetchone()[0]))
            elif ec.execute(f"SELECT multiplier FROM balance WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0] == "5x":
                multipliermode = "5x истекает <t:{}:R>".format(math.trunc(task.execute(f"SELECT date FROM tasks WHERE id={user.id} and guild_id = {interaction.guild.id} and name = 'multiplier'").fetchone()[0]))

        ec.execute(f"SELECT id FROM channel where id={user.id} and guild_id={interaction.guild.id}")
        if ec.fetchone() is None:
            channelmode = "Отсутствует"
        else:
            channelmode = "Присутствует"

        embed=nextcord.Embed(title="Инвентарь пользователя - {}".format(user.name), description=f"**Личная роль:** {rolemode}\r**Личный канал:** {channelmode}\r**Множители:** {multipliermode}", color=0x2b2d31)
        embed.set_thumbnail(url=user.display_avatar)
        embed.add_field(name="Предметы:", value="```Личная роль - {} шт.\rЛичный канал - {} шт.```".format(
            ec.execute(f"SELECT customrole_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
            ec.execute(f"SELECT customchannel_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
            inline=False)
        embed.add_field(name="Кейсы:", value="```Обычный кейс - {} шт.\rПремиум кейс - {} шт.\rОнлайн кейс - {} шт.\rЛюбовный кейс - {} шт.```".format(
            ec.execute(f"SELECT case_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
            ec.execute(f"SELECT casepremium_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
            ec.execute(f"SELECT caseonline_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
            ec.execute(f"SELECT casemarry_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), inline=False)
        embed.add_field(name="Множители:", value="```5x на час - {} шт.\r3x на час - {} шт.\r2x на час - {} шт.```".format(
            ec.execute(f"SELECT multiplier5x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
            ec.execute(f"SELECT multiplier3x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
            ec.execute(f"SELECT multiplier2x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
            inline=False)

        class category(nextcord.ui.Select):
            def __init__(self):
                selectOptions = [
                    nextcord.SelectOption(label='Кейсы'),
                    nextcord.SelectOption(label='Предметы'),
                    nextcord.SelectOption(label='Прочее'),
                ]
                super().__init__(placeholder='Выбери категорию', min_values=1, max_values=1, options=selectOptions)


            async def callback(self, interaction: nextcord.Interaction):
                if owner.id == interaction.user.id:

                    if self.values[0] == 'Кейсы':
                        embed=nextcord.Embed(title="Инвентарь пользователя - {}".format(user.name), color=0x2b2d31)
                        embed.set_thumbnail(url=user.display_avatar)
                        embed.add_field(name="Кейсы:", value="```Обычный кейс - {} шт.\rПремиум кейс - {} шт.\rОнлайн кейс - {} шт.\rЛюбовный кейс - {} шт.```".format(
                            ec.execute(f"SELECT case_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
                            ec.execute(f"SELECT casepremium_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
                            ec.execute(f"SELECT caseonline_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0],
                            ec.execute(f"SELECT casemarry_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), inline=False)
                        await main.edit(embed=embed, view = case())
                    elif self.values[0] == 'Предметы':
                        embed=nextcord.Embed(title="Инвентарь пользователя - {}".format(user.name), color=0x2b2d31)
                        embed.set_thumbnail(url=user.display_avatar)
                        embed.add_field(name="Предметы:", value="```Личная роль - {} шт.\rЛичный канал - {} шт.```".format(
                            ec.execute(f"SELECT customrole_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                            ec.execute(f"SELECT customchannel_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                            inline=False)
                        await main.edit(embed=embed, view = item())
                    else:
                        embed=nextcord.Embed(title="Инвентарь пользователя - {}".format(user.name), color=0x2b2d31)
                        embed.set_thumbnail(url=user.display_avatar)
                        embed.add_field(name="Множители:", value="```5x на час - {} шт.\r3x на час - {} шт.\r2x на час - {} шт.```".format(
                            ec.execute(f"SELECT multiplier5x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                            ec.execute(f"SELECT multiplier3x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0], 
                            ec.execute(f"SELECT multiplier2x_ FROM inventory WHERE id={user.id} and guild_id={interaction.guild.id} ").fetchone()[0]), 
                            inline=False)
                        await main.edit(embed=embed, view = multiplier_())
                else:
                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                    await interaction.send(embed=embed, ephemeral= True)

        class sort(nextcord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)
                self.add_item(category())
        if interaction.user.id == user.id:
            main = await interaction.send(embed=embed, view = sort())
        else:
            main = await interaction.send(embed=embed)

    @nextcord.slash_command(description="Меню управления личной комнатой", guild_ids = [int(settings["Guild_ID"])])
    async def voice_manager(self, interaction: nextcord.Interaction):  
        cost = int(settings['cost_channel'])
        backup = int(settings['percent_channel']) * 0.01 * cost
        owner = interaction.user
        bot = self.bot
        ec_db = sqlite3.connect('database/economy.db', timeout=10)
        ec = ec_db.cursor()   
        ec.execute(f"SELECT id FROM channel where id={interaction.user.id} and guild_id={interaction.guild.id}")
        if ec.fetchone() is None:
            embed = nextcord.Embed(description = f'У тебя нету своей личной комнаты', color=0x2b2d31)
            embed.set_thumbnail(url=interaction.user.display_avatar)       
            await interaction.send(embed=embed, ephemeral= True)           
        else:
            for channel1 in ec.execute(f"SELECT channel FROM channel where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                channel = interaction.guild.get_channel(channel1[0])
                for close in ec.execute(f"SELECT status FROM channel WHERE id = {interaction.user.id} and guild_id = {interaction.guild.id}"):
                    if 'close' == close[0]:
                        if channel is None:
                            ec.execute(f"DELETE FROM channel where id={interaction.user.id} and guild_id = {interaction.guild.id}")


                            embed = nextcord.Embed(description = f'У тебя нету своей личной роли', color=0x2b2d31)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)         
                        else:
                            delete = Button(label="! Удалить канал !", style=nextcord.ButtonStyle.red)
                            buy = Button(label=f"Оплатить [{cost} коинов]", style=nextcord.ButtonStyle.gray)
                            
                            
                            async def buy_callback(interaction: nextcord.Interaction):
                                
                                for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):

                                    if bal[0] < cost:
                                        embed=nextcord.Embed(description = "Тебе нужно **{}** монет для оплаты личной роли ^^".format(cost), color=0x2b2d31)
                                        await interaction.send(embed = embed,ephemeral=True)      
                                    else:   
                                        task.execute(f"DELETE FROM tasks where id={interaction.user.id} and guild_id = {interaction.guild.id} and name='channel'")
                                        task.execute(f"DELETE FROM tasks where id={interaction.user.id} and guild_id = {interaction.guild.id} and name='deletechannel'")
                                        task_db.commit()
                                        bloop = (datetime.now() + timedelta(days=30)).timestamp()


                                        task.execute(f"INSERT INTO tasks VALUES ('channel','{bloop}','{interaction.user.id}', '{interaction.guild.id}')")
                                        task_db.commit()

                                        ec.execute(f'UPDATE channel SET status = "open" where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                        ec.execute(f'UPDATE balance SET bal={bal[0] - cost}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                        ec_db.commit()
                                        embed=nextcord.Embed(description = "Ты успешно продлил личную комнату^^", color=0x2b2d31)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)
                                        await interaction.edit(embed = embed, view=None)   

                            async def delete_callback(interaction: nextcord.Interaction):
                                if owner.id == interaction.user.id:  
                                    ec_db = sqlite3.connect('database/economy.db', timeout=10)
                                    ec = ec_db.cursor() 
                                    class dress(nextcord.ui.View):
                                        def __init__(self):
                                            super().__init__(timeout=60)

                                        @nextcord.ui.button(label = 'Да', style = nextcord.ButtonStyle.red, disabled=False)
                                        async def yes(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):   
                                            if owner.id == interaction.user.id:  

                                                name = channel.name
                                                await channel.delete()
                                                for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                                    ec.execute(f"DELETE FROM channel where id={interaction.user.id} and guild_id = {interaction.guild.id}")
                                                    task.execute(f"DELETE FROM tasks where id={interaction.user.id} and guild_id = {interaction.guild.id} and name='deletechannel'")
                                                    task_db.commit()

                                                    embed=nextcord.Embed(description = f"Ты успешно удалил свою комнату: {name}.", color=0x2b2d31)
                                                    embed.set_thumbnail(url=interaction.user.display_avatar)
                                                    await interaction.edit(embed = embed, view=None) 
                                                ec_db.commit() 
                                            else:
                                                embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                await interaction.send(embed=embed, ephemeral= True)    

                                        @nextcord.ui.button(label = 'Нет', style = nextcord.ButtonStyle.grey, disabled=False)
                                        async def no(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):  
                                            if owner.id == interaction.user.id:  
                                                embed = nextcord.Embed(description = f'Действия для данной команды было отменено', color=0x2b2d31)
                                                embed.set_footer(text='Через 5 секунд, данное сообщение будет удалено')
                                                await interaction.edit(embed=embed, view = None)
                                                await asyncio.sleep(5)
                                                await interaction.message.delete()
                                            else:
                                                embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                await interaction.send(embed=embed, ephemeral= True)    

                                    embed = nextcord.Embed(description = f'Данное действие нельзя будет потом отменить. Ты уверен что ты хочешь продолжить?', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)
                                    await interaction.edit(embed=embed, view=dress())


                                else:
                                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)   
                                
                            delete.callback = delete_callback
                            buy.callback = buy_callback
                            view = View()
    
                            view.add_item(buy)
                            view.add_item(delete)


                            for row in task.execute(f"SELECT date FROM tasks WHERE id={interaction.user.id} and guild_id = {interaction.guild.id} and name = 'deletechannel'"):
                                embed=nextcord.Embed(title = 'Меню управления каналом', description=f'Твоя комната: {channel.mention} \r\rCрок действия твоего товара закончился.\n・<t:{math.trunc(row[0])}:R> роль будет удалена, если не будет внесена оплата.', color=0x2b2d31)
                                for bal in ec.execute(f"SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}"):
                                    embed.set_footer(text=f'Баланс: {bal[0]}')
                                embed.set_thumbnail(url=interaction.user.display_avatar)
                                
                                await interaction.send(embed = embed, view=view)    
                    else:




                        class reset(nextcord.ui.View):
                            def __init__(self):
                                super().__init__(timeout=60)

                    


                            @nextcord.ui.button(label = 'Переименовать', style = nextcord.ButtonStyle.grey, disabled=False)
                            async def rename(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                if owner.id == interaction.user.id:
                                    for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):

                        
                                        if bal[0] < 250:
                                            embed=nextcord.Embed(description = "Стоимость данной функции 250 монет", color=0x2b2d31)
                                            await interaction.send(embed = embed, ephemeral=True)      
                                        else:                        
                                        
                                            class rename(nextcord.ui.Modal):
                                                def __init__(self):
                                                    super().__init__('Cмена названия комнаты')

                                                    self.Name = nextcord.ui.TextInput(label = 'New Name', min_length=1, max_length=50, required=False, placeholder='Например: dota 2', style=nextcord.TextInputStyle.paragraph)
                                                    self.add_item(self.Name)

                                                async def callback(self, interaction: nextcord.Interaction) -> None:
                                                    name = self.Name.value
                                                
                                                    await channel.edit(name = name)
                                                    ec.execute(f'UPDATE balance SET bal={bal[0] - 250}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                                    ec_db.commit() 
                                                    embed = nextcord.Embed(description = f'Ты успешно переименовал свою комнату.\n\nНовое название: **{name}**', color=0x2b2d31)
                                                    embed.set_thumbnail(url=interaction.user.display_avatar)
                                                    await interaction.send(embed=embed, ephemeral= True)
                                                    
                                            await interaction.response.send_modal(rename())

                                else:
                                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)

                            @nextcord.ui.button(label = 'Выдать доступ', style = nextcord.ButtonStyle.grey, disabled=False)
                            async def give(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                if owner.id == interaction.user.id:
                                    for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):

                                    
                                        if bal[0] < 100:
                                            embed=nextcord.Embed(description = "Стоимость данной функции 100 монет", color=0x2b2d31)
                                            await interaction.send(embed = embed, ephemeral=True)      
                                        else:     
                                                        
                                            if owner.id == interaction.user.id:
                                                er=nextcord.Embed(description="Укажи **человека** или его **id** которому хочешь дать доступ в свою комнату^^", color=0x2b2d31)
                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                
                                                await interaction.edit(embed=er, view = None)

                                                try:
                                                    msg = await bot.wait_for('message', check=lambda m: m.author.id == interaction.user.id, timeout = 30)
                                                    s = msg.content

                                                    member = re.sub("[<@!>]","",s)
                                                    try:
                                                        user =   interaction.guild.get_member(int(member))
                                                        await channel.set_permissions(user, connect = True)
                                                        await msg.delete()
                                                        ec.execute(f'UPDATE balance SET bal={bal[0] - 100}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                                        ec_db.commit() 
                                                        embed = nextcord.Embed(description = f'Теперь {user.mention}, может подключаться к твоей комнате^^', color=0x2b2d31)
                                                        embed.set_thumbnail(url=interaction.user.display_avatar)
                                                        await interaction.edit(embed=embed, view = None)      

                                                    except:
                                                        await msg.delete()
                                                        embed = nextcord.Embed(description = f'Ошибка в конвертирование str в member. Скорее всего ты пытаешься **str(**{msg.content}**)** конвертировать в **member(**{msg.content}**)**.\n\n"Входные данные не является id или mention user | Ты не указал id или mention user"', color=0x2b2d31)
                                                        embed.set_footer(text='Через 5 секунды, ты будешь отправлен в главное меню')
                                                        await interaction.edit(embed=embed, view = None)
                                                        await asyncio.sleep(5)
                                                        for role in ec.execute(f"SELECT channel FROM channel where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                            embed1=nextcord.Embed(title = 'Меню управления комнатой', description='Твоя комната: <#{}>'.format(role[0]), color=0x2b2d31)
                                                            embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                            embed1.set_footer(text='/voice_manager - меню управления личной комнатой')
                                                            await interaction.send(embed = embed1, view=reset()) 
                                                            
                                                except asyncio.exceptions.TimeoutError:
                                                    embed = nextcord.Embed(description = f'Время на выполнения данной команды вышло', color=0x2b2d31)
                                                    embed.set_footer(text='Через 5 секунды, ты будешь отправлен в главное меню')
                                                    await interaction.edit(embed=embed, view = None)
                                                    await asyncio.sleep(5)
                                                    for role in ec.execute(f"SELECT channel FROM channel where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                        embed1=nextcord.Embed(title = 'Меню управления комнатой', description='Твоя комната: <#{}>'.format(role[0]), color=0x2b2d31)
                                                        embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                        embed1.set_footer(text='/voice_manager - меню управления личной комнатой')
                                                        await interaction.send(embed = embed1, view=reset()) 
                                else:
                                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)  

                            @nextcord.ui.button(label = 'Забрать доступ', style = nextcord.ButtonStyle.grey, disabled=False)
                            async def remove(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                if owner.id == interaction.user.id:
                                    for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):


                                        if bal[0] < 100:
                                            embed=nextcord.Embed(description = "Стоимость данной функции 100 монет", color=0x2b2d31)
                                            await interaction.send(embed = embed, ephemeral=True)      
                                        else:                            
                            
                        
                                                er=nextcord.Embed(description="Укажи **человека** или его **id** у которого хочешь забрать доступ в свою комнату^^", color=0x2b2d31)
                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                
                                                await interaction.edit(embed=er, view = None)

                                                try:
                                                    msg = await bot.wait_for('message', check=lambda m: m.author.id == interaction.user.id, timeout = 30)
                                                    s = msg.content

                                                    member = re.sub("[<@!>]","",s)
                                                    try:
                                                        user =   interaction.guild.get_member(int(member))
                                                        await channel.set_permissions(user, connect = None)
                                                        await msg.delete()
                                                        ec.execute(f'UPDATE balance SET bal={bal[0] - 100}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                                        ec_db.commit() 
                                                        embed = nextcord.Embed(description = f'Теперь {user.mention}, не сможет подключаться к твоей комнате^^', color=0x2b2d31)
                                                        embed.set_thumbnail(url=interaction.user.display_avatar)
                                                        await interaction.edit(embed=embed, view = None)      

                                                    except:
                                                        await msg.delete()
                                                        embed = nextcord.Embed(description = f'Ошибка в конвертирование str в member. Скорее всего ты пытаешься **str(**{msg.content}**)** конвертировать в **member(**{msg.content}**)**.\n\n"Входные данные не является id или mention user | Ты не указал id или mention user"', color=0x2b2d31)
                                                        embed.set_footer(text='Через 5 секунды, ты будешь отправлен в главное меню')
                                                        await interaction.edit(embed=embed, view = None)
                                                        await asyncio.sleep(5)
                                                        for role in ec.execute(f"SELECT channel FROM channel where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                            embed1=nextcord.Embed(title = 'Меню управления комнатой', description='Твоя комната: <#{}>'.format(role[0]), color=0x2b2d31)
                                                            embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                            embed1.set_footer(text='/voice_manager - меню управления личной комнатой')
                                                            await interaction.send(embed = embed1, view=reset()) 
                                                            
                                                except asyncio.exceptions.TimeoutError:
                                                    embed = nextcord.Embed(description = f'Время на выполнения данной команды вышло', color=0x2b2d31)
                                                    embed.set_footer(text='Через 5 секунды, ты будешь отправлен в главное меню')
                                                    await interaction.edit(embed=embed, view = None)
                                                    await asyncio.sleep(5)
                                                    for role in ec.execute(f"SELECT channel FROM channel where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                        embed1=nextcord.Embed(title = 'Меню управления комнатой', description='Твоя комната: <#{}>'.format(role[0]), color=0x2b2d31)
                                                        embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                        embed1.set_footer(text='/voice_manager - меню управления личной комнатой')
                                                        await interaction.send(embed = embed1, view=reset()) 
                                else:
                                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)  

                            @nextcord.ui.button(label = 'Выдать доступ (роль)', style = nextcord.ButtonStyle.grey, disabled=False)
                            async def giverole(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                if owner.id == interaction.user.id:
                                    for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):

                                    
                                        if bal[0] < 400:
                                            embed=nextcord.Embed(description = "Стоимость данной функции 400 монет", color=0x2b2d31)
                                            await interaction.send(embed = embed, ephemeral=True)      
                                        else:     
                                                        
                                            if owner.id == interaction.user.id:
                                                er=nextcord.Embed(description="Укажи **роль** или **id роли**, для того что бы выдать доступ^^", color=0x2b2d31)
                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                
                                                await interaction.edit(embed=er, view = None)

                                                try:
                                                    msg = await bot.wait_for('message', check=lambda m: m.author.id == interaction.user.id, timeout = 30)
                                                    s = msg.content

                                                    member = re.sub("[<@&>]","",s)
                                                    try:
                                                        user =   interaction.guild.get_role(int(member))
                                                        await channel.set_permissions(user, connect = True)
                                                        await msg.delete()
                                                        ec.execute(f'UPDATE balance SET bal={bal[0] - 400}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                                        ec_db.commit() 
                                                        embed = nextcord.Embed(description = f'Теперь люди с ролью {user.mention}, смогут подключаться к твоей комнате^^', color=0x2b2d31)
                                                        embed.set_thumbnail(url=interaction.user.display_avatar)
                                                        await interaction.edit(embed=embed, view = None)      

                                                    except:
                                                        await msg.delete()
                                                        embed = nextcord.Embed(description = f'Ошибка в конвертирование str в member. Скорее всего ты пытаешься **str(**{msg.content}**)** конвертировать в **member(**{msg.content}**)**.\n\n"Входные данные не является id или mention user | Ты не указал id или mention user"', color=0x2b2d31)
                                                        embed.set_footer(text='Через 5 секунды, ты будешь отправлен в главное меню')
                                                        await interaction.edit(embed=embed, view = None)
                                                        await asyncio.sleep(5)
                                                        for role in ec.execute(f"SELECT channel FROM channel where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                            embed1=nextcord.Embed(title = 'Меню управления комнатой', description='Твоя комната: <#{}>'.format(role[0]), color=0x2b2d31)
                                                            embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                            embed1.set_footer(text='/voice_manager - меню управления личной комнатой')
                                                            await interaction.send(embed = embed1, view=reset()) 
                                                            
                                                except asyncio.exceptions.TimeoutError:
                                                    embed = nextcord.Embed(description = f'Время на выполнения данной команды вышло', color=0x2b2d31)
                                                    embed.set_footer(text='Через 5 секунды, ты будешь отправлен в главное меню')
                                                    await interaction.edit(embed=embed, view = None)
                                                    await asyncio.sleep(5)
                                                    for role in ec.execute(f"SELECT channel FROM channel where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                        embed1=nextcord.Embed(title = 'Меню управления комнатой', description='Твоя комната: <#{}>'.format(role[0]), color=0x2b2d31)
                                                        embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                        embed1.set_footer(text='/voice_manager - меню управления личной комнатой')
                                                        await interaction.send(embed = embed1, view=reset()) 
                                else:
                                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)  

                            @nextcord.ui.button(label = 'Забрать доступ (роль)', style = nextcord.ButtonStyle.grey, disabled=False)
                            async def removerole(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                if owner.id == interaction.user.id:
                                    for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):


                                        if bal[0] < 400:
                                            embed=nextcord.Embed(description = "Стоимость данной функции 400 монет", color=0x2b2d31)
                                            await interaction.send(embed = embed, ephemeral=True)      
                                        else:                            
                            
                        
                                                er=nextcord.Embed(description="Укажи **роль** или **id роли**, для того что бы забрать доступ^^", color=0x2b2d31)
                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                
                                                await interaction.edit(embed=er, view = None)

                                                try:
                                                    msg = await bot.wait_for('message', check=lambda m: m.author.id == interaction.user.id, timeout = 30)
                                                    s = msg.content

                                                    member = re.sub("[<@&>]","",s)
                                                    try:
                                                        user =   interaction.guild.get_role(int(member))
                                                        await channel.set_permissions(user, connect = None)
                                                        await msg.delete()
                                                        ec.execute(f'UPDATE balance SET bal={bal[0] - 400}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                                        ec_db.commit() 
                                                        embed = nextcord.Embed(description = f'Теперь люди с ролью {user.mention}, не смогут подключаться к твоей комнате^^', color=0x2b2d31)
                                                        embed.set_thumbnail(url=interaction.user.display_avatar)
                                                        await interaction.edit(embed=embed, view = None)      

                                                    except:
                                                        await msg.delete()
                                                        embed = nextcord.Embed(description = f'Ошибка в конвертирование str в member. Скорее всего ты пытаешься **str(**{msg.content}**)** конвертировать в **member(**{msg.content}**)**.\n\n"Входные данные не является id или mention user | Ты не указал id или mention user"', color=0x2b2d31)
                                                        embed.set_footer(text='Через 5 секунды, ты будешь отправлен в главное меню')
                                                        await interaction.edit(embed=embed, view = None)
                                                        await asyncio.sleep(5)
                                                        for role in ec.execute(f"SELECT channel FROM channel where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                            embed1=nextcord.Embed(title = 'Меню управления комнатой', description='Твоя комната: <#{}>'.format(role[0]), color=0x2b2d31)
                                                            embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                            embed1.set_footer(text='/voice_manager - меню управления личной комнатой')
                                                            await interaction.send(embed = embed1, view=reset()) 
                                                            
                                                except asyncio.exceptions.TimeoutError:
                                                    embed = nextcord.Embed(description = f'Время на выполнения данной команды вышло', color=0x2b2d31)
                                                    embed.set_footer(text='Через 5 секунды, ты будешь отправлен в главное меню')
                                                    await interaction.edit(embed=embed, view = None)
                                                    await asyncio.sleep(5)
                                                    for role in ec.execute(f"SELECT channel FROM channel where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                        embed1=nextcord.Embed(title = 'Меню управления комнатой', description='Твоя комната: <#{}>'.format(role[0]), color=0x2b2d31)
                                                        embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                        embed1.set_footer(text='/voice_manager - меню управления личной комнатой')
                                                        await interaction.send(embed = embed1, view=reset()) 
                                else:
                                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)  

                            @nextcord.ui.button(label = 'Установить лимит', style = nextcord.ButtonStyle.grey, disabled=False)
                            async def limit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                if owner.id == interaction.user.id:
                                    for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):


                                        if bal[0] < 400:
                                            embed=nextcord.Embed(description = "Стоимость данной функции 400 монет", color=0x2b2d31)
                                            await interaction.send(embed = embed, ephemeral=True)      
                                        else:                            
                            
                        
                                                er=nextcord.Embed(description="Укажи новый лимит^^", color=0x2b2d31)
                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                
                                                await interaction.edit(embed=er, view = None)

                                                try:
                                                    msg = await bot.wait_for('message', check=lambda m: m.author.id == interaction.user.id, timeout = 30)
                                                    s = msg.content

                                                    count = re.sub("[<@&>]","",s)
                                                    try:
                                                        await channel.edit(user_limit = int(count))
                                                        await msg.delete()
                                                        ec.execute(f'UPDATE balance SET bal={bal[0] - 400}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                                        ec_db.commit() 
                                                        embed = nextcord.Embed(description = f'Лимит комнаты был изменен: `{count}`^^', color=0x2b2d31)
                                                        embed.set_thumbnail(url=interaction.user.display_avatar)
                                                        await interaction.edit(embed=embed, view = None)      

                                                    except:
                                                        await msg.delete()
                                                        embed = nextcord.Embed(description = f'Ошибка в конвертирование str в int. Скорее всего ты пытаешься **str(**{msg.content}**)** конвертировать в **int(**{msg.content}**)**.\n\n"Входные данные не является числом | Ты указал не число, а что то другое"', color=0x2b2d31)
                                                        embed.set_footer(text='Через 5 секунды, ты будешь отправлен в главное меню')
                                                        await interaction.edit(embed=embed, view = None)
                                                        await asyncio.sleep(5)
                                                        for role in ec.execute(f"SELECT channel FROM channel where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                            embed1=nextcord.Embed(title = 'Меню управления комнатой', description='Твоя комната: <#{}>'.format(role[0]), color=0x2b2d31)
                                                            embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                            embed1.set_footer(text='/voice_manager - меню управления личной комнатой')
                                                            await interaction.send(embed = embed1, view=reset()) 
                                                            
                                                except asyncio.exceptions.TimeoutError:
                                                    embed = nextcord.Embed(description = f'Время на выполнения данной команды вышло', color=0x2b2d31)
                                                    embed.set_footer(text='Через 5 секунды, ты будешь отправлен в главное меню')
                                                    await interaction.edit(embed=embed, view = None)
                                                    await asyncio.sleep(5)
                                                    for role in ec.execute(f"SELECT channel FROM channel where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                        embed1=nextcord.Embed(title = 'Меню управления комнатой', description='Твоя комната: <#{}>'.format(role[0]), color=0x2b2d31)
                                                        embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                        embed1.set_footer(text='/voice_manager - меню управления личной комнатой')
                                                        await interaction.send(embed = embed1, view=reset()) 
                                else:
                                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)                          

                            @nextcord.ui.button(label = '! Удалить !', style = nextcord.ButtonStyle.red, disabled=False)
                            async def deletchannel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                if owner.id == interaction.user.id:  
                                    ec_db = sqlite3.connect('database/economy.db', timeout=10)
                                    ec = ec_db.cursor() 
                                    class dress(nextcord.ui.View):
                                        def __init__(self):
                                            super().__init__(timeout=60)

                                        @nextcord.ui.button(label = 'Да', style = nextcord.ButtonStyle.red, disabled=False)
                                        async def yes(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):   
                                            if owner.id == interaction.user.id:  

                                                name = r.name
                                                await r.delete()
                                                for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                                    ec.execute(f'UPDATE balance SET bal={bal[0] + int(backup)}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                                    ec.execute(f"DELETE FROM channel where id={interaction.user.id} and guild_id = {interaction.guild.id}")
                                                    task.execute(f"DELETE FROM tasks where id={interaction.user.id} and guild_id = {interaction.guild.id} and name='channel'")
                                                    task_db.commit()
                                                    embed=nextcord.Embed(description = f"Ты успешно удалил свою комнату: {name}.", color=0x2b2d31)
                                                    embed.set_thumbnail(url=interaction.user.display_avatar)
                                                    await interaction.edit(embed = embed, view=None) 
                                                ec_db.commit() 
                                            else:
                                                embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                await interaction.send(embed=embed, ephemeral= True)    

                                        @nextcord.ui.button(label = 'Нет', style = nextcord.ButtonStyle.grey, disabled=False)
                                        async def no(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):  
                                            if owner.id == interaction.user.id:  
                                                embed = nextcord.Embed(description = f'Действия для данной команды было отменено', color=0x2b2d31)
                                                embed.set_footer(text='Через 5 секунды, ты будешь отправлен в главное меню')
                                                await interaction.edit(embed=embed, view = None)
                                                await asyncio.sleep(5)
                                                for role in ec.execute(f"SELECT channel FROM channel where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                                    embed1=nextcord.Embed(title = 'Меню управления комнатой', description='Твоя комната: <#{}>'.format(role[0]), color=0x2b2d31)
                                                    embed1.set_thumbnail(url=interaction.user.display_avatar)
                                                    embed1.set_footer(text='/voice_manager - меню управления личной комнатой')
                                                    await interaction.send(embed = embed1, view=reset()) 
                                            else:
                                                embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                await interaction.send(embed=embed, ephemeral= True)    

                                    embed = nextcord.Embed(description = f'Данное действие нельзя будет потом отменить. Ты уверен что ты хочешь продолжить?', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)
                                    embed.set_footer(text='После продажи данного товара, ты получишь 30% от стоимости товара')
                                    await interaction.edit(embed=embed, view=dress())


                                else:
                                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)                        

                            @nextcord.ui.button(label = 'Назад', style = nextcord.ButtonStyle.red, disabled=False)
                            async def delete(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                if owner.id == interaction.user.id:
                                    await interaction.message.delete()
                                    embed = nextcord.Embed(description = f'Сообщение успешно было удалено.', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)
                                else:
                                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)


                        for role in ec.execute(f"SELECT channel FROM channel where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                            r = interaction.guild.get_channel(role[0])
                            if r is None:
                                class refund(nextcord.ui.View):
                                    def __init__(self):
                                        super().__init__(timeout=60)

                                    @nextcord.ui.button(label = 'Вернуть денежные средства', style = nextcord.ButtonStyle.red, disabled=False)
                                    async def restore(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                                        if owner.id == interaction.user.id:  
                                            
                                            for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                                ec.execute(f"DELETE FROM channel where id={interaction.user.id} and guild_id = {interaction.guild.id}")
                                                task.execute(f"DELETE FROM tasks where id={interaction.user.id} and guild_id = {interaction.guild.id} and name='channel'")
                                                task_db.commit()
                                                ec_db.commit() 
                                                embed=nextcord.Embed(description = f"Ты успешно **оформил** **возврат денежных средств** за **удаленный** товар\nВ течение **минуты** деньги поступят на твой счет", color=0x2b2d31)
                                                embed.set_thumbnail(url=interaction.user.display_avatar)
                                                await interaction.edit(embed = embed, view=None) 
                                                time = random.randint(10, 60)
                                                print(time)
                                                await asyncio.sleep(time)
                                                ec.execute(f'UPDATE balance SET bal={bal[0] + int(backup)}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                                emb=nextcord.Embed(title=f"**Поступление монет**", description = f"Комиссия с перевода: Отсутсвтует", color=0x2b2d31)
                                                emb.add_field(name = 'Получатель:', value=interaction.user.mention, inline=False)
                                                emb.add_field(name = 'Отправитель:', value=interaction.guild.name, inline=False)
                                                emb.add_field(name = 'Комментарий:', value='**Возврат** денежных **средств** за товар: `личная комната`', inline=False)
                                                emb.add_field(name = 'Сумма', value=f'{backup}', inline=False)
                                                await interaction.user.send(embed=emb)
                                            ec_db.commit() 
                                        else:
                                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                                            await interaction.send(embed=embed, ephemeral= True)

                                embed=nextcord.Embed(title = 'Меню управления комнатой', description='~~Твоя комната: None~~\n\nТвоя комната **не была найдена**, в списке **каналов**. Для вас доступна **функция** возврата **денежных средств.**', color=0x2b2d31)
                                for bal in ec.execute(f"SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}"):
                                    embed.set_footer(text=f'Баланс: {bal[0]}')
                                embed.set_thumbnail(url=interaction.user.display_avatar)
                                
                                await interaction.send(embed = embed, view=refund())



                            else:
                                for row in task.execute(f"SELECT date FROM tasks WHERE id={interaction.user.id} and guild_id = {interaction.guild.id} and name = 'channel'"):
                                    

                                    

                                    for channel1 in ec.execute(f"SELECT channel FROM channel where id={interaction.user.id} and guild_id = {interaction.guild.id}"):
                                        channel = interaction.guild.get_channel(channel1[0])
                                        embed=nextcord.Embed(title = 'Меню управления комнатой', description='Твоя комната: {}\r\rСрок действия предмета истекает <t:{}:R>'.format(channel.mention, math.trunc(row[0])), color=0x2b2d31)
                                        for bal in ec.execute(f"SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}"):
                                            embed.set_footer(text=f'Баланс: {bal[0]}')
                                        embed.set_thumbnail(url=interaction.user.display_avatar)
                                        
                                        await interaction.send(embed = embed, view=reset())
  
   


    @nextcord.slash_command(description="Подросить монетку", guild_ids = [int(settings["Guild_ID"])])
    async def coinflip(self, interaction: nextcord.Interaction, amout : int, 
    var : str = nextcord.SlashOption(
        name="var",
        choices={"Орёл": 'h', "Решка": 't'},
    ),):
        """・`bf <money> <h/t>`\n・Игра орёл/решка"""
        ec_db = sqlite3.connect('database/economy.db', timeout=10)
        ec = ec_db.cursor()
        txt = random.choice(['h' , 't'])
        for em in ec.execute(f'SELECT currency FROM settings where guild_id={interaction.guild.id}'):
            t1 = self.bot.get_emoji(em[0]) 
    
            if 0 > amout:
                embed=nextcord.Embed( description = "Незя ставить ставку ниже нолика", color=0x2b2d31)
                embed.set_thumbnail(url=interaction.user.display_avatar)
                await interaction.send(embed = embed, ephemeral=True)     
            else:

                for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                    if bal[0] < amout:
                        embed=nextcord.Embed( description = "Не хватает денюшек", color=0x2b2d31)
                        embed.set_thumbnail(url=interaction.user.display_avatar)
                        await interaction.send(embed = embed, ephemeral=True)      
                    else:                   
                        if var == 'h' or var == 't':        
                            if txt == var:
                                if txt == 'h':
                                    for row in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                        embed = nextcord.Embed(color=0x2b2d31)
                                        embed.set_image(url = 'https://media.discordapp.net/attachments/1085202500052865078/1085254091883675778/ZGrjQZw.gif')
                                        orel12 = await interaction.send(embed=embed)
                                        
                                        await asyncio.sleep(3,5)

                                        embed1 = nextcord.Embed(description = f'Вы подкинули монетку и вам выпал `орёл`. Вы выиграли - `{amout}` {t1}', color=0x2b2d31)
                                        embed1.set_thumbnail(url=interaction.user.display_avatar)
                                        await orel12.edit(embed=embed1)
                                        ec.execute(f'UPDATE balance SET bal={int(amout) + row[0]}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                if txt == 't':                                
                                    for row in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                        embed = nextcord.Embed(color=0x2b2d31)
                                        embed.set_image(url = 'https://media.discordapp.net/attachments/1085202500052865078/1085254091455868928/eZbhjUw.gif')
                                        orel13 = await interaction.send(embed=embed)
                                        
                                        await asyncio.sleep(3,5)

                                        embed1 = nextcord.Embed(description = f'Вы подкинули монетку и вам выпал `решка`. Вы выиграли - `{amout}` {t1}', color=0x2b2d31)
                                        embed1.set_thumbnail(url=interaction.user.display_avatar)
                                        await orel13.edit(embed=embed1)
                                        ec.execute(f'UPDATE balance SET bal={int(amout) + row[0]}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                            else:
                                    if txt == 'h':
                                        for row in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                            embed = nextcord.Embed(color=0x2b2d31)
                                            embed.set_image(url = 'https://media.discordapp.net/attachments/1085202500052865078/1085254091883675778/ZGrjQZw.gif')
                                            orel14 = await interaction.send(embed=embed)
                                            
                                            await asyncio.sleep(3,5)

                                            embed1 = nextcord.Embed(description = f'Вы подкинули монетку и вам выпал `орёл`. Вы проиграли - `{amout}` {t1}', color=0x2b2d31)
                                            embed1.set_thumbnail(url=interaction.user.display_avatar)
                                            await orel14.edit(embed=embed1)
                                            ec.execute(f'UPDATE balance SET bal={row[0] - int(amout)}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                    elif txt == 't':
                                        for row in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                            embed = nextcord.Embed(color=0x2b2d31)
                                            embed.set_image(url = 'https://media.discordapp.net/attachments/1085202500052865078/1085254091455868928/eZbhjUw.gif')
                                            orel15 = await interaction.send(embed=embed)
                                            
                                            await asyncio.sleep(3,5)

                                            embed1 = nextcord.Embed(description = f'Вы подкинули монетку и вам выпала `решка`. Вы проиграли - `{amout}` {t1}', color=0x2b2d31)
                                            embed1.set_thumbnail(url=interaction.user.display_avatar)
                                            await orel15.edit(embed=embed1)
                                            ec.execute(f'UPDATE balance SET bal={row[0] - int(amout)}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
        
                        else:
                            embed=nextcord.Embed( description = "Ну ты и дурак, я же тебе говрила что нужна указывать h или t", color=0x2b2d31)
                            embed.set_thumbnail(url=interaction.user.display_avatar)
                            await interaction.send(embed = embed, ephemeral=True) 
        ec_db.commit()
 
    @nextcord.slash_command(description="Камень/Ножницы/Бумага", guild_ids = [int(settings["Guild_ID"])])
    async def rps(self, interaction: nextcord.Interaction, amout : int, 
    var : str = nextcord.SlashOption(
        name="var",
        choices={
        "Камень": 'к', 
        "Ножницы": 'н',
        "Бумага": 'б'        
        },
    ),):
        ec_db = sqlite3.connect('database/economy.db', timeout=10)
        ec = ec_db.cursor()
        txt = random.choice(['к' , 'н', 'б'])
        for em in ec.execute(f'SELECT currency FROM settings where guild_id={interaction.guild.id}'):
            t1 = self.bot.get_emoji(em[0]) 
    
            if 0 > amout:
                embed=nextcord.Embed(description = "Незя ставить ставку ниже нолика", color=0x2b2d31)
                embed.set_thumbnail(url=interaction.user.display_avatar)
                await interaction.send(embed = embed, ephemeral=True)     
            else:

                for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                    if bal[0] < amout:
                        embed=nextcord.Embed(description = "Не хватает денюшек", color=0x2b2d31)
                        embed.set_thumbnail(url=interaction.user.display_avatar)
                        await interaction.send(embed = embed, ephemeral=True)      
                    else:                   
                        if var == 'к':
                            if txt == 'к':
                                embed = nextcord.Embed(title='Камень-Ножницы-Бумага', description = f'Вы выбрали `камень`, а ваш оппонент выбрал `камень`, у вас ничья!', color=0x2b2d31)
                                embed.set_image(url='https://media.discordapp.net/attachments/1085202500052865078/1085228335027736677/1.png?width=1402&height=701')
                                await interaction.send(embed=embed)         
                            elif txt == 'н':
                                    for row in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                        ec.execute(f'UPDATE balance SET bal={int(amout) + row[0]}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                        embed = nextcord.Embed(title='Камень-Ножницы-Бумага', description = f'Вы выбрали `камень`, а ваш оппонент выбрал `ножницы`, вы выиграли {amout} {t1}!', color=0x2b2d31)
                                        embed.set_image(url='https://media.discordapp.net/attachments/1085202500052865078/1085228336088887356/4.png?width=1402&height=701')
                                        await interaction.send(embed=embed)                              
                            elif txt == 'б':
                                for row in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                    ec.execute(f'UPDATE balance SET bal={row[0] - amout}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                    embed = nextcord.Embed(title='Камень-Ножницы-Бумага', description = f'Вы выбрали `камень`, а ваш оппонент выбрал `бумагу`, увы, но вы проиграли {amout} {t1}!', color=0x2b2d31)
                                    embed.set_image(url='https://media.discordapp.net/attachments/1085202500052865078/1085228336357326962/5.png?width=1402&height=701')
                                    await interaction.send(embed=embed)
                        elif var == 'б':
                            if txt == 'б':
                                embed = nextcord.Embed(title='Камень-Ножницы-Бумага', description = f'Вы выбрали `бумагу`, а ваш оппонент выбрал `бумагу`, у вас ничья!', color=0x2b2d31)
                                embed.set_image(url='https://media.discordapp.net/attachments/1085202500052865078/1085228335723986944/3.png?width=1402&height=701')
                                await interaction.send(embed=embed)         
                            elif txt == 'к':
                                    for row in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                        ec.execute(f'UPDATE balance SET bal={int(amout) + row[0]}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                        embed = nextcord.Embed(title='Камень-Ножницы-Бумага', description = f'Вы выбрали `бумагу`, а ваш оппонент выбрал `камень`, вы выиграли {amout} {t1}!', color=0x2b2d31)
                                        embed.set_image(url='https://media.discordapp.net/attachments/1085202500052865078/1085228337481400470/8.png?width=1402&height=701')
                                        await interaction.send(embed=embed)                              
                            elif txt == 'н':
                                for row in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                    ec.execute(f'UPDATE balance SET bal={row[0] - amout}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                    embed = nextcord.Embed(title='Камень-Ножницы-Бумага', description = f'Вы выбрали `бумагу`, а ваш оппонент выбрал `ножницы`, увы, но вы проиграли {amout} {t1}!', color=0x2b2d31)
                                    embed.set_image(url='https://media.discordapp.net/attachments/1085202500052865078/1085228334725738567/9.png?width=1402&height=701')
                                    await interaction.send(embed=embed)
                        elif var == 'н':
                            if txt == 'н':
                                embed = nextcord.Embed(title='Камень-Ножницы-Бумага', description = f'Вы выбрали `ножницы`, а ваш оппонент выбрал `ножницы`, у вас ничья!', color=0x2b2d31)
                                embed.set_image(url='https://media.discordapp.net/attachments/1085202500052865078/1085228335329718312/2.png?width=1402&height=701')
                                await interaction.send(embed=embed)         
                            elif txt == 'б':
                                    for row in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                        ec.execute(f'UPDATE balance SET bal={int(amout) + row[0]}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                        embed = nextcord.Embed(title='Камень-Ножницы-Бумага', description = f'Вы выбрали `ножницы`, а ваш оппонент выбрал `бумагу`, вы выиграли {amout} {t1}!', color=0x2b2d31)
                                        embed.set_image(url='https://media.discordapp.net/attachments/1085202500052865078/1085228337078743050/7.png?width=1402&height=701')
                                        await interaction.send(embed=embed)                              
                            elif txt == 'к':
                                for row in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                    ec.execute(f'UPDATE balance SET bal={row[0] - amout}  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                    embed = nextcord.Embed(title='Камень-Ножницы-Бумага', description = f'Вы выбрали `ножницы`, а ваш оппонент выбрал `ножницы`, увы, но вы проиграли {amout} {t1}!', color=0x2b2d31)
                                    embed.set_image(url='https://media.discordapp.net/attachments/1085202500052865078/1085228336688681041/6.png?width=1402&height=701')
                                    await interaction.send(embed=embed)
                              


        ec_db.commit()

    @nextcord.slash_command(description="Передать деньги пользователю", guild_ids = [int(settings["Guild_ID"])])
    async def transfer(self, interaction: nextcord.Interaction, money:int , member: nextcord.Member , *, txt = None):
        """・`transfer <money> <member> <comment (optional)>`\n・Перевод денежных средств пользователю"""
        ec_db = sqlite3.connect('database/economy.db', timeout=10)
        ec = ec_db.cursor()
        for em in ec.execute(f'SELECT currency FROM settings where guild_id={interaction.guild.id}'):
            t1 = self.bot.get_emoji(em[0]) 
            for com in ec.execute(f'SELECT com, com_info FROM settings where guild_id={interaction.guild.id}'):
                if 0 > money:
                    embed=nextcord.Embed(description = "Незя передать cумму которая ниже нолика(", color=0x2b2d31)
                    
                    await interaction.send(embed = embed)   
                else:  
                    if 20 > money:
                        embed=nextcord.Embed(description = f"Минимальный перевод от 20 {t1}", color=0x2b2d31)
                        
                        await interaction.send(embed = embed)   
                    else:    
                        if member.id == interaction.user.id:
                            embed=nextcord.Embed(description = "Ты не можешь перевести деньги сам себе(", color=0x2b2d31)
                            
                            await interaction.send(embed = embed)
                        else:
                            for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                if bal[0] < money:
                                    embed=nextcord.Embed(description = "Не хватает денюшек", color=0x2b2d31)
                                    
                                    await interaction.send(embed = embed)      
                                else:       
                                    if txt is None:
                                        if com[0] < 10:
                                            mon = int(money)*com[0]
                                            for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                                ec.execute(f'UPDATE balance SET bal={bal[0] - int(money)} where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                            for bal1 in ec.execute(f'SELECT bal FROM balance where id={member.id} and guild_id={interaction.guild.id}'):
                                                ec.execute(f'UPDATE balance SET bal={bal1[0] + round(money - mon)} where id={member.id} and guild_id={interaction.guild.id}')
                                            embed=nextcord.Embed(title=f"**Перевод монет**", description = f"Комиссия с перевода: {com[1]}%", color=0x2b2d31)
                                            embed.add_field(name = 'Получатель:', value=member.mention, inline=False)
                                            embed.add_field(name = 'Отправитель:', value=interaction.user.mention, inline=False)
                                            embed.add_field(name = 'Сумма с комиссией:', value=f'{round(int(money) - mon)} {t1}', inline=False)
                                            embed.add_field(name = 'Сумма без комиссии:', value=f'{money} {t1}', inline=False)
                                            
                                            await interaction.send(embed = embed)   

                                            embed1=nextcord.Embed(title=f"**Поступление монет**", description = f"Комиссия с перевода: {com[1]}%", color=0x2b2d31)
                                            embed1.add_field(name = 'Получатель:', value=member.mention, inline=False)
                                            embed1.add_field(name = 'Отправитель:', value=interaction.user.mention, inline=False)
                                            embed1.add_field(name = 'Сумма с комиссией:', value=f'{round(int(money) - mon)} {t1}', inline=False)
                                            embed1.add_field(name = 'Сумма без комиссии:', value=f'{money} {t1}', inline=False)
                                            
                                            await member.send(embed = embed1)   
                                        else:
                                            mon = int(money)*com[0]
                                            for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                                ec.execute(f'UPDATE balance SET bal={bal[0] - int(money)} where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                            for bal1 in ec.execute(f'SELECT bal FROM balance where id={member.id} and guild_id={interaction.guild.id}'):
                                                ec.execute(f'UPDATE balance SET bal={bal1[0] + round(money - mon)} where id={member.id} and guild_id={interaction.guild.id}')
                                            embed=nextcord.Embed(title=f"**Перевод монет**", description = f"Комиссия с перевода: {com[1]}%", color=0x2b2d31)
                                            embed.add_field(name = 'Получатель:', value=member.mention, inline=False)
                                            embed.add_field(name = 'Отправитель:', value=interaction.user.mention, inline=False)
                                            embed.add_field(name = 'Сумма с комиссией:', value=f'{round(int(money) - mon)} {t1}', inline=False)
                                            embed.add_field(name = 'Сумма без комиссии:', value=f'{money} {t1}', inline=False)
                                            
                                            await interaction.send(embed = embed)   

                                            embed1=nextcord.Embed(title=f"**Поступление монет**", description = f"Комиссия с перевода: {com[1]}%", color=0x2b2d31)
                                            embed1.add_field(name = 'Получатель:', value=member.mention, inline=False)
                                            embed1.add_field(name = 'Отправитель:', value=interaction.user.mention, inline=False)
                                            embed1.add_field(name = 'Сумма с комиссией:', value=f'{round(int(money) - mon)} {t1}', inline=False)
                                            embed1.add_field(name = 'Сумма без комиссии:', value=f'{money} {t1}', inline=False)
                                            
                                            await member.send(embed = embed1)   
                                    else: 
                                        if com[0] < 10:
                                            mon = int(money)*com[0]         
                                            for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                                ec.execute(f'UPDATE balance SET bal={bal[0] - int(money)} where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                            for bal1 in ec.execute(f'SELECT bal FROM balance where id={member.id} and guild_id={interaction.guild.id}'):
                                                ec.execute(f'UPDATE balance SET bal={bal1[0] + round(money - mon)} where id={member.id} and guild_id={interaction.guild.id}')
                                            embed=nextcord.Embed(title=f"**Перевод монет**", description = f"Комиссия с перевода: {com[1]}%", color=0x2b2d31)
                                            embed.add_field(name = 'Получатель:', value=member.mention, inline=False)
                                            embed.add_field(name = 'Отправитель:', value=interaction.user.mention, inline=False)
                                            embed.add_field(name = 'Комментарий:', value=txt, inline=False)
                                            embed.add_field(name = 'Сумма с комиссией:', value=f'{round(int(money) - mon)} {t1}', inline=False)
                                            embed.add_field(name = 'Сумма без комиссии:', value=f'{money} {t1}', inline=False)
                                            
                                            await interaction.send(embed = embed)  

                                            embed1=nextcord.Embed(title=f"**Поступление монет**", description = f"Комиссия с перевода: {com[1]}%", color=0x2b2d31)
                                            embed1.add_field(name = 'Получатель:', value=member.mention, inline=False)
                                            embed1.add_field(name = 'Отправитель:', value=interaction.user.mention, inline=False)
                                            embed1.add_field(name = 'Комментарий:', value=txt, inline=False)
                                            embed1.add_field(name = 'Сумма с комиссией:', value=f'{round(int(money) - mon)} {t1}', inline=False)
                                            embed1.add_field(name = 'Сумма без комиссии:', value=f'{money} {t1}', inline=False)
                                            
                                            await member.send(embed = embed1)  
                                        else:
                                            mon = int(money)*com[0]   
                                            for bal in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                                ec.execute(f'UPDATE balance SET bal={bal[0] - int(money)} where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                            for bal1 in ec.execute(f'SELECT bal FROM balance where id={member.id} and guild_id={interaction.guild.id}'):
                                                ec.execute(f'UPDATE balance SET bal={bal1[0] + round(money - mon)} where id={member.id} and guild_id={interaction.guild.id}')
                                            embed=nextcord.Embed(title=f"**Перевод монет**", description = f"Комиссия с перевода: {com[1]}%", color=0x2b2d31)
                                            embed.add_field(name = 'Получатель:', value=member.mention, inline=False)
                                            embed.add_field(name = 'Отправитель:', value=interaction.user.mention, inline=False)
                                            embed.add_field(name = 'Комментарий:', value=txt, inline=False)
                                            embed.add_field(name = 'Сумма с комиссией:', value=f'{round(int(money) - mon)} {t1}', inline=False)
                                            embed.add_field(name = 'Сумма без комиссии:', value=f'{money} {t1}', inline=False)
                                            
                                            await interaction.send(embed = embed)  

                                            embed1=nextcord.Embed(title=f"**Поступление монет**", description = f"Комиссия с перевода: {com[1]}%", color=0x2b2d31)
                                            embed1.add_field(name = 'Получатель:', value=member.mention, inline=False)
                                            embed1.add_field(name = 'Отправитель:', value=interaction.user.mention, inline=False)
                                            embed1.add_field(name = 'Комментарий:', value=txt, inline=False)
                                            embed1.add_field(name = 'Сумма с комиссией:', value=f'{round(int(money) - mon)} {t1}', inline=False)
                                            embed1.add_field(name = 'Сумма без комиссии:', value=f'{money} {t1}', inline=False)
                                            
                                            await member.send(embed = embed1)  
                ec_db.commit()
     
    @nextcord.slash_command(description="Ежедневная награда", guild_ids = [int(settings["Guild_ID"])])
    @cooldowns.cooldown(1, 60*60*24, bucket=cooldowns.SlashBucket.author)
    async def timely(self, interaction: nextcord.Interaction):
        """・`timely`\n・Ежедневная награда, использовать можно 1 раз в 180 секунд"""
        ec_db = sqlite3.connect('database/economy.db', timeout=10)
        ec = ec_db.cursor() 
        for ec1 in ec.execute(f"SELECT timely_ot, timely_do FROM settings where guild_id={interaction.guild.id}"):
            money = random.randint(ec1[0], ec1[1])
            for em in ec.execute(f'SELECT currency FROM settings where guild_id={interaction.guild.id}'):
                t1 = self.bot.get_emoji(em[0]) 
                for row in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                    ec.execute(f'UPDATE balance SET bal={int(money) + row[0]} where id={interaction.user.id} and guild_id={interaction.guild.id}')
                ec_db.commit()

                a = await timely(money, interaction.user.display_avatar.url)
                await interaction.send(file=nextcord.File(a))

           
            
    @nextcord.slash_command(description="Бросить кубик", guild_ids = [int(settings["Guild_ID"])])
    async def cube(self, interaction: nextcord.Interaction, money:int, number:str = nextcord.SlashOption(
        name="number",
        description='Укажи число точек',
        choices={
        "Одна точка": '1',  
        "Две точки": '2',
        "Три точки": '3', 
        "Четыре точки": '4',
        "Пять точек": '5', 
        "Шесть точек": '6'
        })):
        ec_db = sqlite3.connect('database/economy.db', timeout=10)
        ec = ec_db.cursor()
        txt1 = random.randint(1,6)
        for em in ec.execute(f'SELECT currency FROM settings where guild_id={interaction.guild.id}'):
            t1 = self.bot.get_emoji(em[0])
            print(number)
            if 1 > money:    
                embed1=nextcord.Embed(description=f'Нельзя поставить сумму меньше 1-го', color=0x2b2d31)
                embed.set_thumbnail(url=interaction.user.display_avatar)
                await interaction.send(embed=embed1, empheral = True)      
            else:    
                for row in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                    if row[0] < money:  
                        embed112=nextcord.Embed(description=f'Недостаточно денюшек', color=0x2b2d31)
                        embed.set_thumbnail(url=interaction.user.display_avatar)
                        await interaction.send(embed=embed112, empheral = True)  
                    else:   
                        if txt1 == int(number):  
                            for row in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                ec.execute(f'UPDATE balance SET bal={(money*2) + row[0]} where id={interaction.user.id} and guild_id={interaction.guild.id}')
                            embed = nextcord.Embed(title='Cube', description=f'Вы угадали. Кости показали `{txt1}`. Вы получили {money*2} {t1}', color=0x2b2d31)
                            if txt1 == 1:
                                embed.set_image(url = 'https://media.discordapp.net/attachments/1085202500052865078/1085248122684444863/1.png?width=701&height=701')
                                embed.set_footer(text = f'Вы выйграли: {(money*2)}')
                            elif txt1 == 2:
                                embed.set_image(url = 'https://media.discordapp.net/attachments/1085202500052865078/1085248122948681928/2.png?width=701&height=701')
                                embed.set_footer(text = f'Вы выйграли: {(money*2)}')
                            elif txt1 == 3:
                                embed.set_image(url = 'https://media.discordapp.net/attachments/1085202500052865078/1085248123183570944/3.png?width=701&height=701')
                                embed.set_footer(text = f'Вы выйграли: {(money*2)}')
                            elif txt1 == 4:
                                embed.set_image(url = 'https://media.discordapp.net/attachments/1085202500052865078/1085248123393282128/4.png?width=701&height=701')
                                embed.set_footer(text = f'Вы выйграли: {(money*2)}')
                            elif txt1 == 5:
                                embed.set_image(url = 'https://media.discordapp.net/attachments/1085202500052865078/1085248123632353402/5.png?width=701&height=701')
                                embed.set_footer(text = f'Вы выйграли: {(money*2)}')
                            elif txt1 == 6:
                                embed.set_image(url = 'https://media.discordapp.net/attachments/1085202500052865078/1085248123909185586/6.png?width=701&height=701')
                                embed.set_footer(text = f'Вы выйграли: {(money*2)}')
                            
                            await interaction.send(embed=embed)
                            ec_db.commit()
                        else:
                            for row in ec.execute(f'SELECT bal FROM balance where id={interaction.user.id} and guild_id={interaction.guild.id}'):
                                ec.execute(f'UPDATE balance SET bal={row[0] - money} where id={interaction.user.id} and guild_id={interaction.guild.id}')
                            embed = nextcord.Embed(title='Cube', description=f'**Вы не угадали.** Кости показали `{txt1}`', color=0x2b2d31)
                            if txt1 == 1:
                                embed.set_image(url = 'https://media.discordapp.net/attachments/1085202500052865078/1085248122684444863/1.png?width=701&height=701')
                                embed.set_footer(text = f'Вы проиграли: {money}')
                            elif txt1 == 2:
                                embed.set_image(url = 'https://media.discordapp.net/attachments/1085202500052865078/1085248122948681928/2.png?width=701&height=701')
                                embed.set_footer(text = f'Вы проиграли: {money}')
                            elif txt1 == 3:
                                embed.set_image(url = 'https://media.discordapp.net/attachments/1085202500052865078/1085248123183570944/3.png?width=701&height=701')
                                embed.set_footer(text = f'Вы проиграли: {money}')
                            elif txt1 == 4:
                                embed.set_image(url = 'https://media.discordapp.net/attachments/1085202500052865078/1085248123393282128/4.png?width=701&height=701')
                                embed.set_footer(text = f'Вы проиграли: {money}')
                            elif txt1 == 5:
                                embed.set_image(url = 'https://media.discordapp.net/attachments/1085202500052865078/1085248123632353402/5.png?width=701&height=701')
                                embed.set_footer(text = f'Вы проиграли: {money}')
                            elif txt1 == 6:
                                embed.set_image(url = 'https://media.discordapp.net/attachments/1085202500052865078/1085248123909185586/6.png?width=701&height=701')
                                embed.set_footer(text = f'Вы проиграли: {money}')
                            await interaction.send(embed=embed)
                            ec_db.commit()

    ### Error ###

    @take.error 
    async def remove_error(self, interaction: nextcord.Interaction, error):
        if isinstance(error, nextcord.ext.application_checks.errors.ApplicationMissingPermissions):
            embed=nextcord.Embed(description = f"Не хватает прав.", color=0x2b2d31)
            embed.set_thumbnail(url=interaction.user.display_avatar)
            await interaction.send(embed = embed)




    @give.error 
    async def give_error(self, interaction: nextcord.Interaction, error):
        if isinstance(error, nextcord.ext.application_checks.errors.ApplicationMissingPermissions):
            embed=nextcord.Embed(description = f"Не хватает прав.", color=0x2b2d31)
            embed.set_thumbnail(url=interaction.user.display_avatar)
            await interaction.send(embed = embed)

    @awardp.error 
    async def awardp_error(self, interaction: nextcord.Interaction, error):
        if isinstance(error, nextcord.ext.application_checks.errors.ApplicationMissingPermissions):
            embed=nextcord.Embed(description = f"Не хватает прав.", color=0x2b2d31)
            embed.set_thumbnail(url=interaction.user.display_avatar)
            await interaction.send(embed = embed)



    @timely.error
    async def timely_error(self, interaction: nextcord.Interaction, error):
        if isinstance(error, cooldowns.exceptions.CallableOnCooldown):
            embed=nextcord.Embed(description="Команду **можно использовать** снова через **<t:{}:R>**".format(int(time.time() + error.retry_after)), color=0x2b2d31)
            embed.set_thumbnail(url=interaction.user.display_avatar)
            await interaction.send(embed=embed, ephemeral=True)




def setup(bot):
    bot.add_cog(economy(bot))