import nextcord
from nextcord.ext import commands
import math
from config import *
from nextcord.ext import application_checks, commands, menus
import sqlite3
import asyncio

ec_db = sqlite3.connect('database/economy.db', timeout=10)
ec = ec_db.cursor()   

mr_db = sqlite3.connect('database/marry.db', timeout=10)
mr = mr_db.cursor()

pec_db = sqlite3.connect('database/premium.db')
pec = pec_db.cursor()

class BuyButtons(nextcord.ui.Button):
    def __init__(self, label, inter, limit):
        super().__init__(label = label, style = nextcord.ButtonStyle.grey, emoji = "<:shop:1061218078869958706>",row = 0)
        self.inter = inter
        self.limit = limit
        self.label = label

    async def callback(self, interaction):
        if interaction.user == self.inter.user:
            cost = ec.execute("SELECT cost FROM shop WHERE _rowid_ = {}".format(self.label)).fetchone()[0]
            if cost > ec.execute("SELECT bal FROM balance WHERE id = {}".format(self.inter.user.id)).fetchone()[0]:
                await interaction.response.send_message( embed = nextcord.Embed(
                    description = "У тебя не хватает коинов^^", color=0x2b2d31
                ), ephemeral = True)
            else:
                role_id = ec.execute("SELECT role_id FROM shop WHERE _rowid_ = {}".format(self.label)).fetchone()[0]
                role = self.inter.guild.get_role(role_id)
                people_id = ec.execute("SELECT id FROM shop WHERE _rowid_ = {}".format(self.label)).fetchone()[0]
                people = self.inter.guild.get_member(people_id)
                if role in self.inter.user.roles:
                    await interaction.response.send_message( embed = nextcord.Embed(
                        description = "У вас уже имеется данный товар", color=0x2b2d31
                    ), ephemeral = True)
                else:
                    ec.execute("UPDATE balance SET bal = bal - {} WHERE id = {}".format(cost, self.inter.user.id))
                    ec.execute("UPDATE balance SET bal = bal + {} WHERE id = {}".format(math.floor(cost*0.3), people.id))
                    ec.execute("UPDATE shop SET buy = buy + 1 WHERE _rowid_ = {}".format(self.label))
                    ec_db.commit()
                    await self.inter.user.add_roles(role)
                    await interaction.send(  embed = nextcord.Embed(
                        description = f"Вы успешно купили слот под №{self.label} - {role.mention}", color=0x2b2d31
                    ), ephemeral=True)
                    await people.send(  embed = nextcord.Embed(
                        description = f"Ваш слот был куплен. Ваша прибыль с данного слота - {math.floor(cost*0.3)} коинов", color=0x2b2d31
                    ))
        
class Button_back(nextcord.ui.Button):
    def __init__(self, pages, inter, limit, current_page, sorting, sort, con_one):
        super().__init__(emoji="<:leftarrow:1070631138298699776> ", row = 2)
        self.pages = pages
        self.inter = inter
        self.limit = limit
        self.current_page = current_page
        self.sorting = sorting
        self.sort = sort
        self.con_one = con_one

    async def callback(self, interaction):
        if interaction.user == self.inter.user:
            self.current_page -= 1
            self.limit -= 5
            self.con_one = 0
            if self.current_page < 1:
                self.con_one = len(self.pages)*5-5
                self.current_page = len(self.pages)
                self.limit = len(self.pages)*5-5
            view = nextcord.ui.View()
            for x in ec.execute("SELECT id, role_id, cost, buy, _rowid_ FROM shop ORDER BY {} {} LIMIT {},5".format(self.sorting, self.sort, self.limit)):
                self.con_one += 1
                view.add_item(BuyButtons(str(self.con_one), self.inter, self.limit))

            view.add_item(Shop_select(self.inter))
            view.add_item(Button_back(self.pages, self.inter, self.limit, self.current_page, self.sorting, self.sort, self.con_one))
            view.add_item(Button_close(self.inter))
            view.add_item(Button_forward(self.pages, self.inter, self.limit, self.current_page, self.sorting, self.sort, self.con_one))

            await interaction.response.edit_message( embed = self.pages[self.current_page-1], view = view)

class Button_close(nextcord.ui.Button):
    def __init__(self, inter):
        super().__init__(emoji="<:downfilledtriangulararrow:1070631163586158592> ", row = 2)
        self.inter = inter

    async def callback(self, interaction):
        if interaction.user == self.inter.user:
            await interaction.response.defer()
            await interaction.edit_original_message(embed = nextcord.Embed(
                title = "Удаление сообщение...", color=0x2b2d31
            ), view = None,)
            await interaction.delete_original_message()

