import nextcord
from nextcord.ext import commands
from nextcord.ext import tasks
from datetime import datetime, date, time, timedelta
from config import *
import sqlite3


task_db = sqlite3.connect('database/tasks.db', timeout=10)
task = task_db.cursor()

ec_db = sqlite3.connect('database/economy.db', timeout=10)
ec = ec_db.cursor() 

mr_db = sqlite3.connect('database/marry.db', timeout=10)
mr = mr_db.cursor()

class void_update(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.channel = 907212184537419818
        self.text = 'Text'
        

    @tasks.loop(seconds=1)
    async def role(self):
        cost = int(settings['cost_role'])
        guild = self.bot.get_guild(int(settings["Guild_ID"]))
        bloop = datetime.now().timestamp()
        task.execute(f"SELECT date, id FROM tasks WHERE name = 'role'")
        for row in task.fetchall():
            member = guild.get_member(int(row[1]))
            if member is None:
                pass
            else: 
                if row[0] <= bloop:
                    if ec.execute(f"SELECT auto FROM role where id={member.id} and guild_id={guild.id}").fetchone()[0] == 'on':
                        for bal in ec.execute(f'SELECT bal FROM balance where id={member.id} and guild_id={guild.id}'):

                            if bal[0] < cost:

                                task.execute(f"DELETE FROM tasks where id={member.id} and guild_id = {guild.id} and name='role'")
                                task_db.commit()

                                ec.execute(f'UPDATE role SET status = "close" where id={member.id} and guild_id={guild.id}')
                                ec_db.commit()

                                floot = (datetime.now() + timedelta(days=3)).timestamp()
                                
                                task.execute(f"INSERT INTO tasks VALUES ('deleterole','{floot}','{member.id}', '{guild.id}')")
                                task_db.commit()

                                embed=nextcord.Embed(title='Автооплата', description = "У тебя не хватило коинов для продления личной роли. Твой предмет был заблокирован на 3 дня^^\rТы можешь продлить товар вручную через меню управления твоей ролью".format(cost), color=0x2b2d31)
                                await member.send(embed = embed)      
                            else:   

                                bloop = (datetime.now() + timedelta(days=30)).timestamp()
                                task.execute(f'UPDATE tasks SET date = "{bloop}" where id={member.id} and guild_id={guild.id}')
                                task_db.commit()

                                ec.execute(f'UPDATE role SET status = "open" where id={member.id} and guild_id={guild.id}')
                                ec.execute(f'UPDATE balance SET bal={bal[0] - cost}  where id={member.id} and guild_id={guild.id}')
                                ec_db.commit()
                                embed=nextcord.Embed(title='Автооплата', description = f"Твоя личная роль успешно была продлена. \rС твоего баланса было списано {cost}", color=0x2b2d31)
                                embed.set_thumbnail(url=member.display_avatar)
                                await member.send(embed = embed) 
                    else:

                        
                        task.execute(f"DELETE FROM tasks where id={member.id} and guild_id = {guild.id} and name='role'")
                        task_db.commit()

                        ec.execute(f'UPDATE role SET status = "close" where id={member.id} and guild_id={guild.id}')
                        ec_db.commit()

                        floot = (datetime.now() + timedelta(days=3)).timestamp()
                        
                        task.execute(f"INSERT INTO tasks VALUES ('deleterole','{floot}','{member.id}', '{guild.id}')")
                        task_db.commit()

                        embed=nextcord.Embed(title="Ваша личная роль была заблокирована", description='Причина блокировки: `Окончание срока действия товара`', color=0x2b2d31)
                        embed.set_thumbnail(url=member.display_avatar)
                        await member.send(embed=embed)
                else:
                    pass

    @tasks.loop(seconds=1)
    async def delrole(self):
        guild = self.bot.get_guild(int(settings["Guild_ID"]))
        bloop = datetime.now().timestamp()
        task.execute(f"SELECT date, id FROM tasks WHERE name = 'deleterole'")
        for row in task.fetchall():
            if row[0] <= bloop:
                member = guild.get_member(int(row[1]))
                task.execute(f"DELETE FROM tasks where id={member.id} and guild_id = {guild.id} and name='deleterole'")
                task_db.commit()
                for custom in ec.execute(f"SELECT role FROM role where id={member.id} and guild_id = {guild.id}"):
                    role = guild.get_role(int(custom[0]))
                    await role.delete()
                    embed=nextcord.Embed(title="Ваша личная роль была удалена", description='Причина удаления: `Окончание срока действия товара`', color=0x2b2d31)
                    embed.set_thumbnail(url=member.display_avatar)
                    await member.send(embed=embed)
            else:
                pass   

    @tasks.loop(seconds=1)
    async def nonadmission(self):
        guild = self.bot.get_guild(int(settings["Guild_ID"]))

        bloop = datetime.now().timestamp()
        task.execute(f"SELECT date, id FROM tasks WHERE name = 'nonadmission'")
        for row in task.fetchall():
            member = guild.get_member(int(row[1]))
            if member is None:
                pass
            else: 
                if row[0] <= bloop:
                    unf = nextcord.utils.get(guild.roles, id = int(settings['unf']))
                    role = guild.get_role(int(settings["nedopysk"]))
                    await member.remove_roles(role)
                    await member.add_roles(unf)
                    task.execute(f"DELETE FROM tasks where id={member.id} and guild_id = {guild.id} and name='nonadmission'")
                    task_db.commit()
                else:
                    pass

    @tasks.loop(seconds=1)
    async def multiplier(self):
        guild = self.bot.get_guild(int(settings["Guild_ID"]))

        bloop = datetime.now().timestamp()
        task.execute(f"SELECT date, id FROM tasks WHERE name = 'multiplier'")
        for row in task.fetchall():
            member = guild.get_member(int(row[1]))
            if member is None:
                pass
            else: 
                if row[0] <= bloop:
                    ec.execute(f'UPDATE balance SET multiplier = "None"  where id={member.id} and guild_id={guild.id}')
                    task.execute(f"DELETE FROM tasks where id={member.id} and guild_id = {guild.id} and name='multiplier'")
                    task_db.commit()
                    ec_db.commit()


                    try:
                        embed=nextcord.Embed(description="Время действия вашего множителя закончилось", color=0x2b2d31)
                        embed.set_thumbnail(url=member.display_avatar)
                        await member.send(embed=embed)
                    except:
                        pass

                else:
                    pass



    @tasks.loop(seconds=1)
    async def channels(self):
        cost = int(settings['cost_role'])
        guild = self.bot.get_guild(int(settings["Guild_ID"]))
        bloop = datetime.now().timestamp()
        task.execute(f"SELECT date, id FROM tasks WHERE name = 'channel'")
        for row in task.fetchall():
            member = guild.get_member(int(row[1]))
            if member is None:
                print(123)
            else: 
                if row[0] <= bloop:
                    if ec.execute(f"SELECT auto FROM channel where id={member.id} and guild_id={guild.id}").fetchone()[0] == 'on':
                        for bal in ec.execute(f'SELECT bal FROM balance where id={member.id} and guild_id={guild.id}'):

                            if bal[0] < cost:

                                task.execute(f"DELETE FROM tasks where id={member.id} and guild_id = {guild.id} and name='channel'")
                                task_db.commit()

                                ec.execute(f'UPDATE channel SET status = "close" where id={member.id} and guild_id={guild.id}')
                                ec_db.commit()

                                floot = (datetime.now() + timedelta(days=3)).timestamp()
                                
                                task.execute(f"INSERT INTO tasks VALUES ('deletechannel','{floot}','{member.id}', '{guild.id}')")
                                task_db.commit()

                                embed=nextcord.Embed(title='Автооплата', description = "У тебя не хватило коинов для продления личной комнаты. Твой предмет был заблокирован на 3 дня^^\rТы можешь продлить товар вручную через меню управления твоей ролью".format(cost), color=0x2b2d31)
                                await member.send(embed = embed)      
                            else:   

                                bloop = (datetime.now() + timedelta(days=30)).timestamp()
                                task.execute(f'UPDATE tasks SET date = "{bloop}" where id={member.id} and guild_id={guild.id}')
                                task_db.commit()

                                ec.execute(f'UPDATE channel SET status = "open" where id={member.id} and guild_id={guild.id}')
                                ec.execute(f'UPDATE balance SET bal={bal[0] - cost}  where id={member.id} and guild_id={guild.id}')
                                ec_db.commit()
                                embed=nextcord.Embed(title='Автооплата', description = f"Твоя личная комната успешно была продлена. \rС твоего баланса было списано {cost}", color=0x2b2d31)
                                embed.set_thumbnail(url=member.display_avatar)
                                await member.send(embed = embed) 
                    else:

                        
                        task.execute(f"DELETE FROM tasks where id={member.id} and guild_id = {guild.id} and name='channel'")
                        task_db.commit()

                        ec.execute(f'UPDATE channel SET status = "close" where id={member.id} and guild_id={guild.id}')
                        ec_db.commit()

                        floot = (datetime.now() + timedelta(days=3)).timestamp()
                        
                        task.execute(f"INSERT INTO tasks VALUES ('deletechannel','{floot}','{member.id}', '{guild.id}')")
                        task_db.commit()

                        embed=nextcord.Embed(title="Ваша личная комната была заблокирована", description='Причина блокировки: `Окончание срока действия товара`\rНа продление товара, тебе дается **3 дня**. Товар можно продлить в меню управления товаром', color=0x2b2d31)
                        embed.set_thumbnail(url=member.display_avatar)
                        await member.send(embed=embed)
                else:
                    pass

    @tasks.loop(seconds=1)
    async def delchannel(self):
        guild = self.bot.get_guild(int(settings["Guild_ID"]))
        bloop = datetime.now().timestamp()
        task.execute(f"SELECT date, id FROM tasks WHERE name = 'deletechannel'")
        for row in task.fetchall():
            if row[0] <= bloop:
                member = guild.get_member(int(row[1]))
                task.execute(f"DELETE FROM tasks where id={member.id} and guild_id = {guild.id} and name='deletechannel'")
                task_db.commit()
                for custom in ec.execute(f"SELECT channel FROM channel where id={member.id} and guild_id = {guild.id}"):
                    channel = guild.get_channel(int(custom[0]))
                    await channel.delete()
                    embed=nextcord.Embed(title="Ваша личная комната была удалена", description='Причина удаления: `Окончание срока действия товара`', color=0x2b2d31)
                    embed.set_thumbnail(url=member.display_avatar)
                    await member.send(embed=embed)
            else:
                pass   



    @commands.Cog.listener()
    async def on_ready(self):
        self.role.start()
        self.delrole.start()
        self.channels.start()
        self.delchannel.start()
        self.nonadmission.start()
        self.multiplier.start()
        
    @multiplier.before_loop
    async def before_act(self):
        await self.bot.wait_until_ready()  

    @nonadmission.before_loop
    async def before_act(self):
        await self.bot.wait_until_ready()   

    @delchannel.before_loop
    async def before_act(self):
        await self.bot.wait_until_ready()  

    @delchannel.before_loop
    async def before_act(self):
        await self.bot.wait_until_ready()  

    @role.before_loop
    async def before_act(self):
        await self.bot.wait_until_ready()   


    @delrole.before_loop
    async def before_act(self):
        await self.bot.wait_until_ready()   


    
        
    


def setup(bot):
    bot.add_cog(void_update(bot))
    print('Loop успешно были подключены')
    