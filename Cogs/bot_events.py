import os
from discord import guild
from discord.ext import commands
import json
from discord.utils import get
import discord.errors as errors
import discord

class bot_events(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        Handles startup stuff
        :return: None
        """
        activity = discord.Activity(name="hentai", type=discord.ActivityType.watching)
        print(f"Logged in as: {self.bot.user}")
        await self.bot.change_presence(activity=activity)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """
        Handle creation of server folder/info when bot joins a guild
        :param guild: The guild object of the joined guild
        """
        if not os.path.isdir("./Servers"):
            os.mkdir("./Servers")
        new_dir = "./Servers/server_" + str(guild.id)
        if not os.path.isdir("./Servers/server_" + str(guild.id)):
            os.mkdir(new_dir)
        new_file_path = new_dir + "/guild_info.json"
        if not os.path.isfile(new_file_path):
            new_file = open(new_file_path, "x")
            new_file.close()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """
        Handle what happens when a member joins, currently consisting of:
        - Give member a role if specified in guild
        :param member: Member object of member who joined guild
        """
        if member.bot:
            return
        guild = member.guild
        info_dir = "./Servers/server_" + str(guild.id) + "/guild_info.json"
        info_file = open(info_dir, "r")
        guild_info = dict()
        info = info_file.read()
        if info != "":
            guild_info = json.loads(info)
        info_file.close()
        if "default_role" in guild_info:
            role_id = guild_info["default_role"]
            role = get(guild.roles, id=role_id)
            try:
                await member.add_roles(role)
            except errors.Forbidden:
                await guild.system_channel.send("Error: add_roles forbidden. Default role set but \
bot does not have Manage Roles permission or bot role is below set default role in role list.")
            except:
                await guild.system_channel.send("An unknown error occured.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        """
        Handles reaction events currently containing:
        - reaction for role
        :param payload: a raw reaction action event payload object
        :return: None
        """
        member = payload.member
        if member.bot:
            return
        if not member.guild:
            return
        info_dir = "./Servers/server_" + str(payload.guild_id) + "/guild_info.json"
        info_file = open(info_dir)
        guild_info = json.load(info_file)
        info_file.close()
        if "role_reactions" in guild_info and str(payload.message_id) in guild_info["role_reactions"]:
            react_dict = guild_info["role_reactions"][str(payload.message_id)][1]
            emoji = str(payload.emoji)
            if emoji in react_dict:
                role = get(member.guild.roles, id=react_dict[emoji])
                try:
                    await member.add_roles(role)
                    await member.send(f"Added `{role.name}` role in `{member.guild.name}`!")
                except discord.Forbidden:
                    await member.guild.system_channel.send("Cannot give reaction role. Please allow manage roles permission or \
move bot role above role to give.")

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent) -> None:
        """
        Currently an extension of reaction command
        """
        info_dir = "./Servers/server_" + str(payload.guild_id) + "/guild_info.json"
        info_file = open(info_dir)
        guild_info = json.load(info_file)
        info_file.close()
        if "role_reactions" in guild_info and str(payload.message_id) in guild_info["role_reactions"]:
            guild_info.pop("role_reactions", None)
            info_file = open(info_dir, "w")
            json.dump(guild_info, info_file)
            info_file.close()

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:
        """
        Also an extenstion of reaction command
        """
        # basically like add but instead we remove the role or do nothing if the role isn't
        # given to the user
        guild = self.bot.get_guild(id=payload.guild_id)
        if not guild:
            return
        member = guild.get_member(payload.user_id)
        if member.bot:
            return
        info_dir = "./Servers/server_" + str(payload.guild_id) + "/guild_info.json"
        info_file = open(info_dir)
        guild_info = json.load(info_file)
        info_file.close()
        if "role_reactions" in guild_info and str(payload.message_id) in guild_info["role_reactions"]:
            react_dict = guild_info["role_reactions"][str(payload.message_id)][1]
            emoji = str(payload.emoji)
            if emoji in react_dict:
                role = get(guild.roles, id=react_dict[emoji])
                if role in member.roles:
                    try:
                        await member.remove_roles(role)
                        await member.send(f"Removed `{role.name}` role in `{guild.name}`!")
                    except discord.Forbidden:
                        await guild.system_channel.send("Cannot remove reaction role. Please allow manage roles permission or \
move bot role above role to give.")
                
def setup(bot):
    bot.add_cog(bot_events(bot))
