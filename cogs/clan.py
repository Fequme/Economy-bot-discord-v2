import nextcord
import sqlite3
from nextcord.ext import commands
import sqlite3
import traceback
import asyncio
import re
from clan import clan_owner
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from config import *
from nextcord.ext import tasks

c_db = sqlite3.connect('database/clan.db', timeout=10)
c = c_db.cursor()

ec_db = sqlite3.connect('database/economy.db', timeout=10)
ec = ec_db.cursor()

class clan1(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.voice_check.start()

    @tasks.loop(seconds = 60)
    async def voice_check(self):
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            if guild.id == int(settings['Guild_ID']):
                for channel in guild.voice_channels:
                    for member in channel.members:
                        for cu in c.execute(f"SELECT owner_club FROM user where id={member.id}"):
                            for cur in c.execute(f"SELECT voicetime, voice_id, role_id, balance FROM clan where owner={cu[0]}"):
                                role = guild.get_role(cur[2])
                                if channel.id == cur[1] and role in member.roles:
                                    for vefi in c.execute(f"SELECT voicetime FROM clan where owner={cu[0]}"):
                                        c.execute(f'UPDATE clan SET voicetime={vefi[0] + 60} where owner={cu[0]}')
                                        c.execute(f'UPDATE clan SET balance={cur[3] + 1} where owner={cu[0]}')
                                        c_db.commit()


    @nextcord.slash_command(description='Создать клан')
    async def clan_create(self, interaction: nextcord.Interaction):
        class clan(nextcord.ui.Modal):
            def __init__(self):
                super().__init__('Создание Embed')

                self.Name = nextcord.ui.TextInput(label = 'Имя', min_length=1, max_length=7, required=True, placeholder='Например: WinStrike')
                self.add_item(self.Name)




                




            async def callback(self, interaction: nextcord.Interaction) -> None:

                name = self.Name.value
                name = name.lower()
                

                
                c.execute(f"SELECT id, name FROM clan where id= {interaction.guild.id} and name = '{name}'")
                if c.fetchone() is None:
                    for curver in ec.execute(f"SELECT bal FROM balance where id = {interaction.user.id}"):
                        if curver[0] < 4000:
                            emb1 = nextcord.Embed(description=f"Для создания клана требуется взнос в размере: **4000**", color = 0x2f3136)
                            emb1.set_thumbnail(url = interaction.user.display_avatar.url)
                            await interaction.send(embed=emb1, ephemeral=True)
                        else:
                            ec.execute(f"UPDATE balance SET bal={curver[0] - 4000} where id={interaction.user.id}")
                            ec_db.commit()
                            time = date.today()
                            timeplus = time + timedelta(days=30)
                            
                            category = nextcord.utils.get(interaction.guild.categories, id = 1086640163117084722)
                            role = await interaction.guild.create_role(name=name)
                            channel = await interaction.guild.create_voice_channel(name = f"Clan {name}", category=category)

                            c.execute(f"INSERT INTO clan VALUES ({interaction.user.id}, 'None', 'None', '{name}', '{interaction.guild.id}', '{role.id}', '{channel.id}', 0, 0, '{time}', '{timeplus}', '{settings['avatar_club_bag']}', 0, 1, 0, 15)")
                            c.execute(f"UPDATE user SET guild_id={interaction.guild.id} where id={interaction.user.id}")
                            c.execute(f"UPDATE user SET owner_club={interaction.user.id} where id={interaction.user.id}")
                            c_db.commit()

                            await interaction.user.add_roles(role)
                            await channel.set_permissions(role, connect = True)

                            emb = nextcord.Embed(title = 'Ты успешно создал клан', description='Поздравляем с преобретением клана!', color = 0x2f3136)
                            emb.add_field(name='Имя:', value='```{}```'.format(name))
                            emb.set_thumbnail(url = f'{settings["avatar_club_bag"]}')
                            await interaction.send(embed=emb, ephemeral=True)
                else:
                    emb = nextcord.Embed(description='Ошибка в создание клана. \n\n**Клан с таким именем уже существует**', color = 0x2f3136)
                    emb.set_thumbnail(url = interaction.user.display_avatar.url)
                    await interaction.send(embed=emb, ephemeral=True)
                c_db.commit()
                

        for clan1 in c.execute(f"SELECT owner_club FROM user where id = {interaction.user.id}"):
            if clan1[0] == 0:
                await interaction.response.send_modal(clan())      
            else:
                emb1 = nextcord.Embed(description=f"Ты уже состоишь в клане. Дабы создать новый клан, покинь свой клан", color = 0x2f3136)
                emb1.set_thumbnail(url = interaction.user.display_avatar.url)
                await interaction.send(embed=emb1, ephemeral=True)      

    @nextcord.slash_command(description='Просмотреть клан')
    async def clan(self, interaction: nextcord.Interaction, member: nextcord.Member = None):
        user = member or interaction.user
        author = interaction.user
        bot = self.bot
        ownek = interaction.user.id
        for em in ec.execute(f'SELECT currency FROM settings where guild_id={interaction.guild.id}'):
            t1 = self.bot.get_emoji(em[0]) 

        class balance(nextcord.ui.Modal):
            def __init__(self):
                super().__init__('Баланс клана')

                self.EmTitle = nextcord.ui.TextInput(label = 'Сколько денюшек вы хотите внести?', min_length=2, max_length=50, required=True, placeholder='1000...', style=nextcord.TextInputStyle.paragraph)
                self.add_item(self.EmTitle)


    

            async def callback(self, interaction: nextcord.Interaction) -> None:
                title = self.EmTitle.value
                try:
                    for curver in ec.execute(f"SELECT bal FROM balance where id = {interaction.user.id}"):
                        if curver[0] < int(title):
                            embed = nextcord.Embed(description = f'У вас недостаточно средств для такого взноса.', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                        elif int(title) < 20:
                            embed = nextcord.Embed(description = f'Минимальный взнос равен **20** {t1}', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                        else:
                            for cus in c.execute(f"SELECT owner_club FROM user where id = {interaction.user.id}"):
                                for cusik in c.execute(f"SELECT balance FROM clan where owner = {cus[0]}"):
                                    c.execute(f"UPDATE clan SET balance={cusik[0] + int(title)} where owner={cus[0]}")
                                    ec.execute(f"UPDATE balance SET bal={curver[0] - int(title)} where id={cus[0]}")
                                    c_db.commit()
                                    ec_db.commit()
                            
                            embed = nextcord.Embed(description = f'Вы успешно внесли **{title}** {t1} в свой клуб.', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True) 
                except:
                    embed = nextcord.Embed(description = f'Вы неправильно указали взнос.', color=0x2f3136)
                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                    await interaction.send(embed=embed, ephemeral= True) 
        
        
        class settings(nextcord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)   

            @nextcord.ui.button(emoji = '✨', label = 'Пополнить средства', style = nextcord.ButtonStyle.grey, disabled=False)
            async def add(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if author.id == interaction.user.id:
                    await interaction.response.send_modal(balance())
                else:
                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                    await interaction.send(embed=embed, ephemeral= True)
            
            @nextcord.ui.button(emoji = '😊', label = 'Пригласить участника', style = nextcord.ButtonStyle.gray, disabled=False)
            async def addmember(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if author.id == interaction.user.id:
                    for frendlik in c.execute(f"SELECT owner_club FROM user where id={interaction.user.id}"):
                        for frendlisk in c.execute(f"SELECT members, max_members FROM clan where owner={frendlik[0]}"):
                            if frendlisk[0] == frendlisk[1]:
                                embed = nextcord.Embed(description = f'Клан заполнен, вы не можете пригласить участников, что бы повысить вместимость повысьте уровень клана.', color=0x2f3136)
                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                await interaction.send(embed=embed, ephemeral= True)  
                            else:
                                view = invite()
                                er=nextcord.Embed(description="Укажи **человека** или его **id** которого хочешь пригласить в клан", color=0x2f3136)
                                er.set_thumbnail(url=interaction.user.display_avatar)
                                ssf = await interaction.send(embed=er, ephemeral = True)
                                try: 
                                    msg = await bot.wait_for('message', check=lambda m: m.author.id == interaction.user.id, timeout = 30)
                                    s = msg.content
                                    member = re.sub("[<@>]","",s) 
                                except asyncio.exceptions.TimeoutError:
                                    er=nextcord.Embed(description="Вы не успели ввести пользователя, поэтому действии команды были отменены", color=0x2f3136)
                                    er.set_thumbnail(url=interaction.user.display_avatar)
                                    await interaction.send(embed=er)
                                try:
                                    global useri
                                    useri = interaction.guild.get_member(int(member))
                                    for frendli in c.execute(f"SELECT owner_club FROM user where id={interaction.user.id}"):
                                        for frendlis in c.execute(f"SELECT owner_club FROM user where id={useri.id}"):
                                            if frendlis[0] == 0:
                                                if useri.id == interaction.user.id:
                                                    embed = nextcord.Embed(description = f'Вы не можете пригласить самого себя', color=0x2f3136)
                                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                    await interaction.send(embed=embed, ephemeral= True)
                                                else:
                                                    for frendli in c.execute(f"SELECT owner_club FROM user where id={interaction.user.id}"):
                                                        for mebil in c.execute(f"SELECT avatar, name FROM clan where owner={frendli[0]}"):
                                                            er=nextcord.Embed(description=f"Вас пригласили в клан **{mebil[1]}**", color=0x2f3136)
                                                            er.set_thumbnail(url=mebil[0])
                                                            try:
                                                                global ff1
                                                                ff1 = await useri.send(embed=er, view = view)

                                                                er=nextcord.Embed(description=f"Вы успешно пригласили {useri.mention} в ваш клан **{mebil[1]}**", color=0x2f3136)
                                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                                await interaction.send(embed=er, ephemeral=True)
                                                                await msg.delete()
                                                            except:
                                                                er=nextcord.Embed(description=f"Вас пригласили в клан **{mebil[1]}**", color=0x2f3136)
                                                                er.set_thumbnail(url=mebil[0])
                                                                global ff2
                                                                ff2 = await interaction.send(f'{useri.mention}', embed=er, view=view)
                                                            
                                                                er=nextcord.Embed(description=f"Вы успешно пригласили {useri.mention} в ваш клан **{mebil[1]}**", color=0x2f3136)
                                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                                await interaction.send(embed=er, ephemeral=True)
                                                                await msg.delete()
                                                            
                                            else:
                                                er=nextcord.Embed(description="Данный участник уже состоит в клане", color=0x2f3136)
                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                try:
                                                    await interaction.send(embed=er)
                                                    await msg.delete()
                                                except:
                                                    pass
                                except:
                                    er=nextcord.Embed(description="Эй, ты неправильно указал пользователя", color=0x2f3136)
                                    er.set_thumbnail(url=interaction.user.display_avatar)
                                    await interaction.send(embed=er, ephemeral = True)
                else:
                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                    await interaction.send(embed=embed, ephemeral= True)

            @nextcord.ui.button(emoji = '🧺', label = 'Выгнать участника', style = nextcord.ButtonStyle.gray, disabled=False)
            async def addmemberff(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if author.id == interaction.user.id:
                    for frendlik in c.execute(f"SELECT owner_club FROM user where id={interaction.user.id}"):
                        for frendlisk in c.execute(f"SELECT members, max_members FROM clan where owner={frendlik[0]}"):
                            er=nextcord.Embed(description="Укажи **человека** или его **id** которого хочешь выгнать с клана", color=0x2f3136)
                            er.set_thumbnail(url=interaction.user.display_avatar)
                            ssf = await interaction.send(embed=er, ephemeral = True)
                            try: 
                                msg = await bot.wait_for('message', check=lambda m: m.author.id == interaction.user.id, timeout = 30)
                                s = msg.content
                                member = re.sub("[<@>]","",s) 
                            except asyncio.exceptions.TimeoutError:
                                er=nextcord.Embed(description="Вы не успели ввести пользователя, поэтому действии команды были отменены", color=0x2f3136)
                                er.set_thumbnail(url=interaction.user.display_avatar)
                                await interaction.send(embed=er)
                            try:
                                useri = interaction.guild.get_member(int(member))
                                for frendli in c.execute(f"SELECT owner_club FROM user where id={interaction.user.id}"):
                                    for frendlis in c.execute(f"SELECT owner_club FROM user where id={useri.id}"):
                                        if frendlis[0] == interaction.user.id:
                                            if useri.id == interaction.user.id:
                                                embed = nextcord.Embed(description = f'Вы не можете выгнать самого себя', color=0x2f3136)
                                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                await interaction.send(embed=embed, ephemeral= True)
                                                await msg.delete()
                                            else:
                                                for frendlig in c.execute(f"SELECT owner_club FROM user where id={useri.id}"):
                                                    for mebil in c.execute(f"SELECT avatar, name, members FROM clan where owner={frendlig[0]}"):
                        
                                                        er=nextcord.Embed(description=f"Вы успешно выгнали {useri.mention} с вашего клана **{mebil[1]}**", color=0x2f3136)
                                                        er.set_thumbnail(url=interaction.user.display_avatar)
                                                        await interaction.send(embed=er, ephemeral=True)
                                                        await msg.delete()
                                                        
                                                        c.execute(f"UPDATE clan SET members={mebil[2] - 1} where owner={frendli[0]}")
                                                        c.execute(f"UPDATE user SET owner_club=0 where id={useri.id}")
                                                        c_db.commit()
                                                        
                                                        try:
                                                            er=nextcord.Embed(description=f"Вас выгнал {interaction.user.mention} с клана **{mebil[1]}**", color=0x2f3136)
                                                            er.set_thumbnail(url=interaction.user.display_avatar)
                                                            await useri.send(embed=er)
                                                        except:
                                                            pass
                                                    
                                        else:
                                            embed = nextcord.Embed(description = f'Данный участник не состоит в вашем клане', color=0x2f3136)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                                            await interaction.send(embed=embed, ephemeral= True)
                                            try:
                                                await interaction.send(embed=er)
                                                await msg.delete()
                                            except:
                                                pass
                            except:
                                er=nextcord.Embed(description="Эй, ты неправильно указал пользователя", color=0x2f3136)
                                er.set_thumbnail(url=interaction.user.display_avatar)
                                await interaction.send(embed=er, ephemeral = True)
                else:
                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                    await interaction.send(embed=embed, ephemeral= True)
            
            @nextcord.ui.button(emoji = '💕', label = 'Участники', style = nextcord.ButtonStyle.grey, disabled=False)
            async def members(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if author.id == interaction.user.id:
                    for frendli in c.execute(f"SELECT owner_club FROM user where id={interaction.user.id}"):
                        for frendlis in c.execute(f"SELECT co_owner1, co_owner2, avatar FROM clan where owner={frendli[0]}"):
                            c.execute(f"SELECT id FROM user where owner_club = {frendli[0]}")
                            rows = c.fetchall()
                            sss = str(rows).replace(',', '')
                            fff = sss.replace('(', '<@')
                            kkk = fff.replace(')', '>')
                            ggg = kkk.replace('[', '')
                            lll = ggg.replace(']', '')
                            if frendlis[0] == 'None':
                                embed = nextcord.Embed(title = 'Участники', description = f'> Здесь ты можешь просмотреть всех участников своего клана', color=0x2f3136)
                                embed.set_thumbnail(url=f'{frendlis[2]}')       
                                embed.add_field(name="・Глава:", value=f'<@{frendli[0]}>', inline=False)
                                embed.add_field(name="・Участники:", value=f'{lll}', inline=False)
                                await interaction.send(embed=embed, ephemeral= True) 
                            elif frendlis[0] > 0 and frendlis[1] == 'None':
                                embed = nextcord.Embed(title = 'Участники', description = f'> Здесь ты можешь просмотреть всех участников своего клана', color=0x2f3136)
                                embed.set_thumbnail(url=f'{frendlis[2]}')       
                                embed.add_field(name="・Глава:", value=f'<@{frendli[0]}>', inline=False)
                                embed.add_field(name="・Заместители:", value=f'<@{frendlis[0]}>', inline=False)
                                embed.add_field(name="・Участники:", value=f'{lll}', inline=False)
                                await interaction.send(embed=embed, ephemeral= True) 
                            elif frendlis[0] > 0 and frendlis[1] > 0:
                                embed = nextcord.Embed(title = 'Участники', description = f'> Здесь ты можешь просмотреть всех участников своего клана', color=0x2f3136)
                                embed.set_thumbnail(url=f'{frendlis[2]}')       
                                embed.add_field(name="・Глава:", value=f'<@{frendli[0]}>', inline=False)
                                embed.add_field(name="・Заместители:", value=f'<@{frendlis[0]}> <@{frendlis[1]}>', inline=False)
                                embed.add_field(name='・Участники:', value=f'{lll}', inline=True)
                                await interaction.send(embed=embed, ephemeral= True) 
                else:
                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                    await interaction.send(embed=embed, ephemeral= True)

        class invite(nextcord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
            
            @nextcord.ui.button(label = 'Вступить в клан', style = nextcord.ButtonStyle.green, disabled=False)
            async def vxod(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                for mebi in c.execute(f"SELECT owner_club FROM user where id={author.id}"): 
                    for mebis in c.execute(f"SELECT members FROM clan where owner={mebi[0]}"): 
                        c.execute(f"UPDATE clan SET members={mebis[0] + 1} where owner={mebi[0]}")
                        c_db.commit()
                for veib in c.execute(f"SELECT owner_club FROM user where id={author.id}"):    
                    c.execute(f"UPDATE user SET owner_club={veib[0]} where id={useri.id}")
                    c_db.commit()
                    
                    for veibv in c.execute(f"SELECT name, avatar FROM clan where owner={author.id}"):

                        er=nextcord.Embed(description=f"Вас пригласили в клан **{veibv[0]}**", color=0x2f3136)
                        er.set_thumbnail(url=veibv[1])    
                        er.set_footer(text='Положение: Принято')
                        
                        try:
                            await ff1.edit(embed = er, view=None)
                        except:
                            await ff2.edit(embed = er, view=None)

                        embed = nextcord.Embed(description = f'Принял ваше приглашение в клан: **{veibv[0]}**', color=0x2f3136)
                        embed.set_thumbnail(url=useri.display_avatar) 
                        try:      
                            await author.send(embed=embed)
                        except:
                            pass

                        await useri.add_roles(role)


            @nextcord.ui.button(label = 'Отклонить приглашение', style = nextcord.ButtonStyle.red, disabled=False)
            async def vixod(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if interaction.user.id == useri.id:
                    for mebi in c.execute(f"SELECT name, avatar FROM clan where owner={author.id}"):
                        embed = nextcord.Embed(description = f'Отклонил ваше приглашение в клан: **{mebi[0]}**', color=0x2f3136)
                        embed.set_thumbnail(url=useri.display_avatar)  

                        er=nextcord.Embed(description=f"Вас пригласили в клан **{mebi[0]}**", color=0x2f3136)
                        er.set_thumbnail(url=mebi[1])    
                        er.set_footer(text='Положение: Отклонено')  
                        
                        try:      
                            await author.send(embed=embed)
                        except:
                            pass   


                        try:
                            await ff1.edit(embed = er, view=None)
                        except:
                            await ff2.edit(embed = er, view=None)
                else:
                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                    await interaction.send(embed=embed, ephemeral= True)

        class invite1(nextcord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
            
            @nextcord.ui.button(label = 'Вступить в клан', style = nextcord.ButtonStyle.green, disabled=False)
            async def vxods(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                for mebi in c.execute(f"SELECT owner_club FROM user where id={author.id}"): 
                    for mebis in c.execute(f"SELECT members FROM clan where owner={mebi[0]}"): 
                        c.execute(f"UPDATE clan SET members={mebis[0] + 1} where owner={mebi[0]}")
                        c_db.commit()
                for veib in c.execute(f"SELECT owner_club FROM user where id={author.id}"):    
                    c.execute(f"UPDATE user SET owner_club={veib[0]} where id={useri.id}")
                    c_db.commit()
                    
                    for veibv in c.execute(f"SELECT name, avatar FROM clan where owner={author.id}"):

                        er=nextcord.Embed(description=f"Вас пригласили в клан **{veibv[0]}**", color=0x2f3136)
                        er.set_thumbnail(url=veibv[1])    
                        er.set_footer(text='Положение: Принято')
                        
                        try:
                            await ff4.edit(embed = er, view=None)
                        except:
                            await ff5.edit(embed = er, view=None)

                        embed = nextcord.Embed(description = f'Принял ваше приглашение в клан: **{veibv[0]}**', color=0x2f3136)
                        embed.set_thumbnail(url=useri.display_avatar) 
                        try:      
                            await author.send(embed=embed)
                        except:
                            pass

                        await useri.add_roles(role)


            @nextcord.ui.button(label = 'Отклонить приглашение', style = nextcord.ButtonStyle.red, disabled=False)
            async def vixods(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if interaction.user.id == useri.id:
                    for mebi in c.execute(f"SELECT name, avatar FROM clan where owner={author.id}"):
                        embed = nextcord.Embed(description = f'Отклонил ваше приглашение в клан: **{mebi[0]}**', color=0x2f3136)
                        embed.set_thumbnail(url=useri.display_avatar)  

                        er=nextcord.Embed(description=f"Вас пригласили в клан **{mebi[0]}**", color=0x2f3136)
                        er.set_thumbnail(url=mebi[1])    
                        er.set_footer(text='Положение: Отклонено')  
                        
                        try:      
                            await author.send(embed=embed)
                        except:
                            pass   


                        try:
                            await ff4.edit(embed = er, view=None)
                        except:
                            await ff5.edit(embed = er, view=None)
                else:
                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                    await interaction.send(embed=embed, ephemeral= True)

        class settings1(nextcord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)

            @nextcord.ui.button(emoji = '😍', label = 'Выйти из клана', style = nextcord.ButtonStyle.grey, disabled=False)
            async def leavef(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if author.id == interaction.user.id:
                    for curver in c.execute(f"SELECT owner_club FROM user where id = {interaction.user.id}"):
                        if curver[0] == interaction.user.id:
                            embed = nextcord.Embed(description = f'Ты не можешь покинуть собственный клан', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True) 
                        else: 
                            for mebi in c.execute(f"SELECT owner_club FROM user where id={interaction.user.id}"): 
                                for mebi1 in c.execute(f"SELECT members FROM clan where owner={mebi[0]}"): 
                                    c.execute(f"UPDATE clan SET members={mebi1[0] - 1} where owner={mebi[0]}")
                                    c.execute(f"UPDATE user SET owner_club=0 where id={interaction.user.id}")
                                    c_db.commit() 
                                    await interaction.user.remove_roles(role)
                                    embed = nextcord.Embed(description = f'Ты успешно вышел с клана **{clan[0]}**', color=0x2f3136)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.edit(view = None)    
                                    await interaction.send(embed=embed, ephemeral= True)                                      
                else:
                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                    await interaction.send(embed=embed, ephemeral= True)                                

            @nextcord.ui.button(emoji = '👌', label = 'Пополнить средства', style = nextcord.ButtonStyle.grey, disabled=False)
            async def addf(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if author.id == interaction.user.id:
                    await interaction.response.send_modal(balance())
                else:
                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                    await interaction.send(embed=embed, ephemeral= True)
            
            @nextcord.ui.button(emoji = '😁', label = 'Участники', style = nextcord.ButtonStyle.grey, disabled=False)
            async def members(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if author.id == interaction.user.id:
                    for frendli in c.execute(f"SELECT owner_club FROM user where id={interaction.user.id}"):
                        for frendlis in c.execute(f"SELECT co_owner1, co_owner2, avatar FROM clan where owner={frendli[0]}"):
                            c.execute(f"SELECT id FROM user where owner_club = {frendli[0]}")
                            rows = c.fetchall()
                            sss = str(rows).replace(',', '')
                            fff = sss.replace('(', '<@')
                            kkk = fff.replace(')', '>')
                            ggg = kkk.replace('[', '')
                            lll = ggg.replace(']', '')
                            if frendlis[0] == 'None':
                                embed = nextcord.Embed(title = 'Участники', description = f'> Здесь ты можешь просмотреть всех участников своего клана', color=0x2f3136)
                                embed.set_thumbnail(url=f'{frendlis[2]}')       
                                embed.add_field(name="・Глава:", value=f'<@{frendli[0]}>', inline=False)
                                embed.add_field(name="・Участники:", value=f'{lll}', inline=False)
                                await interaction.send(embed=embed, ephemeral= True) 
                            elif frendlis[0] > 0 and frendlis[1] == 'None':
                                embed = nextcord.Embed(title = 'Участники', description = f'> Здесь ты можешь просмотреть всех участников своего клана', color=0x2f3136)
                                embed.set_thumbnail(url=f'{frendlis[2]}')       
                                embed.add_field(name="・Глава:", value=f'<@{frendli[0]}>', inline=False)
                                embed.add_field(name="・Заместители:", value=f'<@{frendlis[0]}>', inline=False)
                                embed.add_field(name="・Участники:", value=f'{lll}', inline=False)
                                await interaction.send(embed=embed, ephemeral= True) 
                            elif frendlis[0] > 0 and frendlis[1] > 0:
                                embed = nextcord.Embed(title = 'Участники', description = f'> Здесь ты можешь просмотреть всех участников своего клана', color=0x2f3136)
                                embed.set_thumbnail(url=f'{frendlis[2]}')       
                                embed.add_field(name="・Глава:", value=f'<@{frendli[0]}>', inline=False)
                                embed.add_field(name="・Заместители:", value=f'<@{frendlis[0]}> <@{frendlis[1]}>', inline=False)
                                embed.add_field(name='・Участники:', value=f'{lll}', inline=True)
                                await interaction.send(embed=embed, ephemeral= True) 
                else:
                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                    await interaction.send(embed=embed, ephemeral= True)

        
        class settings2(nextcord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)

            @nextcord.ui.button(emoji = '💕', label = 'Выйти из клана', style = nextcord.ButtonStyle.grey, disabled=False)
            async def leavesd(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if author.id == interaction.user.id:
                    for curver in c.execute(f"SELECT owner_club FROM user where id = {interaction.user.id}"):
                        if curver[0] == interaction.user.id:
                            embed = nextcord.Embed(description = f'Ты не можешь покинуть собственный клан', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True) 
                        else: 
                            for mebi in c.execute(f"SELECT owner_club FROM user where id={interaction.user.id}"): 
                                for mebi1 in c.execute(f"SELECT members, co_owner1, co_owner2 FROM clan where owner={mebi[0]}"): 
                                    if interaction.user.id == mebi1[1]:
                                        c.execute(f"UPDATE clan SET co_owner1='None' where owner={mebi[0]}")
                                        c_db.commit() 
                                    elif interaction.user.id == mebi1[2]:
                                        c.execute(f"UPDATE clan SET co_owner2='None' where owner={mebi[0]}")
                                        c_db.commit() 

                                    c.execute(f"UPDATE clan SET members={mebi1[0] - 1} where owner={mebi[0]}")
                                    c.execute(f"UPDATE user SET owner_club=0 where id={interaction.user.id}")
                                    c_db.commit() 

                                    await interaction.user.remove_roles(role)
                                    embed = nextcord.Embed(description = f'Ты успешно вышел с клана **{clan[0]}**', color=0x2f3136)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.edit(view = None)    
                                    await interaction.send(embed=embed, ephemeral= True)                                      
                else:
                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                    await interaction.send(embed=embed, ephemeral= True)                                

            @nextcord.ui.button(emoji = '✨', label = 'Пополнить средства', style = nextcord.ButtonStyle.grey, disabled=False)
            async def addsd(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if author.id == interaction.user.id:
                    await interaction.response.send_modal(balance())
                else:
                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                    await interaction.send(embed=embed, ephemeral= True)
            

            @nextcord.ui.button(emoji = '😒', label = 'Пригласить участника', style = nextcord.ButtonStyle.gray, disabled=False)
            async def addmember(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if author.id == interaction.user.id:
                    for frendlik in c.execute(f"SELECT owner_club FROM user where id={interaction.user.id}"):
                        for frendlisk in c.execute(f"SELECT members, max_members FROM clan where owner={frendlik[0]}"):
                            if frendlisk[0] == frendlisk[1]:
                                embed = nextcord.Embed(description = f'Клан заполнен, вы не можете пригласить участников, что бы повысить вместимость повысьте уровень клана.', color=0x2f3136)
                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                await interaction.send(embed=embed, ephemeral= True)  
                            else:
                                view = invite()
                                er=nextcord.Embed(description="Укажи **человека** или его **id** которого хочешь пригласить в клан", color=0x2f3136)
                                er.set_thumbnail(url=interaction.user.display_avatar)
                                ssf = await interaction.send(embed=er, ephemeral = True)
                                try: 
                                    msg = await bot.wait_for('message', check=lambda m: m.author.id == interaction.user.id, timeout = 30)
                                    s = msg.content
                                    member = re.sub("[<@>]","",s) 
                                except asyncio.exceptions.TimeoutError:
                                    er=nextcord.Embed(description="Вы не успели ввести пользователя, поэтому действии команды были отменены", color=0x2f3136)
                                    er.set_thumbnail(url=interaction.user.display_avatar)
                                    await interaction.send(embed=er, ephemeral=True)
                                try:
                                    global useri
                                    useri = interaction.guild.get_member(int(member))
                                    for frendli in c.execute(f"SELECT owner_club FROM user where id={interaction.user.id}"):
                                        for frendlis in c.execute(f"SELECT owner_club FROM user where id={useri.id}"):
                                            if frendlis[0] == 0:
                                                if useri.id == interaction.user.id:
                                                    embed = nextcord.Embed(description = f'Вы не можете пригласить самого себя', color=0x2f3136)
                                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                    await interaction.send(embed=embed, ephemeral= True)
                                                else:
                                                    for frendli in c.execute(f"SELECT owner_club FROM user where id={interaction.user.id}"):
                                                        for mebil in c.execute(f"SELECT avatar, name FROM clan where owner={frendli[0]}"):
                                                            er=nextcord.Embed(description=f"Вас пригласили в клан **{mebil[1]}**", color=0x2f3136)
                                                            er.set_thumbnail(url=mebil[0])
                                                            try:
                                                                global ff4
                                                                ff4 = await useri.send(embed=er, view = view)

                                                                er=nextcord.Embed(description=f"Вы успешно пригласили {useri.mention} в ваш клан **{mebil[1]}**", color=0x2f3136)
                                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                                await interaction.send(embed=er)
                                                                await msg.delete()
                                                            except:
                                                                er=nextcord.Embed(description=f"Вас пригласили в клан **{mebil[1]}**", color=0x2f3136)
                                                                er.set_thumbnail(url=mebil[0])
                                                                global ff5
                                                                ff5 = await interaction.send(f'{useri.mention}', embed=er, view=view)
                                                            
                                                                er=nextcord.Embed(description=f"Вы успешно пригласили {useri.mention} в ваш клан **{mebil[1]}**", color=0x2f3136)
                                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                                await interaction.send(embed=er, ephemeral=True)
                                                                await msg.delete()
                                                            
                                            else:
                                                er=nextcord.Embed(description="Данный участник уже состоит в клане", color=0x2f3136)
                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                try:
                                                    await interaction.send(embed=er)
                                                    await msg.delete()
                                                except:
                                                    pass
                                except:
                                    er=nextcord.Embed(description="Эй, ты неправильно указал пользователя", color=0x2f3136)
                                    er.set_thumbnail(url=interaction.user.display_avatar)
                                    await interaction.send(embed=er, ephemeral = True)
                else:
                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                    await interaction.send(embed=embed, ephemeral= True)

            @nextcord.ui.button(emoji = '💕', label = 'Выгнать участника', style = nextcord.ButtonStyle.gray, disabled=False)
            async def addmembersfsf(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if author.id == interaction.user.id:
                    for frendlik in c.execute(f"SELECT owner_club FROM user where id={interaction.user.id}"):
                        for frendlisk in c.execute(f"SELECT members, max_members FROM clan where owner={frendlik[0]}"):
                            er=nextcord.Embed(description="Укажи **человека** или его **id** которого хочешь выгнать с клана", color=0x2f3136)
                            er.set_thumbnail(url=interaction.user.display_avatar)
                            ssf = await interaction.send(embed=er, ephemeral = True)
                            try: 
                                msg = await bot.wait_for('message', check=lambda m: m.author.id == interaction.user.id, timeout = 30)
                                s = msg.content
                                member = re.sub("[<@>]","",s) 
                            except asyncio.exceptions.TimeoutError:
                                er=nextcord.Embed(description="Вы не успели ввести пользователя, поэтому действии команды были отменены", color=0x2f3136)
                                er.set_thumbnail(url=interaction.user.display_avatar)
                                await interaction.send(embed=er, ephemeral=True)
                            try:
                                useri = interaction.guild.get_member(int(member))
                                for frendli in c.execute(f"SELECT owner_club FROM user where id={interaction.user.id}"):
                                    for frendlis in c.execute(f"SELECT owner_club FROM user where id={useri.id}"):
                                        if frendlis[0] == interaction.user.id:
                                            if useri.id == interaction.user.id:
                                                embed = nextcord.Embed(description = f'Вы не можете выгнать самого себя', color=0x2f3136)
                                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                                await interaction.send(embed=embed, ephemeral= True)
                                                await msg.delete()
                                            else:
                                                for frendli in c.execute(f"SELECT owner_club FROM user where id={useri.id}"):
                                                    for mebil in c.execute(f"SELECT avatar, name, members FROM clan where owner={frendli[0]}"):
                        
                                                        er=nextcord.Embed(description=f"Вы успешно выгнали {useri.mention} с вашего клана **{mebil[1]}**", color=0x2f3136)
                                                        er.set_thumbnail(url=interaction.user.display_avatar)
                                                        await interaction.send(embed=er, ephemeral=True)
                                                        await msg.delete()
                                                        
                                                        c.execute(f"UPDATE clan SET members={mebil[2] - 1} where owner={frendli[0]}")
                                                        c.execute(f"UPDATE user SET owner_club=0 where id={useri.id}")
                                                        c_db.commit()
                                                        
                                                        try:
                                                            er=nextcord.Embed(description=f"Вас выгнал {interaction.user.mention} с клана **{mebil[1]}**", color=0x2f3136)
                                                            er.set_thumbnail(url=interaction.user.display_avatar)
                                                            await useri.send(embed=er)
                                                        except:
                                                            pass
                                        else:
                                            embed = nextcord.Embed(description = f'Данный участник не состоит в вашем клане', color=0x2f3136)
                                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                                            await interaction.send(embed=embed, ephemeral= True)
                                            try:
                                                await interaction.send(embed=er)
                                                await msg.delete()
                                            except:
                                                pass
                            except:
                                er=nextcord.Embed(description="Эй, ты неправильно указал пользователя", color=0x2f3136)
                                er.set_thumbnail(url=interaction.user.display_avatar)
                                await interaction.send(embed=er, ephemeral = True)
                else:
                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                    await interaction.send(embed=embed, ephemeral= True)

            
            @nextcord.ui.button(emoji = '🧺', label = 'Участники', style = nextcord.ButtonStyle.grey, disabled=False)
            async def members(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if author.id == interaction.user.id:
                    for frendli in c.execute(f"SELECT owner_club FROM user where id={interaction.user.id}"):
                        for frendlis in c.execute(f"SELECT co_owner1, co_owner2, avatar FROM clan where owner={frendli[0]}"):
                            c.execute(f"SELECT id FROM user where owner_club = {frendli[0]}")
                            rows = c.fetchall()
                            sss = str(rows).replace(',', '')
                            fff = sss.replace('(', '<@')
                            kkk = fff.replace(')', '>')
                            ggg = kkk.replace('[', '')
                            lll = ggg.replace(']', '')
                            if frendlis[0] == 'None':
                                embed = nextcord.Embed(title = 'Участники', description = f'> Здесь ты можешь просмотреть всех участников своего клана', color=0x2f3136)
                                embed.set_thumbnail(url=f'{frendlis[2]}')       
                                embed.add_field(name="・Глава:", value=f'<@{frendli[0]}>', inline=False)
                                embed.add_field(name="・Участники:", value=f'{lll}', inline=False)
                                await interaction.send(embed=embed, ephemeral= True) 
                            elif frendlis[0] > 0 and frendlis[1] == 'None':
                                embed = nextcord.Embed(title = 'Участники', description = f'> Здесь ты можешь просмотреть всех участников своего клана', color=0x2f3136)
                                embed.set_thumbnail(url=f'{frendlis[2]}')       
                                embed.add_field(name="・Глава:", value=f'<@{frendli[0]}>', inline=False)
                                embed.add_field(name="・Заместители:", value=f'<@{frendlis[0]}>', inline=False)
                                embed.add_field(name="・Участники:", value=f'{lll}', inline=False)
                                await interaction.send(embed=embed, ephemeral= True) 
                            elif frendlis[0] > 0 and frendlis[1] > 0:
                                embed = nextcord.Embed(title = 'Участники', description = f'> Здесь ты можешь просмотреть всех участников своего клана', color=0x2f3136)
                                embed.set_thumbnail(url=f'{frendlis[2]}')       
                                embed.add_field(name="・Глава:", value=f'<@{frendli[0]}>', inline=False)
                                embed.add_field(name="・Заместители:", value=f'<@{frendlis[0]}> <@{frendlis[1]}>', inline=False)
                                embed.add_field(name='・Участники:', value=f'{lll}', inline=True)
                                await interaction.send(embed=embed, ephemeral= True) 
                else:
                    embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                    await interaction.send(embed=embed, ephemeral= True)
                            
            
           

                    
        if member == None:
            for clan in c.execute(f"SELECT owner_club FROM user where id = {author.id}"):
                if clan[0] == 0:
                    emb1 = nextcord.Embed(description=f"Вы не состоите в клане", color = 0x2f3136)
                    emb1.set_thumbnail(url = interaction.user.display_avatar.url)
                    await interaction.send(embed=emb1, ephemeral=True)                  
                else:
                    for dops in c.execute(f"SELECT owner_club FROM user where id={interaction.user.id}"):
                        for dopclan in c.execute(f"SELECT owner, role_id, datecreate, datesbor, balance, voicetime, avatar, co_owner1, co_owner2, co_owner_count, voice_id, members, name, lvl, max_members FROM clan where owner={dops[0]}"):
                            if dopclan[0] == dops[0]:
                                rt = relativedelta(seconds=dopclan[5])
                                voicetime = '{:01d} d. {:01d} h. {:01d} m. '.format(int(rt.days), int(rt.hours), int(rt.minutes))
                                number = 0
                                role = interaction.guild.get_role(dopclan[1])
                                for member1 in role.members:
                                    number += 1
                                owner = interaction.guild.get_member(dopclan[0])
                                try:
                                    if dops[0] == interaction.user.id:
                                        back = 'clan.png'
                                        a = await clan_owner(back, str(owner.display_avatar.url), dopclan[3], dopclan[4], dopclan[11], voicetime, dopclan[12], dopclan[6], dopclan[13], dopclan[14])
                                        await interaction.response.defer()
                                        await interaction.send(file=nextcord.File(a), view=settings())
                                    elif interaction.user.id == dopclan[7] or interaction.user.id == dopclan[8]:
                                        back = 'clan.png'
                                        a = await clan_owner(back, str(owner.display_avatar.url), dopclan[3], dopclan[4], dopclan[11], voicetime, dopclan[12], dopclan[6], dopclan[13], dopclan[14])
                                        await interaction.response.defer()
                                        await interaction.send(file=nextcord.File(a), view=settings2())
                                    else:
                                        back = 'clan.png'
                                        a = await clan_owner(back, str(owner.display_avatar.url), dopclan[3], dopclan[4], dopclan[11], voicetime, dopclan[12], dopclan[6], dopclan[13], dopclan[14])
                                        await interaction.response.defer()
                                        await interaction.send(file=nextcord.File(a), view=settings1())
                                except Error as e:
                                    # обработка исключения
                                    print(f"Произошла ошибка: {e}")
        else:
            for clans in c.execute(f"SELECT owner_club FROM user where id = {member.id}"):
                if clans[0] == 0:
                    emb1 = nextcord.Embed(description=f"Данный пользователь не состоил в клане", color = 0x2f3136)
                    emb1.set_thumbnail(url = member.display_avatar.url)
                    await interaction.send(embed=emb1, ephemeral=True)                  
                else:
                    for fifa in c.execute(f"SELECT owner_club FROM user where id={member.id}"):
                        for rita in c.execute(f"SELECT owner, role_id, datecreate, datesbor, balance, voicetime, avatar, co_owner1, co_owner2, co_owner_count, voice_id, members, name, lvl, max_members FROM clan where owner={fifa[0]}"):
                            if rita[0] == fifa[0]:
                                rt = relativedelta(seconds=rita[5])
                                voicetime = '{:01d} d. {:01d} h. {:01d} m.'.format(int(rt.days), int(rt.hours), int(rt.minutes))
                                number = 0
                                role = interaction.guild.get_role(rita[1])
                                for member1 in role.members:
                                    number += 1
                                owner = interaction.guild.get_member(rita[0])
                                try:
                                    back = 'clan.png'
                                    a = await clan_owner(back, str(owner.display_avatar.url), rita[3], rita[4], rita[11], voicetime, rita[12], rita[6], rita[13], rita[14])
                                    await interaction.response.defer()
                                    await interaction.send(file=nextcord.File(a))
                                except:
                                    embed = nextcord.Embed(description = f'Ты не можешь глянуть клан участника, т.к. он не настроен полностью.', color=0x2f3136)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)
                            



    @nextcord.slash_command(description='Редактировать клан')
    async def clan_manager(self, interaction: nextcord.Interaction):
        author = interaction.user
        bot = self.bot
        for em in ec.execute(f'SELECT currency FROM settings where guild_id={interaction.guild.id}'):
            t1 = self.bot.get_emoji(em[0]) 
        class kivisi(nextcord.ui.Modal):
            def __init__(self):
                super().__init__('Аватарка клана')

                self.EmTitle = nextcord.ui.TextInput(label = 'Укажите url аватарки ниже', min_length=2, max_length=4000, required=True, placeholder='url', style=nextcord.TextInputStyle.paragraph)
                self.add_item(self.EmTitle)


    

            async def callback(self, interaction: nextcord.Interaction) -> None:
                title = self.EmTitle.value
                
                try:
                    c.execute(f"UPDATE clan SET avatar='{title}' where owner={interaction.user.id}")
                    c_db.commit()
                    embed = nextcord.Embed(description = f'Вы успешно сменили аватарку клуба.', color=0x2f3136)
                    embed.set_thumbnail(url=f'{title}')       
                    await interaction.send(embed=embed, ephemeral= True)

                    for bibi in c.execute(f"SELECT id, owner_club FROM user where id={interaction.user.id}"):
                        for bibis in c.execute(f"SELECT avatar, name, datecreate FROM clan where owner={bibi[1]}"):
                            embed = nextcord.Embed(title = f'{bibis[1]}', description = f'> Здесь расположены инструменты для редактирования клана.', color=0x2f3136)
                            embed.add_field(name='・дата создания:', value=f'```{bibis[2]}```', inline=False)
                            embed.set_thumbnail(url=f'{bibis[0]}')
                            await jorj.edit(embed=embed)

                except:
                    c.execute(f"UPDATE clan SET avatar='{settings['avatar_club_bag']}' where owner={interaction.user.id}")
                    c_db.commit()
                    embed = nextcord.Embed(description = f'Аватарка не рабочая, поэтому аватар клана был сменён на стандартный', color=0x2f3136)
                    embed.set_thumbnail(url=f'{settings["avatar_club_bag"]}')       
                    await interaction.send(embed=embed, ephemeral= True)
        
        class kivisik(nextcord.ui.Modal):
            def __init__(self):
                super().__init__('Название клана')

                self.EmTitle = nextcord.ui.TextInput(label = 'Укажите название клана ниже', min_length=1, max_length=7, required=True, placeholder='Например: Fufl', style=nextcord.TextInputStyle.paragraph)
                self.add_item(self.EmTitle)


    

            async def callback(self, interaction: nextcord.Interaction) -> None:
                title = self.EmTitle.value
                c.execute(f"SELECT id, name FROM clan where id= {interaction.guild.id} and name = '{title}'")
                if c.fetchone() is None:
                    for curver in ec.execute(f"SELECT bal FROM balance where id = {interaction.user.id}"):
                        c.execute(f"UPDATE clan SET name='{title}' where owner={interaction.user.id}")
                        ec.execute(f"UPDATE balance SET bal={curver[0] - int(settings['name_club_cena'])} where id={interaction.user.id}")

                        for sei in c.execute(f"SELECT role_id, voice_id FROM clan where owner = {interaction.user.id}"):
                            role = nextcord.utils.get(interaction.guild.roles, id = sei[0])
                            voice = nextcord.utils.get(interaction.guild.channels, id = sei[1])
                        
                        await role.edit(name=title)
                        await voice.edit(name=f'Clan {title}')
                        
                        emb = nextcord.Embed(description=f'Вы успешно сменили название на **{title}**', color = 0x2f3136)
                        emb.set_thumbnail(url = interaction.user.display_avatar.url)
                        await interaction.send(embed=emb, ephemeral=True)
                        
                        for bibi in c.execute(f"SELECT id, owner_club FROM user where id={interaction.user.id}"):
                            for bibis in c.execute(f"SELECT avatar, name, datecreate FROM clan where owner={bibi[1]}"):
                                embed = nextcord.Embed(title = f'{bibis[1]}', description = f'> Здесь расположены инструменты для редактирования клана.', color=0x2f3136)
                                embed.add_field(name='・дата создания:', value=f'```{bibis[2]}```', inline=False)
                                embed.set_thumbnail(url=f'{bibis[0]}')
                                await jorj.edit(embed=embed)
                else:
                    emb = nextcord.Embed(description='Ошибка в изменении названия клана. \n\nError: **Клан с таким именем уже существует**', color = 0x2f3136)
                    emb.set_thumbnail(url = interaction.user.display_avatar.url)
                    await interaction.send(embed=emb, ephemeral=True)
                c_db.commit()
        
        class Trues(nextcord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)

            @nextcord.ui.button(label = 'Да', style = nextcord.ButtonStyle.green, disabled=False)
            async def nimess(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                for frendlis in c.execute(f"SELECT co_owner1, co_owner2, name, avatar, co_owner_count, owner FROM clan where owner={interaction.user.id}"):
                    for frs in c.execute(f"SELECT owner_club FROM user where id={useri1.id}"):
                        if frs[0] == interaction.user.id:
                            if frendlis[0] == useri1.id:
                                c.execute(f"UPDATE clan SET co_owner_count={frendlis[4] - 1} where owner={interaction.user.id}")
                                c.execute(f"UPDATE clan SET co_owner1='None' where owner={interaction.user.id}")
                                c.execute(f"UPDATE clan SET owner={useri1.id} where owner={interaction.user.id}")
                                c.execute(f"UPDATE user SET owner_club={useri1.id} where owner_club={interaction.user.id}")
                                c_db.commit()

                                er=nextcord.Embed(description=f"Вы успешно **передали главу** учатнику: {useri1.mention}", color=0x2f3136)
                                er.set_thumbnail(url=interaction.user.display_avatar)
                                await aa.edit(embed=er, view=None) 

                                ers=nextcord.Embed(description=f"Поздравляю! Вам передали главу в клане: **{frendlis[2]}**", color=0x2f3136)
                                ers.set_thumbnail(url=f'{frendlis[3]}')
                                try:
                                    await useri1.send(embed=ers) 
                                except:
                                    pass
                            elif frendlis[1] == useri1.id:
                                c.execute(f"UPDATE clan SET co_owner_count={frendlis[4] - 1} where owner={interaction.user.id}")
                                c.execute(f"UPDATE clan SET co_owner2='None' where owner={interaction.user.id}")
                                c.execute(f"UPDATE clan SET owner={useri1.id} where owner={interaction.user.id}")
                                c.execute(f"UPDATE user SET owner_club={useri1.id} where owner_club={interaction.user.id}")
                                c_db.commit()

                                er=nextcord.Embed(description=f"Вы успешно **передали главу** учатнику: {useri1.mention}", color=0x2f3136)
                                er.set_thumbnail(url=interaction.user.display_avatar)
                                await aa.edit(embed=er, view=None)

                                ers=nextcord.Embed(description=f"Поздравляю! Вам передали главу в клане: **{frendlis[2]}**", color=0x2f3136)
                                ers.set_thumbnail(url=f'{frendlis[3]}')
                                try:
                                    await useri1.send(embed=ers) 
                                except:
                                    pass 
                            else:
                                c.execute(f"UPDATE clan SET owner={useri1.id} where owner={interaction.user.id}")
                                c.execute(f"UPDATE user SET owner_club={useri1.id} where owner_club={interaction.user.id}")
                                c_db.commit()

                                er=nextcord.Embed(description=f"Вы успешно **передали главу** учатнику: {useri1.mention}", color=0x2f3136)
                                er.set_thumbnail(url=interaction.user.display_avatar)
                                await aa.edit(embed=er, view=None) 

                                ers=nextcord.Embed(description=f"Поздравляю! Вам передали главу в клане: **{frendlis[2]}**", color=0x2f3136)
                                ers.set_thumbnail(url=f'{frendlis[3]}')
                                try:
                                    await useri1.send(embed=ers) 
                                except:
                                    pass
                        else:
                            er=nextcord.Embed(description="Данный участник не состоит в вашем клане", color=0x2f3136)
                            er.set_thumbnail(url=interaction.user.display_avatar)
                            await aa.edit(embed=er) 

            @nextcord.ui.button(label = 'Нет', style = nextcord.ButtonStyle.red, disabled=False)
            async def nimes(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                await aa.delete()
        
        class Del(nextcord.ui.View):
            def __init__(self):
                super().__init__(timeout=120)

            @nextcord.ui.button(label = 'Да', style = nextcord.ButtonStyle.green, disabled=False)
            async def nimess(self, button: nextcord.ui.Button, interaction: nextcord.Interaction): 
                c.execute(f"UPDATE user SET owner_club=0 where owner_club={interaction.user.id}")    
                c.execute(f"DELETE FROM clan where owner = {interaction.user.id}")
                c_db.commit()

                er=nextcord.Embed(description=f"Вы успешно **удалили** свой клан", color=0x2f3136)
                er.set_thumbnail(url=interaction.user.display_avatar)
                await fk.edit(embed=er, view=None) 
                           

            @nextcord.ui.button(label = 'Нет', style = nextcord.ButtonStyle.red, disabled=False)
            async def nimes(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                await fk.delete()

        class edit(nextcord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                
            for supers in c.execute(f"SELECT lvl FROM clan where owner = {interaction.user.id}"):
                if supers[0] == 0:
                    @nextcord.ui.button(emoji = '🧺', label = 'Изменить имя', style = nextcord.ButtonStyle.gray, disabled=False)
                    async def nime(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            for curver in ec.execute(f"SELECT bal FROM balance where id = {interaction.user.id}"):
                                if curver[0] < 2000:
                                    embed = nextcord.Embed(description = f'Данная функция платная, стоимость: **{settings["name_club_cena"]}** {t1}', color=0x2f3136)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)
                                else:
                                    await interaction.response.send_modal(kivisik())
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)


                    @nextcord.ui.button(emoji = '🧺', label = 'Изменить аватар', style = nextcord.ButtonStyle.gray, disabled=True)
                    async def avas(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        pass

                    @nextcord.ui.button(emoji = '🧺', label = 'Добавить заместителя', style = nextcord.ButtonStyle.gray, disabled=True)
                    async def zams(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        pass

                    @nextcord.ui.button(emoji = '🧺', label = 'Убрать заместителя', style = nextcord.ButtonStyle.gray, disabled=True)
                    async def zam1sa(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        pass

                    @nextcord.ui.button(emoji = '🧺', label = 'Передать главу', style = nextcord.ButtonStyle.gray, disabled=False, row = True)
                    async def zam1(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            er=nextcord.Embed(description="Укажи **человека** или его **id** которому хочешь передать главу", color=0x2f3136)
                            er.set_thumbnail(url=interaction.user.display_avatar)
                            ssf = await interaction.send(embed=er, ephemeral = True)
                            try:
                                msg = await bot.wait_for('message', check=lambda m: m.author.id == interaction.user.id, timeout = 30)
                                s = msg.content
                                member = re.sub("[<@>]","",s) 
                            except asyncio.exceptions.TimeoutError:
                                er=nextcord.Embed(description="Вы не успели ввести пользователя, поэтому действии команды были отменены", color=0x2f3136)
                                er.set_thumbnail(url=interaction.user.display_avatar)
                                await interaction.send(embed=er, ephemeral=True)
                            try:
                                global useri1
                                useri1 = interaction.guild.get_member(int(member))
                                if useri1.id == interaction.user.id:
                                    er=nextcord.Embed(description="Ты не можешь указать себя", color=0x2f3136)
                                    er.set_thumbnail(url=interaction.user.display_avatar)
                                    await interaction.send(embed=er, ephemeral = True)
                                else:
                                    for frendlis in c.execute(f"SELECT co_owner1, co_owner2, name, avatar, co_owner_count, owner FROM clan where owner={interaction.user.id}"):
                                        for frs in c.execute(f"SELECT owner_club FROM user where id={useri1.id}"):
                                            if frs[0] == interaction.user.id:
                                                er=nextcord.Embed(description=f"Вы правда хотите передать главу {useri1.mention}?", color=0x2f3136)
                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                global aa
                                                aa = await interaction.send(embed=er, ephemeral=True, view = Trues())  
                                                await msg.delete()
                                            else:
                                                er=nextcord.Embed(description="Данный участник не состоит в вашем клане", color=0x2f3136)
                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                await interaction.send(embed=er, ephemeral=True)  
                                                await msg.delete()        
                            except:
                                er=nextcord.Embed(description="Эй, ты неправильно указал пользователя", color=0x2f3136)
                                er.set_thumbnail(url=interaction.user.display_avatar)
                                await interaction.send(embed=er, ephemeral=True) 
                                await msg.delete()   
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)

                    @nextcord.ui.button(emoji = '🧺', label = 'Поднять уровень', style = nextcord.ButtonStyle.gray, disabled=False, row=True)
                    async def lvlup(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            for supers in c.execute(f"SELECT lvl, balance FROM clan where owner = {interaction.user.id}"):
                                if supers[0] == 0:
                                    if supers[1] < 6000:
                                        embed = nextcord.Embed(description = f'У вас **недостаточно средств клана**, для повышения лвла требуется взнос в размере: **6000**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                    else:
                                        c.execute(f"UPDATE clan SET lvl=1 where owner={interaction.user.id}")
                                        c.execute(f"UPDATE clan SET max_members=25 where owner={interaction.user.id}")
                                        c_db.commit()

                                        embed = nextcord.Embed(description = f'Вы успешно **повысили уровень клана до 1-вого**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                elif supers[0] == 1:
                                    if supers[1] < 10000:
                                        embed = nextcord.Embed(description = f'У вас **недостаточно средств клана**, для повышения лвла требуется взнос в размере: **10000**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                    else:
                                        c.execute(f"UPDATE clan SET lvl=2 where owner={interaction.user.id}")
                                        c.execute(f"UPDATE clan SET max_members=35 where owner={interaction.user.id}")
                                        c_db.commit()

                                        embed = nextcord.Embed(description = f'Вы успешно **повысили уровень клана до 2-рого**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                elif supers[0] == 2:
                                    if supers[1] < 15000:
                                        embed = nextcord.Embed(description = f'У вас **недостаточно средств клана**, для повышения лвла требуется взнос в размере: **15000**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                    else:
                                        c.execute(f"UPDATE clan SET lvl=3 where owner={interaction.user.id}")
                                        c.execute(f"UPDATE clan SET max_members=50 where owner={interaction.user.id}")
                                        c_db.commit()

                                        embed = nextcord.Embed(description = f'Вы успешно **повысили уровень клана до 3-тьего**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                elif supers[0] == 3:
                                    embed = nextcord.Embed(description = f'У вас достигнут **максимальный уровень клана**', color=0x2f3136)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                    
                    @nextcord.ui.button(emoji = '🧺', label = 'Удалить', style = nextcord.ButtonStyle.grey, disabled=False, row=True)
                    async def delete(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            embed = nextcord.Embed(description = f'Вы **уверены** в том что хотите **удалить** клан?', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            global fk    
                            fk = await interaction.send(embed=embed, ephemeral= True, view=Del())
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)

                elif supers[0] == 1:

                    @nextcord.ui.button(emoji = '🧺', label = 'Изменить имя', style = nextcord.ButtonStyle.gray, disabled=False)
                    async def nime(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            for curver in ec.execute(f"SELECT bal FROM balance where id = {interaction.user.id}"):
                                if curver[0] < 2000:
                                    embed = nextcord.Embed(description = f'Данная функция платная, стоимость: **{settings["name_club_cena"]}** {t1}', color=0x2f3136)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)
                                else:
                                    await interaction.response.send_modal(kivisik())
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)

                    @nextcord.ui.button(emoji = '🧺', label = 'Изменить аватар', style = nextcord.ButtonStyle.gray, disabled=False)
                    async def ava(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            for curver in c.execute(f"SELECT lvl FROM clan where owner = {interaction.user.id}"): 
                                if curver[0] < 1:
                                    embed = nextcord.Embed(description = f'Для изменения аватара, нужен 1 уровень клана', color=0x2f3136)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)
                                else:
                                    await interaction.response.send_modal(kivisi())
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                    
                    @nextcord.ui.button(emoji = '🧺', label = 'Добавить заместителя', style = nextcord.ButtonStyle.gray, disabled=True)
                    async def zams(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        pass

                    @nextcord.ui.button(emoji = '🧺', label = 'Убрать заместителя', style = nextcord.ButtonStyle.gray, disabled=True)
                    async def zam1sa(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        pass

                    @nextcord.ui.button(emoji = '🧺', label = 'Передать главу', style = nextcord.ButtonStyle.gray, disabled=False, row = True)
                    async def zam1(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            er=nextcord.Embed(description="Укажи **человека** или его **id** которому хочешь передать главу", color=0x2f3136)
                            er.set_thumbnail(url=interaction.user.display_avatar)
                            ssf = await interaction.send(embed=er, ephemeral = True)
                            try:
                                msg = await bot.wait_for('message', check=lambda m: m.author.id == interaction.user.id, timeout = 30)
                                s = msg.content
                                member = re.sub("[<@>]","",s) 
                            except asyncio.exceptions.TimeoutError:
                                er=nextcord.Embed(description="Вы не успели ввести пользователя, поэтому действии команды были отменены", color=0x2f3136)
                                er.set_thumbnail(url=interaction.user.display_avatar)
                                await interaction.send(embed=er, ephemeral=True)
                            try:
                                global useri1
                                useri1 = interaction.guild.get_member(int(member))
                                if useri1.id == interaction.user.id:
                                    er=nextcord.Embed(description="Ты не можешь указать себя", color=0x2f3136)
                                    er.set_thumbnail(url=interaction.user.display_avatar)
                                    await interaction.send(embed=er, ephemeral = True)
                                else:
                                    for frendlis in c.execute(f"SELECT co_owner1, co_owner2, name, avatar, co_owner_count, owner FROM clan where owner={interaction.user.id}"):
                                        for frs in c.execute(f"SELECT owner_club FROM user where id={useri1.id}"):
                                            if frs[0] == interaction.user.id:
                                                er=nextcord.Embed(description=f"Вы правда хотите передать главу {useri1.mention}?", color=0x2f3136)
                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                global aa
                                                aa = await interaction.send(embed=er, ephemeral=True, view = Trues())  
                                                await msg.delete()
                                            else:
                                                er=nextcord.Embed(description="Данный участник не состоит в вашем клане", color=0x2f3136)
                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                await interaction.send(embed=er, ephemeral=True)  
                                                await msg.delete()        
                            except:
                                er=nextcord.Embed(description="Эй, ты неправильно указал пользователя", color=0x2f3136)
                                er.set_thumbnail(url=interaction.user.display_avatar)
                                await interaction.send(embed=er, ephemeral=True) 
                                await msg.delete()   
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)

                    @nextcord.ui.button(emoji = '🧺', label = 'Поднять уровень', style = nextcord.ButtonStyle.gray, disabled=False, row=True)
                    async def lvlup(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            for supers in c.execute(f"SELECT lvl, balance FROM clan where owner = {interaction.user.id}"):
                                if supers[0] == 0:
                                    if supers[1] < 6000:
                                        embed = nextcord.Embed(description = f'У вас **недостаточно средств клана**, для повышения лвла требуется взнос в размере: **6000**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                    else:
                                        c.execute(f"UPDATE clan SET lvl=1 where owner={interaction.user.id}")
                                        c.execute(f"UPDATE clan SET max_members=25 where owner={interaction.user.id}")
                                        c_db.commit()

                                        embed = nextcord.Embed(description = f'Вы успешно **повысили уровень клана до 1-вого**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                elif supers[0] == 1:
                                    if supers[1] < 10000:
                                        embed = nextcord.Embed(description = f'У вас **недостаточно средств клана**, для повышения лвла требуется взнос в размере: **10000**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                    else:
                                        c.execute(f"UPDATE clan SET lvl=2 where owner={interaction.user.id}")
                                        c.execute(f"UPDATE clan SET max_members=35 where owner={interaction.user.id}")
                                        c_db.commit()

                                        embed = nextcord.Embed(description = f'Вы успешно **повысили уровень клана до 2-рого**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                elif supers[0] == 2:
                                    if supers[1] < 15000:
                                        embed = nextcord.Embed(description = f'У вас **недостаточно средств клана**, для повышения лвла требуется взнос в размере: **15000**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                    else:
                                        c.execute(f"UPDATE clan SET lvl=3 where owner={interaction.user.id}")
                                        c.execute(f"UPDATE clan SET max_members=50 where owner={interaction.user.id}")
                                        c_db.commit()

                                        embed = nextcord.Embed(description = f'Вы успешно **повысили уровень клана до 3-тьего**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                elif supers[0] == 3:
                                    embed = nextcord.Embed(description = f'У вас достигнут **максимальный уровень клана**', color=0x2f3136)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                    
                    @nextcord.ui.button(emoji = '🧺', label = 'Удалить', style = nextcord.ButtonStyle.grey, disabled=False, row=True)
                    async def delete(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            embed = nextcord.Embed(description = f'Вы **уверены** в том что хотите **удалить** клан?', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            global fk    
                            fk = await interaction.send(embed=embed, ephemeral= True, view=Del())
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                
                elif supers[0] == 2:
                    
                    @nextcord.ui.button(emoji = '🧺', label = 'Изменить имя', style = nextcord.ButtonStyle.gray, disabled=False)
                    async def nime(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            for curver in ec.execute(f"SELECT bal FROM balance where id = {interaction.user.id}"):
                                if curver[0] < 2000:
                                    embed = nextcord.Embed(description = f'Данная функция платная, стоимость: **{settings["name_club_cena"]}** {t1}', color=0x2f3136)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)
                                else:
                                    await interaction.response.send_modal(kivisik())
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)

                    @nextcord.ui.button(emoji = '🧺', label = 'Изменить аватар', style = nextcord.ButtonStyle.gray, disabled=False)
                    async def ava(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            for curver in c.execute(f"SELECT lvl FROM clan where owner = {interaction.user.id}"): 
                                if curver[0] < 1:
                                    embed = nextcord.Embed(description = f'Для изменения аватара, нужен 1 уровень клана', color=0x2f3136)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)
                                else:
                                    await interaction.response.send_modal(kivisi())
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                
    
                    @nextcord.ui.button(emoji = '🧺', label = 'Добавить заместителя', style = nextcord.ButtonStyle.gray, disabled=False)
                    async def zam(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            for hik in c.execute(f"SELECT co_owner_count FROM clan where owner = {interaction.user.id}"):
                                if hik[0] == 2:
                                    embed = nextcord.Embed(description = f'Что бы добавить заместителя снимите прежних', color=0x2f3136)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)
                                else:
                                    er=nextcord.Embed(description="Укажи **человека** или его **id** которого хочешь повысить до зама", color=0x2f3136)
                                    er.set_thumbnail(url=interaction.user.display_avatar)
                                    ssf = await interaction.send(embed=er, ephemeral = True)
                                    try:
                                        msg = await bot.wait_for('message', check=lambda m: m.author.id == interaction.user.id, timeout = 30)
                                        s = msg.content
                                        member = re.sub("[<@>]","",s) 
                                    except asyncio.exceptions.TimeoutError:
                                        er=nextcord.Embed(description="Вы не успели ввести пользователя, поэтому действии команды были отменены", color=0x2f3136)
                                        er.set_thumbnail(url=interaction.user.display_avatar)
                                        await interaction.send(embed=er)
                                    try:
                                        useri1 = interaction.guild.get_member(int(member))
                                        if useri1.id == interaction.user.id:
                                            er=nextcord.Embed(description="Ты не можешь указать себя", color=0x2f3136)
                                            er.set_thumbnail(url=interaction.user.display_avatar)
                                            await interaction.send(embed=er, ephemeral = True)
                                        else:
                                            for frendlis in c.execute(f"SELECT co_owner1, co_owner2, name, avatar, co_owner_count FROM clan where owner={interaction.user.id}"):
                                                for frs in c.execute(f"SELECT owner_club FROM user where id={useri1.id}"):
                                                    if frs[0] == interaction.user.id:
                                                        if frendlis[0] == 'None':
                                                            c.execute(f"UPDATE clan SET co_owner_count={frendlis[4] + 1} where owner={interaction.user.id}")
                                                            c.execute(f"UPDATE clan SET co_owner1={useri1.id} where owner={interaction.user.id}")
                                                            c_db.commit()

                                                            er=nextcord.Embed(description=f"Вы успешно добавили {useri1.mention} на заместителя", color=0x2f3136)
                                                            er.set_thumbnail(url=interaction.user.display_avatar)
                                                            await interaction.send(embed=er, ephemeral=True)

                                                            er1=nextcord.Embed(description=f"Вы были повышены на заместителя в клане: **{frendlis[2]}**", color=0x2f3136)
                                                            er1.set_thumbnail(url=interaction.user.display_avatar)
                                                            try:
                                                                await useri1.send(embed=er1)
                                                            except:
                                                                pass

                                                            await msg.delete()

                                                        elif frendlis[0] > 1 and frendlis[1] == 'None':
                                                            if useri1.id == frendlis[0]:
                                                                er=nextcord.Embed(description="Данный участник уже стоит на заместителе", color=0x2f3136)
                                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                                await interaction.send(embed=er, ephemeral = True)
                                                            else:
                                                                c.execute(f"UPDATE clan SET co_owner_count={frendlis[4] + 1} where owner={interaction.user.id}")
                                                                c.execute(f"UPDATE clan SET co_owner2={useri1.id} where owner={interaction.user.id}")
                                                                c_db.commit()

                                                                er=nextcord.Embed(description=f"Вы успешно добавили {useri1.mention} на заместителя", color=0x2f3136)
                                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                                await interaction.send(embed=er, ephemeral=True)

                                                                er1=nextcord.Embed(description=f"Вы были повышены на заместителя в клане: **{frendlis[2]}**", color=0x2f3136)
                                                                er1.set_thumbnail(url=interaction.user.display_avatar)
                                                                try:
                                                                    await useri1.send(embed=er1)
                                                                except:
                                                                    pass

                                                                await msg.delete()
                                                    else:
                                                        er=nextcord.Embed(description="Данный участник не состоит в вашем клане", color=0x2f3136)
                                                        er.set_thumbnail(url=interaction.user.display_avatar)
                                                        await interaction.send(embed=er, ephemeral=True)  
                                                        await msg.delete()        
                                    except:
                                        er=nextcord.Embed(description="Эй, ты неправильно указал пользователя", color=0x2f3136)
                                        er.set_thumbnail(url=interaction.user.display_avatar)
                                        await interaction.send(embed=er, ephemeral=True) 
                                        await msg.delete()   
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)

                

                    @nextcord.ui.button(emoji = '🧺', label = 'Убрать заместителя', style = nextcord.ButtonStyle.gray, disabled=False)
                    async def zam1s(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            for hik in c.execute(f"SELECT co_owner_count FROM clan where owner = {interaction.user.id}"):
                                if hik[0] == 0:
                                    embed = nextcord.Embed(description = f'У вас нет заместителей', color=0x2f3136)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)
                                else:
                                    er=nextcord.Embed(description="Укажи **человека** или его **id** которого хочешь снять с зама", color=0x2f3136)
                                    er.set_thumbnail(url=interaction.user.display_avatar)
                                    ssf = await interaction.send(embed=er, ephemeral = True)
                                    try:
                                        msg = await bot.wait_for('message', check=lambda m: m.author.id == interaction.user.id, timeout = 30)
                                        s = msg.content
                                        member = re.sub("[<@>]","",s) 
                                    except asyncio.exceptions.TimeoutError:
                                        er=nextcord.Embed(description="Вы не успели ввести пользователя, поэтому действии команды были отменены", color=0x2f3136)
                                        er.set_thumbnail(url=interaction.user.display_avatar)
                                        await interaction.send(embed=er)
                                    try:
                                        useri1 = interaction.guild.get_member(int(member))
                                        if useri1.id == interaction.user.id:
                                            er=nextcord.Embed(description="Ты не можешь указать себя", color=0x2f3136)
                                            er.set_thumbnail(url=interaction.user.display_avatar)
                                            await interaction.send(embed=er, ephemeral = True)
                                        else:
                                            for frendlis in c.execute(f"SELECT co_owner1, co_owner2, name, avatar, co_owner_count FROM clan where owner={interaction.user.id}"):
                                                for frs in c.execute(f"SELECT owner_club FROM user where id={useri1.id}"):
                                                    if frs[0] == interaction.user.id:
                                                        if frendlis[0] == useri1.id:
                                                            c.execute(f"UPDATE clan SET co_owner_count={frendlis[4] - 1} where owner={interaction.user.id}")
                                                            c.execute(f"UPDATE clan SET co_owner1='None' where owner={interaction.user.id}")
                                                            c_db.commit()

                                                            er=nextcord.Embed(description=f"Вы успешно сняли {useri1.mention} с заместителя", color=0x2f3136)
                                                            er.set_thumbnail(url=interaction.user.display_avatar)
                                                            await interaction.send(embed=er, ephemeral=True)

                                                            er1=nextcord.Embed(description=f"Вы были сняты с заместителя в клане: **{frendlis[2]}**", color=0x2f3136)
                                                            er1.set_thumbnail(url=interaction.user.display_avatar)
                                                            try:
                                                                await useri1.send(embed=er1)
                                                            except:
                                                                pass

                                                            await msg.delete()

                                                        elif frendlis[1] == useri1.id:
                                                            c.execute(f"UPDATE clan SET co_owner_count={frendlis[4] - 1} where owner={interaction.user.id}")
                                                            c.execute(f"UPDATE clan SET co_owner2='None' where owner={interaction.user.id}")
                                                            c_db.commit()

                                                            er=nextcord.Embed(description=f"Вы успешно сняли {useri1.mention} с заместителя", color=0x2f3136)
                                                            er.set_thumbnail(url=interaction.user.display_avatar)
                                                            await interaction.send(embed=er, ephemeral=True)

                                                            er1=nextcord.Embed(description=f"Вы были сняты с заместителя в клане: **{frendlis[2]}**", color=0x2f3136)
                                                            er1.set_thumbnail(url=interaction.user.display_avatar)
                                                            try:
                                                                await useri1.send(embed=er1)
                                                            except:
                                                                pass

                                                            await msg.delete()
                                                        else:
                                                            er=nextcord.Embed(description="Данный участник не состоит заместителем в вашем клане", color=0x2f3136)
                                                            er.set_thumbnail(url=interaction.user.display_avatar)
                                                            await interaction.send(embed=er, ephemeral=True)  
                                                            await msg.delete()   
                                                    else:
                                                        er=nextcord.Embed(description="Данный участник не состоит в вашем клане", color=0x2f3136)
                                                        er.set_thumbnail(url=interaction.user.display_avatar)
                                                        await interaction.send(embed=er, ephemeral=True)  
                                                        await msg.delete()        
                                    except:
                                        er=nextcord.Embed(description="Эй, ты неправильно указал пользователя", color=0x2f3136)
                                        er.set_thumbnail(url=interaction.user.display_avatar)
                                        await interaction.send(embed=er) 
                                        await msg.delete()   
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                    
                    @nextcord.ui.button(emoji = '🧺', label = 'Поднять уровень', style = nextcord.ButtonStyle.gray, disabled=False, row=True)
                    async def lvlup(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            for supers in c.execute(f"SELECT lvl, balance FROM clan where owner = {interaction.user.id}"):
                                if supers[0] == 0:
                                    if supers[1] < 6000:
                                        embed = nextcord.Embed(description = f'У вас **недостаточно средств клана**, для повышения лвла требуется взнос в размере: **6000**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                    else:
                                        c.execute(f"UPDATE clan SET lvl=1 where owner={interaction.user.id}")
                                        c.execute(f"UPDATE clan SET max_members=25 where owner={interaction.user.id}")
                                        c_db.commit()

                                        embed = nextcord.Embed(description = f'Вы успешно **повысили уровень клана до 1-вого**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                elif supers[0] == 1:
                                    if supers[1] < 10000:
                                        embed = nextcord.Embed(description = f'У вас **недостаточно средств клана**, для повышения лвла требуется взнос в размере: **10000**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                    else:
                                        c.execute(f"UPDATE clan SET lvl=2 where owner={interaction.user.id}")
                                        c.execute(f"UPDATE clan SET max_members=35 where owner={interaction.user.id}")
                                        c_db.commit()

                                        embed = nextcord.Embed(description = f'Вы успешно **повысили уровень клана до 2-рого**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                elif supers[0] == 2:
                                    if supers[1] < 15000:
                                        embed = nextcord.Embed(description = f'У вас **недостаточно средств клана**, для повышения лвла требуется взнос в размере: **15000**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                    else:
                                        c.execute(f"UPDATE clan SET lvl=3 where owner={interaction.user.id}")
                                        c.execute(f"UPDATE clan SET max_members=50 where owner={interaction.user.id}")
                                        c_db.commit()

                                        embed = nextcord.Embed(description = f'Вы успешно **повысили уровень клана до 3-тьего**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                elif supers[0] == 3:
                                    embed = nextcord.Embed(description = f'У вас достигнут **максимальный уровень клана**', color=0x2f3136)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                    
                    @nextcord.ui.button(emoji = '🧺', label = 'Удалить клан', style = nextcord.ButtonStyle.grey, disabled=False, row=True)
                    async def delete(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            embed = nextcord.Embed(description = f'Вы **уверены** в том что хотите **удалить** клан?', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            global fk    
                            fk = await interaction.send(embed=embed, ephemeral= True, view=Del())
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
            
                elif supers[0] == 3:
                    @nextcord.ui.button(emoji = '🧺', label = 'Изменить имя', style = nextcord.ButtonStyle.gray, disabled=False)
                    async def nime(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            for curver in ec.execute(f"SELECT bal FROM balance where id = {interaction.user.id}"):
                                if curver[0] < 2000:
                                    embed = nextcord.Embed(description = f'Данная функция платная, стоимость: **{settings["name_club_cena"]}** {t1}', color=0x2f3136)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)
                                else:
                                    await interaction.response.send_modal(kivisik())
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)

                    @nextcord.ui.button(emoji = '🧺', label = 'Изменить аватар', style = nextcord.ButtonStyle.gray, disabled=False)
                    async def ava(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            for curver in c.execute(f"SELECT lvl FROM clan where owner = {interaction.user.id}"): 
                                if curver[0] < 1:
                                    embed = nextcord.Embed(description = f'Для изменения аватара, нужен 1 уровень клана', color=0x2f3136)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)
                                else:
                                    await interaction.response.send_modal(kivisi())
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                
    
                    @nextcord.ui.button(emoji = '🧺', label = 'Добавить заместителя', style = nextcord.ButtonStyle.gray, disabled=False)
                    async def zam(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            for hik in c.execute(f"SELECT co_owner_count FROM clan where owner = {interaction.user.id}"):
                                if hik[0] == 2:
                                    embed = nextcord.Embed(description = f'Что бы добавить заместителя снимите прежних', color=0x2f3136)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)
                                else:
                                    er=nextcord.Embed(description="Укажи **человека** или его **id** которого хочешь повысить до зама", color=0x2f3136)
                                    er.set_thumbnail(url=interaction.user.display_avatar)
                                    ssf = await interaction.send(embed=er, ephemeral = True)
                                    try:
                                        msg = await bot.wait_for('message', check=lambda m: m.author.id == interaction.user.id, timeout = 30)
                                        s = msg.content
                                        member = re.sub("[<@>]","",s) 
                                    except asyncio.exceptions.TimeoutError:
                                        er=nextcord.Embed(description="Вы не успели ввести пользователя, поэтому действии команды были отменены", color=0x2f3136)
                                        er.set_thumbnail(url=interaction.user.display_avatar)
                                        await interaction.send(embed=er)
                                    try:
                                        useri1 = interaction.guild.get_member(int(member))
                                        if useri1.id == interaction.user.id:
                                            er=nextcord.Embed(description="Ты не можешь указать себя", color=0x2f3136)
                                            er.set_thumbnail(url=interaction.user.display_avatar)
                                            await interaction.send(embed=er, ephemeral = True)
                                        else:
                                            for frendlis in c.execute(f"SELECT co_owner1, co_owner2, name, avatar, co_owner_count FROM clan where owner={interaction.user.id}"):
                                                for frs in c.execute(f"SELECT owner_club FROM user where id={useri1.id}"):
                                                    if frs[0] == interaction.user.id:
                                                        if frendlis[0] == 'None':
                                                            c.execute(f"UPDATE clan SET co_owner_count={frendlis[4] + 1} where owner={interaction.user.id}")
                                                            c.execute(f"UPDATE clan SET co_owner1={useri1.id} where owner={interaction.user.id}")
                                                            c_db.commit()

                                                            er=nextcord.Embed(description=f"Вы успешно добавили {useri1.mention} на заместителя", color=0x2f3136)
                                                            er.set_thumbnail(url=interaction.user.display_avatar)
                                                            await interaction.send(embed=er, ephemeral=True)

                                                            er1=nextcord.Embed(description=f"Вы были повышены на заместителя в клане: **{frendlis[2]}**", color=0x2f3136)
                                                            er1.set_thumbnail(url=interaction.user.display_avatar)
                                                            try:
                                                                await useri1.send(embed=er1)
                                                            except:
                                                                pass

                                                            await msg.delete()

                                                        elif frendlis[0] > 1 and frendlis[1] == 'None':
                                                            if useri1.id == frendlis[0]:
                                                                er=nextcord.Embed(description="Данный участник уже стоит на заместителе", color=0x2f3136)
                                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                                await interaction.send(embed=er, ephemeral = True)
                                                            else:
                                                                c.execute(f"UPDATE clan SET co_owner_count={frendlis[4] + 1} where owner={interaction.user.id}")
                                                                c.execute(f"UPDATE clan SET co_owner2={useri1.id} where owner={interaction.user.id}")
                                                                c_db.commit()

                                                                er=nextcord.Embed(description=f"Вы успешно добавили {useri1.mention} на заместителя", color=0x2f3136)
                                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                                await interaction.send(embed=er, ephemeral=True)

                                                                er1=nextcord.Embed(description=f"Вы были повышены на заместителя в клане: **{frendlis[2]}**", color=0x2f3136)
                                                                er1.set_thumbnail(url=interaction.user.display_avatar)
                                                                try:
                                                                    await useri1.send(embed=er1)
                                                                except:
                                                                    pass

                                                                await msg.delete()
                                                    else:
                                                        er=nextcord.Embed(description="Данный участник не состоит в вашем клане", color=0x2f3136)
                                                        er.set_thumbnail(url=interaction.user.display_avatar)
                                                        await interaction.send(embed=er, ephemeral=True)  
                                                        await msg.delete()        
                                    except:
                                        er=nextcord.Embed(description="Эй, ты неправильно указал пользователя", color=0x2f3136)
                                        er.set_thumbnail(url=interaction.user.display_avatar)
                                        await interaction.send(embed=er, ephemeral=True) 
                                        await msg.delete()   
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)

                

                    @nextcord.ui.button(emoji = '🧺', label = 'Убрать заместителя', style = nextcord.ButtonStyle.gray, disabled=False)
                    async def zam1s(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            for hik in c.execute(f"SELECT co_owner_count FROM clan where owner = {interaction.user.id}"):
                                if hik[0] == 0:
                                    embed = nextcord.Embed(description = f'У вас нет заместителей', color=0x2f3136)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)
                                else:
                                    er=nextcord.Embed(description="Укажи **человека** или его **id** которого хочешь снять с зама", color=0x2f3136)
                                    er.set_thumbnail(url=interaction.user.display_avatar)
                                    ssf = await interaction.send(embed=er, ephemeral = True)
                                    try:
                                        msg = await bot.wait_for('message', check=lambda m: m.author.id == interaction.user.id, timeout = 30)
                                        s = msg.content
                                        member = re.sub("[<@>]","",s) 
                                    except asyncio.exceptions.TimeoutError:
                                        er=nextcord.Embed(description="Вы не успели ввести пользователя, поэтому действии команды были отменены", color=0x2f3136)
                                        er.set_thumbnail(url=interaction.user.display_avatar)
                                        await interaction.send(embed=er)
                                    try:
                                        useri1 = interaction.guild.get_member(int(member))
                                        if useri1.id == interaction.user.id:
                                            er=nextcord.Embed(description="Ты не можешь указать себя", color=0x2f3136)
                                            er.set_thumbnail(url=interaction.user.display_avatar)
                                            await interaction.send(embed=er, ephemeral = True)
                                        else:
                                            for frendlis in c.execute(f"SELECT co_owner1, co_owner2, name, avatar, co_owner_count FROM clan where owner={interaction.user.id}"):
                                                for frs in c.execute(f"SELECT owner_club FROM user where id={useri1.id}"):
                                                    if frs[0] == interaction.user.id:
                                                        if frendlis[0] == useri1.id:
                                                            c.execute(f"UPDATE clan SET co_owner_count={frendlis[4] - 1} where owner={interaction.user.id}")
                                                            c.execute(f"UPDATE clan SET co_owner1='None' where owner={interaction.user.id}")
                                                            c_db.commit()

                                                            er=nextcord.Embed(description=f"Вы успешно сняли {useri1.mention} с заместителя", color=0x2f3136)
                                                            er.set_thumbnail(url=interaction.user.display_avatar)
                                                            await interaction.send(embed=er, ephemeral=True)

                                                            er1=nextcord.Embed(description=f"Вы были сняты с заместителя в клане: **{frendlis[2]}**", color=0x2f3136)
                                                            er1.set_thumbnail(url=interaction.user.display_avatar)
                                                            try:
                                                                await useri1.send(embed=er1)
                                                            except:
                                                                pass

                                                            await msg.delete()

                                                        elif frendlis[1] == useri1.id:
                                                            c.execute(f"UPDATE clan SET co_owner_count={frendlis[4] - 1} where owner={interaction.user.id}")
                                                            c.execute(f"UPDATE clan SET co_owner2='None' where owner={interaction.user.id}")
                                                            c_db.commit()

                                                            er=nextcord.Embed(description=f"Вы успешно сняли {useri1.mention} с заместителя", color=0x2f3136)
                                                            er.set_thumbnail(url=interaction.user.display_avatar)
                                                            await interaction.send(embed=er, ephemeral=True)

                                                            er1=nextcord.Embed(description=f"Вы были сняты с заместителя в клане: **{frendlis[2]}**", color=0x2f3136)
                                                            er1.set_thumbnail(url=interaction.user.display_avatar)
                                                            try:
                                                                await useri1.send(embed=er1)
                                                            except:
                                                                pass

                                                            await msg.delete()
                                                        else:
                                                            er=nextcord.Embed(description="Данный участник не состоит заместителем в вашем клане", color=0x2f3136)
                                                            er.set_thumbnail(url=interaction.user.display_avatar)
                                                            await interaction.send(embed=er, ephemeral=True)  
                                                            await msg.delete()   
                                                    else:
                                                        er=nextcord.Embed(description="Данный участник не состоит в вашем клане", color=0x2f3136)
                                                        er.set_thumbnail(url=interaction.user.display_avatar)
                                                        await interaction.send(embed=er, ephemeral=True)  
                                                        await msg.delete()        
                                    except:
                                        er=nextcord.Embed(description="Эй, ты неправильно указал пользователя", color=0x2f3136)
                                        er.set_thumbnail(url=interaction.user.display_avatar)
                                        await interaction.send(embed=er) 
                                        await msg.delete()   
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                    
                    @nextcord.ui.button(emoji = '🧺', label = 'Передать главу', style = nextcord.ButtonStyle.gray, disabled=False, row = True)
                    async def zam1(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            er=nextcord.Embed(description="Укажи **человека** или его **id** которому хочешь передать главу", color=0x2f3136)
                            er.set_thumbnail(url=interaction.user.display_avatar)
                            ssf = await interaction.send(embed=er, ephemeral = True)
                            try:
                                msg = await bot.wait_for('message', check=lambda m: m.author.id == interaction.user.id, timeout = 30)
                                s = msg.content
                                member = re.sub("[<@>]","",s) 
                            except asyncio.exceptions.TimeoutError:
                                er=nextcord.Embed(description="Вы не успели ввести пользователя, поэтому действии команды были отменены", color=0x2f3136)
                                er.set_thumbnail(url=interaction.user.display_avatar)
                                await interaction.send(embed=er, ephemeral=True)
                            try:
                                global useri1
                                useri1 = interaction.guild.get_member(int(member))
                                if useri1.id == interaction.user.id:
                                    er=nextcord.Embed(description="Ты не можешь указать себя", color=0x2f3136)
                                    er.set_thumbnail(url=interaction.user.display_avatar)
                                    await interaction.send(embed=er, ephemeral = True)
                                else:
                                    for frendlis in c.execute(f"SELECT co_owner1, co_owner2, name, avatar, co_owner_count, owner FROM clan where owner={interaction.user.id}"):
                                        for frs in c.execute(f"SELECT owner_club FROM user where id={useri1.id}"):
                                            if frs[0] == interaction.user.id:
                                                er=nextcord.Embed(description=f"Вы правда хотите передать главу {useri1.mention}?", color=0x2f3136)
                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                global aa
                                                aa = await interaction.send(embed=er, ephemeral=True, view = Trues())  
                                                await msg.delete()
                                            else:
                                                er=nextcord.Embed(description="Данный участник не состоит в вашем клане", color=0x2f3136)
                                                er.set_thumbnail(url=interaction.user.display_avatar)
                                                await interaction.send(embed=er, ephemeral=True)  
                                                await msg.delete()        
                            except:
                                er=nextcord.Embed(description="Эй, ты неправильно указал пользователя", color=0x2f3136)
                                er.set_thumbnail(url=interaction.user.display_avatar)
                                await interaction.send(embed=er, ephemeral=True) 
                                await msg.delete()   
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                    
                    @nextcord.ui.button(emoji = '🧺', label = 'Поднять уровень', style = nextcord.ButtonStyle.gray, disabled=False, row=True)
                    async def lvlup(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            for supers in c.execute(f"SELECT lvl, balance FROM clan where owner = {interaction.user.id}"):
                                if supers[0] == 0:
                                    if supers[1] < 6000:
                                        embed = nextcord.Embed(description = f'У вас **недостаточно средств клана**, для повышения лвла требуется взнос в размере: **6000**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                    else:
                                        c.execute(f"UPDATE clan SET lvl=1 where owner={interaction.user.id}")
                                        c.execute(f"UPDATE clan SET max_members=25 where owner={interaction.user.id}")
                                        c_db.commit()

                                        embed = nextcord.Embed(description = f'Вы успешно **повысили уровень клана до 1-вого**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                elif supers[0] == 1:
                                    if supers[1] < 10000:
                                        embed = nextcord.Embed(description = f'У вас **недостаточно средств клана**, для повышения лвла требуется взнос в размере: **10000**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                    else:
                                        c.execute(f"UPDATE clan SET lvl=2 where owner={interaction.user.id}")
                                        c.execute(f"UPDATE clan SET max_members=35 where owner={interaction.user.id}")
                                        c_db.commit()

                                        embed = nextcord.Embed(description = f'Вы успешно **повысили уровень клана до 2-рого**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                elif supers[0] == 2:
                                    if supers[1] < 15000:
                                        embed = nextcord.Embed(description = f'У вас **недостаточно средств клана**, для повышения лвла требуется взнос в размере: **15000**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                    else:
                                        c.execute(f"UPDATE clan SET lvl=3 where owner={interaction.user.id}")
                                        c.execute(f"UPDATE clan SET max_members=50 where owner={interaction.user.id}")
                                        c_db.commit()

                                        embed = nextcord.Embed(description = f'Вы успешно **повысили уровень клана до 3-тьего**', color=0x2f3136)
                                        embed.set_thumbnail(url=interaction.user.display_avatar)       
                                        await interaction.send(embed=embed, ephemeral= True)
                                elif supers[0] == 3:
                                    embed = nextcord.Embed(description = f'У вас достигнут **максимальный уровень клана**', color=0x2f3136)
                                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                                    await interaction.send(embed=embed, ephemeral= True)
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
                    
                    @nextcord.ui.button(emoji = '🧺', label = 'Удалить', style = nextcord.ButtonStyle.grey, disabled=False, row=True)
                    async def delete(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if author.id == interaction.user.id:
                            embed = nextcord.Embed(description = f'Вы **уверены** в том что хотите **удалить** клан?', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)   
                            global fk    
                            fk = await interaction.send(embed=embed, ephemeral= True, view=Del())
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2f3136)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)
            
            


        for bibi in c.execute(f"SELECT id, owner_club FROM user where id={interaction.user.id}"):
            for bibis in c.execute(f"SELECT avatar, name, datecreate FROM clan where owner={bibi[1]}"):
                if bibi[0] == bibi[1]:
                    embed = nextcord.Embed(title = f'{bibis[1]}', description = f'> Здесь расположены инструменты для редактирования клана.', color=0x2f3136)
                    embed.add_field(name='・дата создания:', value=f'```{bibis[2]}```', inline=False)
                    embed.set_thumbnail(url=f'{bibis[0]}')       
                    global jorj
                    jorj = await interaction.send(embed=embed, view=edit())
                else:
                    embed = nextcord.Embed(description = f'Вы не являетесь создателем клана, поэтому видите данное сообщение', color=0x2f3136)
                    embed.set_thumbnail(url=interaction.user.display_avatar)       
                    await interaction.send(embed=embed, ephemeral= True)
                                 
                   
def setup(bot):
    bot.add_cog(clan1(bot))
