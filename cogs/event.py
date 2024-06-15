
import nextcord
from nextcord.ext import commands
import sqlite3
from config import *
import time

ec_db = sqlite3.connect('database/economy.db')
ec = ec_db.cursor()

banner_db = sqlite3.connect('database/banner.db', timeout=10)
banner = banner_db.cursor()

logs_db = sqlite3.connect('database/logs.db')
logs = logs_db.cursor()

mr_db = sqlite3.connect('database/marry.db')
mr = mr_db.cursor()

pr_db = sqlite3.connect('database/private.db')
pr = pr_db.cursor()

c_db = sqlite3.connect('database/clan.db', timeout=10)
c = c_db.cursor()

pec_db = sqlite3.connect('database/premium.db')
pec = pec_db.cursor()

lvl_db = sqlite3.connect('database/lvl.db')
lvl = lvl_db.cursor()

wr_db = sqlite3.connect('database/moderation.db')
wr = wr_db.cursor()

profile_db = sqlite3.connect('database/profile.db')
profile = profile_db.cursor()

class event(commands.Cog):


    def __init__(self, bot):
        self.bot = bot
 
    

    @commands.Cog.listener()
    async def on_member_join(self, member):

        lvl.execute(
            f"SELECT id, guild_id FROM level where id={member.id} and guild_id = {member.guild.id}")
        if lvl.fetchone() is None:
            lvl.execute(
                f"INSERT INTO level VALUES (0, '{member.id}', '{member.guild.id}', 1)")
        else:
            pass
        lvl_db.commit() 

        banner.execute(
            f"SELECT id FROM act where id={member.id}")
        if banner.fetchone() is None:
            banner.execute(
                f"INSERT INTO act VALUES ('{member.id}', '{member.guild.id}', 0, 0)")
        else:
            pass
        banner_db.commit()

        c.execute(
            f"SELECT id, guild_id FROM user where id={member.id} and guild_id = {member.guild.id}")
        if c.fetchone() is None:
            c.execute(
                f"INSERT INTO user VALUES ('{member.id}', '{member.guild.id}', 0)")
        else:
            pass
        c_db.commit()

        wr.execute(f"SELECT id FROM profile where id={member.id} and guild_id = {member.guild.id}")
        if wr.fetchone() is None:
            wr.execute(
                f"INSERT INTO profile VALUES ('{member.id}', '{member.guild.id}', 0, 0)")
        else:
            pass
        wr_db.commit()

        wr.execute(f"SELECT id FROM stata where id={member.id} and guild_id = {member.guild.id}")
        if wr.fetchone() is None:
            wr.execute(
                f"INSERT INTO stata VALUES ('{member.id}', '{member.guild.id}', 0, 0, 0, 0, 0)")
        else:
            pass
        wr_db.commit()

        wr.execute(f"SELECT id FROM support where id={member.id} and guild_id = {member.guild.id}")
        if wr.fetchone() is None:
            wr.execute(
                f"INSERT INTO support VALUES ('{member.id}', '{member.guild.id}', 0, 0)")
        else:
            pass
        wr_db.commit()

        mr.execute(
            f"SELECT id, guild_id FROM marry where id={member.id} and guild_id = {member.guild.id}")
        if mr.fetchone() is None:
            mr.execute(
                f"INSERT INTO marry VALUES ('{member.id}', '{member.guild.id}', 0, 0, 0, 0, 'none', 'none', 0)")
        else:
            pass
        mr_db.commit()

 

        ### Profile ###

        profile_db = sqlite3.connect('database/profile.db')
        profile = profile_db.cursor()
        
        profile.execute(
            f"SELECT id, guild_id FROM profile where id={member.id} and guild_id = {member.guild.id}")
        if profile.fetchone() is None:
            profile.execute(
                f"INSERT INTO profile VALUES (0, 0, 'Не указано', '{member.id}', '{member.guild.id}', 'none', 'none', 'none')")
        else:
            pass
        profile_db.commit()

        ### Economy ###

        pec_db = sqlite3.connect('database/premium.db')
        pec = pec_db.cursor()

        pec.execute(
            f"SELECT id, guild_id FROM balance where id={member.id} and guild_id = {member.guild.id}")
        if pec.fetchone() is None:
            pec.execute(
                f"INSERT INTO balance VALUES ('{member.id}', '{member.guild.id}', 0)")
        else:
            pass
        pec_db.commit()



        ec_db = sqlite3.connect('database/economy.db')
        ec = ec_db.cursor()

        ec.execute(
            f"SELECT id, guild_id FROM balance where id={member.id} and guild_id = {member.guild.id}")
        if ec.fetchone() is None:
            ec.execute(
                f"INSERT INTO balance VALUES ('{member.id}', '{member.guild.id}', 0, 'None')")
        else:
            pass
        ec_db.commit()

        ### Private Voice ###


        pr.execute(f"SELECT id FROM private where id={member.id}")
        if pr.fetchone() is None:
            pr.execute(f"INSERT INTO private VALUES ('{member.guild.id}', '{member.id}', 0, 0)")
        else:
            pass
        pr_db.commit()


        pr.execute(f"SELECT id FROM action where id={member.id}")
        if pr.fetchone() is None:
            pr.execute(f"INSERT INTO action VALUES (0, '{member.guild.id}', '{member.id}')")
        else:
            pass
        pr_db.commit()

    @commands.Cog.listener()
    async def on_ready(self):
        
        guild = self.bot.get_guild(int(settings["Guild_ID"]))
        for guild in self.bot.guilds:

            ec.execute(
                f"SELECT guild_id FROM settings where guild_id={guild.id}")
            if ec.fetchone() is None:
                ec.execute(
                    f"INSERT INTO settings VALUES ('{guild.id}', 10, 150, 0, 50, 0.07, 7, 0, 10, 990154974019346522)")
            else:
                pass
            ec_db.commit() 
            


            logs.execute(
                f"SELECT guild_id FROM logs where guild_id={guild.id}")
            if logs.fetchone() is None:
                logs.execute(f"INSERT INTO logs VALUES (0, 0, 0, '{guild.id}')")
            else:
                pass
            logs_db.commit()
            
            pr.execute(
                f"SELECT guild_id FROM settings where guild_id={guild.id}")
            if pr.fetchone() is None:
                pr.execute(
                    f"INSERT INTO settings VALUES ('{guild.id}', 0, 0, 0)")
            else:
                pass
            pr_db.commit()



         

            mr.execute(
                f"SELECT guild_id FROM loveroom where guild_id = {guild.id}")
            if mr.fetchone() is None:
                mr.execute(
                    f"INSERT INTO loveroom VALUES ('{guild.id}', 0, 0)")
            else:
                pass
            mr_db.commit()

            banner.execute(
                f"SELECT guild_id FROM bannerdop where guild_id={guild.id}")
            if banner.fetchone() is None:
                banner.execute(
                    f"INSERT INTO bannerdop VALUES (0, '{guild.id}')")
            else:
                pass
            banner_db.commit()

            for member in guild.members:


                lvl.execute(
                    f"SELECT id, guild_id FROM level where id={member.id} and guild_id = {guild.id}")
                if lvl.fetchone() is None:
                    lvl.execute(
                        f"INSERT INTO level VALUES (0, '{member.id}', '{member.guild.id}', 1)")
                else:
                    pass
                lvl_db.commit()

                banner.execute(
                    f"SELECT id FROM act where id={member.id}")
                if banner.fetchone() is None:
                    banner.execute(
                        f"INSERT INTO act VALUES ('{member.id}', '{guild.id}', 0, 0)")
                else:
                    pass
                banner_db.commit()

                pr.execute(
                    f"SELECT id FROM private where id={member.id}")
                if pr.fetchone() is None:
                    pr.execute(
                        f"INSERT INTO private VALUES ('{guild.id}', '{member.id}', 0, 0)")
                else:
                    pass
                pr_db.commit()

                c.execute(
                    f"SELECT id, guild_id FROM user where id={member.id} and guild_id = {member.guild.id}")
                if c.fetchone() is None:
                    c.execute(
                        f"INSERT INTO user VALUES ('{member.id}', '{guild.id}', 0)")
                else:
                    pass
                c_db.commit()

                wr.execute(f"SELECT id FROM support where id={member.id} and guild_id = {guild.id}")
                if wr.fetchone() is None:
                    wr.execute(
                        f"INSERT INTO support VALUES ('{member.id}', '{member.guild.id}', 0, 0)")
                else:
                    pass
                wr_db.commit()

                wr.execute(f"SELECT id FROM profile where id={member.id} and guild_id = {guild.id}")
                if wr.fetchone() is None:
                    wr.execute(
                        f"INSERT INTO profile VALUES ('{member.id}', '{guild.id}', 0, 0)")
                else:
                    pass
                wr_db.commit()

                wr.execute(f"SELECT id FROM stata where id={member.id} and guild_id = {guild.id}")
                if wr.fetchone() is None:
                    wr.execute(
                        f"INSERT INTO stata VALUES ('{member.id}', '{guild.id}', 0, 0, 0, 0, 0)")
                else:
                    pass
                wr_db.commit()

                profile.execute(
                    f"SELECT id, guild_id FROM profile where id={member.id} and guild_id = {guild.id}")
                if profile.fetchone() is None:
                    profile.execute(
                        f"INSERT INTO profile VALUES (0, 0, 'Не указано', '{member.id}', '{guild.id}', 'none', 'none', 'none')")
                else:
                    pass
                profile_db.commit()

                mr.execute(
                    f"SELECT id, guild_id FROM marry where id={member.id} and guild_id = {guild.id}")
                if mr.fetchone() is None:
                    mr.execute(
                        f"INSERT INTO marry VALUES ('{member.id}', '{member.guild.id}', 0, 0, 0, 0, 'none', 'none', 0)")
                else:
                    pass
                mr_db.commit()

                pec.execute(
                    f"SELECT id, guild_id FROM balance where id={member.id} and guild_id = {guild.id}")
                if pec.fetchone() is None:
                    pec.execute(
                        f"INSERT INTO balance VALUES ('{member.id}', '{guild.id}', 0)")
                else:
                    pass
                pec_db.commit()

                ec.execute(
                    f"SELECT id, guild_id FROM balance where id={member.id} and guild_id = {guild.id}")
                if ec.fetchone() is None:
                    ec.execute(
                        f"INSERT INTO balance VALUES ('{member.id}', '{guild.id}', 0, 'None')")
                else:
                    pass
                ec_db.commit()

                ec.execute(
                    f"SELECT id, guild_id FROM inventory where id={member.id} and guild_id = {guild.id}")
                if ec.fetchone() is None:
                    ec.execute(
                        f"INSERT INTO inventory VALUES ('{member.id}', '{guild.id}', 0, 0, 0, 0, 0, 0, 0, 0, 0)")
                else:
                    pass
                ec_db.commit()








        global tdict
        tdict = {}


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        profile_db = sqlite3.connect('database/profile.db', timeout=10)
        profile = profile_db.cursor()
        for prof in profile.execute(f"SELECT voice FROM profile where id={member.id} and guild_id={member.guild.id}"):
            author = member.id
            if before.channel is None and after.channel is not None:
                t1 = time.time()
                tdict[author] = t1
            elif before.channel is not None and after.channel is None and author in tdict:
                t2 = time.time() 
                profile.execute(f"UPDATE profile SET voice='{prof[0] + t2-tdict[author]}' where id={member.id} and guild_id={member.guild.id}")
                profile_db.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        guild = self.bot.get_guild(int(settings['Guild_ID']))
        profile_db = sqlite3.connect('database/profile.db', timeout=10)
        profile = profile_db.cursor()
        for prof in profile.execute(f"SELECT txt FROM profile where id={message.author.id} and guild_id={guild.id}"):        
            if message.author == self.bot.user:
                return 
            else:
                profile.execute(f"UPDATE profile SET txt='{prof[0] + 1}' where id={message.author.id} and guild_id={guild.id}")
                profile_db.commit()


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        profile_db = sqlite3.connect('database/profile.db', timeout=10)
        profile = profile_db.cursor()
        for prof in profile.execute(f"SELECT voice FROM profile where id={member.id} and guild_id={member.guild.id}"):
            author = member.id
            if before.channel is None and after.channel is not None:
                t1 = time.time()
                tdict[author] = t1
            elif before.channel is not None and after.channel is None and author in tdict:
                t2 = time.time() 
                profile.execute(f"UPDATE profile SET voice='{prof[0] + t2-tdict[author]}' where id={member.id} and guild_id={member.guild.id}")
                profile_db.commit()           

    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        c.execute(f"DELETE FROM user where id = {member.id}")
        c_db.commit()
        for bibi in c.execute(f"SELECT id, owner_club FROM user where id={member.id}"):
            if bibi[1] == 0:
                pass
            else:
                for bibis in c.execute(f"SELECT avatar, name, datecreate, members FROM clan where owner={bibi[1]}"):
                    c.execute(f"UPDATE clan SET members={bibis[3] - 1} where owner={bibi[1]}")



def setup(bot):
    bot.add_cog(event(bot))