class Button_forward(nextcord.ui.Button):
    def __init__(self, pages, inter, limit, current_page, sorting, sort, con_one):
        super().__init__(emoji="<:rightarrow:1070631151502372904> ", row = 2)
        self.pages = pages
        self.inter = inter
        self.limit = limit
        self.current_page = current_page
        self.sorting = sorting
        self.sort = sort
        self.con_one = con_one

    async def callback(self, interaction):
        if interaction.user == self.inter.user:
            self.current_page += 1
            self.limit += 5
            if self.current_page > len(self.pages):
                self.current_page = 1
                self.con_one = 0
                self.limit = 0
                
            view = nextcord.ui.View()
            for x in ec.execute("SELECT id, role_id, cost, buy, _rowid_ FROM shop ORDER BY {} {} LIMIT {},5".format(self.sorting, self.sort, self.limit)):
                self.con_one += 1
                view.add_item(BuyButtons(label = str(self.con_one), inter = self.inter, limit = self.limit))
            
            view.add_item(Shop_select(self.inter))
            view.add_item(Button_back(self.pages, self.inter, self.limit, self.current_page, self.sorting, self.sort, self.con_one))
            view.add_item(Button_close(self.inter))
            view.add_item(Button_forward(self.pages, self.inter, self.limit, self.current_page, self.sorting, self.sort, self.con_one))
            
            await interaction.response.edit_message( embed = self.pages[self.current_page-1], view = view)

class Shop_select(nextcord.ui.Select):
    def __init__(self, inter):
        options = [
            nextcord.SelectOption(label='Сначала старые'),
            nextcord.SelectOption(label='Сначала новые'),
            nextcord.SelectOption(label='Сначала дорогие'),
            nextcord.SelectOption(label='Сначала дешевые'),
            nextcord.SelectOption(label='Сначала популярные')
        ]
        super().__init__(placeholder='Фильтр', min_values=1, max_values=1, options=options, row = 1)
        self.inter = inter


    async def callback(self, interaction):
        if interaction.user == self.inter.user:
            view = nextcord.ui.View()
            emb = nextcord.Embed(
                title = "Магазин ролей", color=0x2b2d31
            )
            if self.values[0] == 'Сначала старые':
                sorting = '_rowid_'
                sort = 'DESC'
            elif self.values[0] == 'Сначала новые':
                sorting = '_rowid_'
                sort = 'ASC'
            elif self.values[0] == 'Сначала дорогие':
                sorting = 'cost'
                sort = 'DESC'
            elif self.values[0] == 'Сначала дешевые':
                sorting = 'cost'
                sort = 'ASC'
            else:
                sorting = 'buy'
                sort = 'DESC'

            con_one = 0
            n = 0
            pages = []
            limit = 0
            for x in ec.execute("SELECT id, role_id, cost, buy, _rowid_ FROM shop ORDER BY {} {} LIMIT 5".format(sorting, sort)):
                con_one += 1
                view.add_item(BuyButtons(label = str(con_one), inter = self.inter, limit = limit))
                
            s = 0
            for x in ec.execute("SELECT id, role_id, cost, buy, _rowid_ FROM shop"):
                s += 1
            
            a = s//5
            if s%5 != 0:
                a += 1
            
            b = 0
            con_two = 0
            for x in ec.execute("SELECT id, role_id, cost, buy, _rowid_ FROM shop ORDER BY {} {}".format(sorting, sort)):
                con_two += 1
                n += 1 
                emb.add_field(
                    name = f" ⁣ ",
                    value = f"**{con_two}) {self.inter.guild.get_role(x[1]).mention} \nВладелец: <@{x[0]}> \nЦена: {x[2]} \nКуплена {x[3]} раз **",
                    inline = False
                )
                if n == 5:
                    b += 1
                    emb.set_thumbnail(url=self.inter.user.display_avatar)
                    emb.set_footer(text = f"Страница {b}/{a}")
                    pages.append(emb)
                    emb = nextcord.Embed(
                        title = "Магазин ролей", color=0x2b2d31
                    )
                    n = 0
            
            if n < 5 and n != 0:
                emb.set_thumbnail(url=self.inter.user.display_avatar)
                emb.set_footer(text = f"Страница {b+1}/{a}")
                pages.append(emb)

            current_page = 1
            view.add_item(Shop_select(self.inter))
            view.add_item(Button_back(pages, self.inter, limit, current_page, sorting, sort, con_one))
            view.add_item(Button_close(self.inter))
            view.add_item(Button_forward(pages, self.inter, limit, current_page, sorting, sort, con_one))

            await interaction.response.edit_message(embed = pages[0], view = view)

