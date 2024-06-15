import nextcord
from nextcord.ext import commands
from config import *
from nextcord.ext import application_checks, commands, menus
import random
from captcha.image import ImageCaptcha




import sqlite3

import asyncio

ec_db = sqlite3.connect('database/economy.db', timeout=10)
ec = ec_db.cursor()   

class BuyButtons(nextcord.ui.Button):
    def __init__(self, label, inter, limit):
        super().__init__(label = label, style = nextcord.ButtonStyle.grey, emoji = "<:shop:1061218078869958706>",row = 0)
        self.inter = inter
        self.limit = limit
        self.label = label

    async def callback(self, interaction):
        label = self.label
        if interaction.user == self.inter.user:
            try:
                image = ImageCaptcha(fonts=['assets/20680.ttf', 'assets/20680.ttf'])

                st = "{}{}{}{}".format(random.randint(0,9), random.randint(0,9), random.randint(0,9), random.randint(0,9))
                

                image.write(st, 'out.png')

                class capt(nextcord.ui.View):
                    def __init__(self):
                        super().__init__(timeout=60)

                    @nextcord.ui.button(label='Ввести капчу', style=nextcord.ButtonStyle.grey)
                    async def regcap(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):

                        class regcap(nextcord.ui.Modal):
                            def __init__(self):
                                super().__init__('Смена названия')

                                self.cap = nextcord.ui.TextInput(label = 'Реши данную капчу', min_length=4, max_length=4, required=True, placeholder='жду^^', style=nextcord.TextInputStyle.paragraph)
                                self.add_item(self.cap)

                            async def callback(self, interaction: nextcord.Interaction) -> None:
                                cap = self.cap.value
                                if st == cap:
                                    role_id = ec.execute("SELECT role_id FROM shop WHERE _rowid_ = {}".format(label)).fetchone()[0]
                                    role = interaction.guild.get_role(role_id)

                                    ec.execute("DELETE FROM shop WHERE _rowid_ and role_id = {}".format(role.id))
                                    ec_db.commit()

                                    await interaction.send(  embed = nextcord.Embed(
                                        description = f"Вы успешно удалили слот под №{label} - {role.mention}", color=0x2b2d31
                                    ), ephemeral=True)
                                else:
                                    await interaction.send(  embed = nextcord.Embed(
                                        description = f"Неверная капча", color=0x2b2d31
                                    ), ephemeral=True)                              

                        await interaction.response.send_modal(regcap())
           
                file = nextcord.File("out.png", filename="out.png")
                await interaction.send(file=file, view=capt(), ephemeral=True)


                
            except:
                await interaction.send(  embed = nextcord.Embed(
                    description = f"Данный товар уже был удален^^", color=0x2b2d31
                ), ephemeral=True)


        
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
                title = "Админ-панель магазина ролей (Нажмите на номер товара для его удаления)", color=0x2b2d31
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
                        title = "Админ-панель магазина ролей (Нажмите на номер товара для его удаления)", color=0x2b2d31
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

class delete(commands.Cog):
    
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @nextcord.slash_command(name = 'delete-item', description="Убрать роль из магазина", guild_ids = [int(settings["Guild_ID"])])
    @application_checks.has_permissions(administrator=True)
    async def delete(self, inter):

          
        emb = nextcord.Embed(
            title = "Админ-панель магазина ролей (Нажмите на номер товара для его удаления)", color=0x2b2d31
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
                    title = "Админ-панель магазина ролей (Нажмите на номер товара для его удаления)", color=0x2b2d31
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
        await inter.send(embed = pages[0], view = view, ephemeral=True )
        
        







def setup(bot):
    bot.add_cog(delete(bot))







            