class GiveCashshop(commands.Cog):
    
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @nextcord.slash_command(description='Магазин ролей', guild_ids = [int(settings["Guild_ID"])])
    async def shop(self, inter, mode : str = nextcord.SlashOption(
        name="категория",
        choices={
        "Ролей": 'о', 
        "Кейсы": 'к'        
        },
    ),):
        owner = inter.user    
        if mode == 'о':
            emb = nextcord.Embed(
                title = "Магазин ролей", color=0x2b2d31
            )
            if ec.execute("SELECT * FROM shop").fetchone() == None:
                return await inter.send(
                    embed = nextcord.Embed(
                        title = "Магазин пуст..",
                        color = 0x2b2d31
                    )
                )

            view = nextcord.ui.View()
            n = 0
            pages = []
            limit = 0
            sorting = '_rowid_'
            sort = 'ASC'
            con_one = 0
            for x in ec.execute("SELECT id, role_id, cost, buy, _rowid_ FROM shop ORDER BY {} {} LIMIT 5".format(sorting, sort)):
                con_one += 1
                view.add_item(BuyButtons(label = str(con_one), inter = inter, limit = limit))
            
            s = 0
            for x in ec.execute("SELECT id, role_id, cost, buy, _rowid_ FROM shop"):
                s += 1
            
            a = s//5
            if s%5 != 0:
                a += 1
            
            b = 0
            con_two = 0
            for x in ec.execute("SELECT id, role_id, cost, buy, _rowid_ FROM shop ORDER BY {} {}".format(sorting, sort)):
                n += 1 
                con_two += 1
                emb.add_field(
                    name = f" ⁣ ",
                    value = f"**{con_two}) {inter.guild.get_role(x[1]).mention} \nВладелец: <@{x[0]}> \nЦена: {x[2]} \nКуплена {x[3]} раз **",
                    inline = False
                )
                if n == 5:
                    b += 1
                    emb.set_thumbnail(url=inter.user.display_avatar)
                    emb.set_footer(text = f"Страница {b}/{a}")
                    pages.append(emb)
                    emb = nextcord.Embed(
                        title = "Магазин ролей", color=0x2b2d31
                    )
                    n = 0
            
            if n < 5 and n != 0:
                emb.set_thumbnail(url=inter.user.display_avatar)
                emb.set_footer(text = f"Страница {b+1}/{a}")
                pages.append(emb)

            current_page = 1
            view.add_item(Shop_select(inter))
            view.add_item(Button_back(pages, inter, limit, current_page, sorting, sort, con_one))
            view.add_item(Button_close(inter))
            view.add_item(Button_forward(pages, inter, limit, current_page, sorting, sort, con_one ))
            await inter.send(embed = pages[0], view = view)
        elif mode == 'п':
            emb = nextcord.Embed(
                title = "Премиум магазин", color=0x2b2d31,
                description='Магазин пуст...'
            )
            await inter.send(embed=emb)
        elif mode == 'л':
            emb = nextcord.Embed(
                title = "Любовный магазин", color=0x2b2d31,
                description='Магазин пуст...'
            )
            await inter.send(embed=emb)
        elif mode == 'к':
            
            class case(nextcord.ui.View):
                def __init__(self):
                    super().__init__(timeout=60)

                if pec.execute(f"SELECT bal FROM balance WHERE id={inter.user.id} and guild_id={inter.guild.id} ").fetchone()[0] < 500:       
                    @nextcord.ui.button(label = '1', style = nextcord.ButtonStyle.grey, disabled=True)
                    async def item1_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        pass
                else:
                    @nextcord.ui.button(label = '1', style = nextcord.ButtonStyle.grey, disabled=False)
                    async def item1_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if owner.id == interaction.user.id: 
                            if pec.execute(f"SELECT bal FROM balance WHERE id={inter.user.id} and guild_id={inter.guild.id} ").fetchone()[0] < 500: 
                                embed = nextcord.Embed(description = f'У тебя не хватает коинов, для покупки данного кейса', color=0x2b2d31)
                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                await interaction.send(embed=embed, ephemeral= True)
                            else:  
                                pec.execute(f'UPDATE balance SET bal=bal-500  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                ec.execute(f'UPDATE inventory SET casepremium_=casepremium_+1  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                ec_db.commit()
                                pec_db.commit()

                                embed = nextcord.Embed(description = f'Ты успешно купил премиум кейс за 500 премиум коинов', color=0x2b2d31)
                                embed.set_footer(text="У тебя {} премиум кейсов".format(ec.execute(f"SELECT casepremium_ FROM inventory WHERE id={interaction.user.id} and guild_id={interaction.guild.id} ").fetchone()[0]))
                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                await interaction.send(embed=embed, ephemeral= True)                  
        
                                if ec.execute(f"SELECT bal FROM balance WHERE id={interaction.user.id} and guild_id={interaction.guild.id} ").fetchone()[0] < 400:
                                    self.item1_.disabled = True
                                if pec.execute(f"SELECT bal FROM balance WHERE id={interaction.user.id} and guild_id={interaction.guild.id} ").fetchone()[0] < 500: 
                                    self.item2_.disabled = True                
                                if ec.execute(f"SELECT bal FROM balance WHERE id={interaction.user.id} and guild_id={interaction.guild.id} ").fetchone()[0] < 400:
                                    self.item3_.disabled = True
                                await interaction.response.edit_message(view=self)  

                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)

                if mr.execute(f"SELECT balance FROM marry WHERE id={inter.user.id} and guild_id={inter.guild.id} ").fetchone()[0] < 800:       
                    @nextcord.ui.button(label = '2', style = nextcord.ButtonStyle.grey, disabled=True)
                    async def item2_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        pass
                else:
                    @nextcord.ui.button(label = '2', style = nextcord.ButtonStyle.grey, disabled=False)
                    async def item2_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if owner.id == interaction.user.id: 
                            if mr.execute(f"SELECT balance FROM marry WHERE id={inter.user.id} and guild_id={inter.guild.id} ").fetchone()[0] < 800:
                                embed = nextcord.Embed(description = f'У тебя не хватает коинов, для покупки данного кейса', color=0x2b2d31)
                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                await interaction.send(embed=embed, ephemeral= True)
                            else:
                                mr.execute(f'UPDATE marry SET balance=balance-800  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                ec.execute(f'UPDATE inventory SET casemarry_=casemarry_+1  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                ec_db.commit()
                                mr_db.commit()

                                embed = nextcord.Embed(description = f'Ты успешно купил обычный кейс за 800 коинов', color=0x2b2d31)
                                embed.set_footer(text="У тебя {} любовных кейсов".format(ec.execute(f"SELECT casemarry_ FROM inventory WHERE id={interaction.user.id} and guild_id={interaction.guild.id} ").fetchone()[0]))
                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                await interaction.send(embed=embed, ephemeral= True)                  
        

  
                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)    

                if ec.execute(f"SELECT bal FROM balance WHERE id={inter.user.id} and guild_id={inter.guild.id} ").fetchone()[0] < 400:       
                    @nextcord.ui.button(label = '3', style = nextcord.ButtonStyle.grey, disabled=True)
                    async def item3_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        pass
                else:
                    @nextcord.ui.button(label = '3', style = nextcord.ButtonStyle.grey, disabled=False)
                    async def item3_(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        if owner.id == interaction.user.id: 
                            if ec.execute(f"SELECT bal FROM balance WHERE id={inter.user.id} and guild_id={inter.guild.id} ").fetchone()[0] < 400:
                                embed = nextcord.Embed(description = f'У тебя не хватает коинов, для покупки данного кейса', color=0x2b2d31)
                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                await interaction.send(embed=embed, ephemeral= True)
                            else:
                                ec.execute(f'UPDATE balance SET bal=bal-400  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                ec.execute(f'UPDATE inventory SET case_=case_+1  where id={interaction.user.id} and guild_id={interaction.guild.id}')
                                ec_db.commit()

                                embed = nextcord.Embed(description = f'Ты успешно купил обычный кейс за 400 коинов', color=0x2b2d31)
                                embed.set_footer(text="У тебя {} обычных кейсов".format(ec.execute(f"SELECT case_ FROM inventory WHERE id={interaction.user.id} and guild_id={interaction.guild.id} ").fetchone()[0]))
                                embed.set_thumbnail(url=interaction.user.display_avatar)       
                                await interaction.send(embed=embed, ephemeral= True)                  
        

                        else:
                            embed = nextcord.Embed(description = f'Ты не можешь взаимодействовать с этим сообщением', color=0x2b2d31)
                            embed.set_thumbnail(url=interaction.user.display_avatar)       
                            await interaction.send(embed=embed, ephemeral= True)


                

            
            
            emb = nextcord.Embed(
                title = "Магазин кейсов", color=0x2b2d31
            )
            emb.add_field(
                    name = f" ⁣ ",
                    value = f"**1) Премиум кейс\nЦена: 500 Премиум коинов**",
                    inline = False
                )
            emb.add_field(
                    name = f" ⁣ ",
                    value = f"**2) Любовный кейс\nЦена: 800 Любовных коинов**",
                    inline = False
                )
            emb.add_field(
                    name = f" ⁣ ",
                    value = f"**3) Обычный кейс\nЦена: 400 коинов**",
                    inline = False
                )
            
            await inter.send(embed=emb, view = case())
        







def setup(bot):
    bot.add_cog(GiveCashshop(bot))







            

