from io import TextIOWrapper
from typing import List, ValuesView
from discord import file
from discord.errors import HTTPException
from discord.ext import commands
import json
from discord.ext.commands.cooldowns import BucketType
from discord.utils import get
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
import discord
from download import download_vid, get_vid_length
import os

def save_guild_data(data: dict, file: TextIOWrapper) -> None:
    file.seek(0)
    file.truncate()
    json.dump(data, file)
    file.close()

class util_cmds(commands.Cog):
    """
    Utility Commands
    """
    def __init__(self, bot) -> None:
        self.bot: commands.bot = bot

    @commands.command()
    async def info(self, ctx: commands.Context, arg: str = None) -> None:
        """
        Help command
        :param ctx: Context object
        :param arg: specifies help subsection
        :return: None
        """
        if ctx.author.bot:
            return
        await ctx.send("This bot is in a development-only state. \
            \nNo commands are currently available.")

    @cog_ext.cog_slash(name="ping", description="Get bot latency 🏓")
    async def ping(self, ctx: SlashContext):
        await ctx.send(f"pong! {round(self.bot.latency * 1000, 2)}ms response")

    @commands.command(name="default_role", aliases=["dr", "def_role"])
    @commands.has_permissions(administrator=True)
    async def default_role(self, ctx: commands.Context, *args: list) -> None:
        """
        Allows a guild administrator to set a default role to give users
        when they join the guild
        :param ctx: command context object
        :param arg: should have a role name passed
        :return: None
        """
        if ctx.author.bot:
            return
        role_name = ""
        for arg in args:
            role_name += "".join(arg)
            if arg != args[-1]:
                role_name += " "
        roles = ctx.guild.roles
        role = get(roles, name=role_name)
        if not role:
            await ctx.send(f'Role "{role_name}" not found. Role names are case-sensitive')
        else:
            info_dir = "./Servers/server_" + str(ctx.guild.id) + "/guild_info.json"
            info_file = open(info_dir, "r+")
            guild_info = dict()
            info = info_file.read()
            if info != "":
                guild_info = json.loads(info)
            # go back to the beginning and erase it for writing.
            info_file.seek(0)
            info_file.truncate()
            guild_info["default_role"] = role.id
            json.dump(guild_info, info_file)
            info_file.close()
            await ctx.send(f'Default role changed to "{role_name}" role.')
    
    @cog_ext.cog_subcommand(base="role", subcommand_group="reactions", name="add",
    description = "Add a role reaction to a role reaction message, or create one.",
    options = [
        create_option (
            name = "emoji",
            description = "The emoji to be used for the role reaction.",
            required = True,
            option_type = 3
        ),
        create_option (
            name = "role",
            description = "The role to give a user",
            required = True,
            option_type = 8
        ),
        create_option (
            name = "message",
            description = "Text to go at the top of role reaction message. Defaults to 'React to get a role:'",
            required = False,
            option_type = 3
        ),
        create_option (
            name = "description",
            description = "Description of role reaction. Defaults to role name.",
            required = False, 
            option_type = 3
        ),
        create_option (
            name = "channel",
            description = "(IF NO MESSAGE EXISTS) The channel to send reaction message in",
            required = False,
            option_type = 7
        )
    ])
    @commands.has_permissions(manage_roles=True)
    async def _role_reactions_add(self, ctx: SlashContext, emoji: str, role: discord.Role,
    message: str = "React to get a role:", description: str = None, channel: discord.TextChannel = None) -> None:
        """
        Takes a lot of args and does some stuff.
        note to self - fix this docstring
        :return: None
        """
        # kind of annoying that the permissions thingy is so bare in this lib
        if ctx.author.bot:
            return
        await ctx.defer(hidden=True)
        info_dir = "./Servers/server_" + str(ctx.guild.id) + "/guild_info.json"
        chan: discord.TextChannel = channel or ctx.channel
        chan_id: int = chan.id
        bot_roles: List[discord.Role] = ctx.guild.get_member(self.bot.user.id).roles
        can_assign: bool = False
        for b_role in bot_roles:
            if b_role.position > role.position:
                can_assign = True
        if not can_assign:
            await ctx.send(content=f"Cannot assign `{role.name}` as role is above bot role.", hidden=True)
            return
        info_file = open(info_dir, "r+")
        guild_info = json.load(info_file)
        if not "role_reactions" in guild_info:
            guild_info["role_reactions"] = dict()
            guild_info["role_reactions"]["emojis_used"] = dict()
            guild_info["role_reactions"]["channel"] = chan_id
            guild_info["role_reactions"]["reactions"] = dict()
            guild_info["role_reactions"]["title"] = message
        rrs: dict = guild_info["role_reactions"]
        if len(rrs["reactions"]) == 0:
            to_send: str = f"{message}\n\n{emoji}  `{description or role.name}`"
            msg: discord.Message = await chan.send(to_send)
            try:
                await msg.add_reaction(emoji)
            except:
                await ctx.send("Emoji not found.", hidden=True)
                await msg.delete()
                info_file.close()
                return
            rrs["message"] = msg.id
            rrs["reactions"][str(role.id)] = {"emoji": emoji, "description": description or role.name}
            rrs["emojis_used"][emoji] = role.id
            await msg.add_reaction(emoji)
            await ctx.send(content="Message creation successful! Click to dismiss.", hidden=True)
        else:
            channels = ctx.guild.channels
            msg: discord.Message = None
            channel: discord.TextChannel = get(channels, id=guild_info["role_reactions"]["channel"])
            if channel:
                try:
                    msg = await channel.fetch_message(guild_info["role_reactions"]["message"])
                except discord.NotFound:
                    guild_info.pop("role_reactions", None)
                    await ctx.send("Reaction message not found. Amending guild data. Please try again.", hidden=True)
                    save_guild_data(guild_info, info_file)
                    return
                rrs: dict = guild_info["role_reactions"]
                if not str(role.id) in rrs["reactions"] and not emoji in rrs["emojis_used"]:
                    try:
                        await msg.add_reaction(emoji)
                    except:
                        await ctx.send(content="Emoji not found.", hidden=True)
                        info_file.close()
                        return
                    to_send: str = msg.content + f"\n\n{emoji}  `{description or role.name}`"
                    await msg.edit(content=to_send)
                    rrs["reactions"][str(role.id)] = {"emoji": emoji, "description": description or role.name}
                    rrs["emojis_used"][emoji] = role.id
                    await ctx.send(content=f"{role.name} successfully added! Click to dismiss.", hidden=True)
                elif str(role.id) in rrs["reactions"]:
                    await ctx.send("Role is already set up for reaction.", hidden=True)
                    info_file.close()
                    return
                elif emoji in rrs["emojis_used"]:
                    await ctx.send("This emoji is alreaedy being used for another role.", hidden=True)
                    info_file.close()
                    return
            else:
                await ctx.send("No channel found :interrobang:", hidden=True)
        save_guild_data(guild_info, info_file)
    
    @cog_ext.cog_subcommand(base="role", subcommand_group="reactions", name="remove", 
    description="Remove a role from role reaction message.",
    options = [
        create_option (
            name = "role",
            description = "The role of the reaction to remove.",
            required = True,
            option_type = 8
        )
    ])
    @commands.has_permissions(manage_roles=True)
    async def _role_reactions_remove(self, ctx: SlashContext, role: discord.Role) -> None:
        """
        Remove a role reaction from role_react message
        :param ctx: discord context object
        :param arg: argument passed, should be an emoji as str
        :return: None
        """
        if ctx.author.bot:
            return
        info_dir = "./Servers/server_" + str(ctx.guild.id) + "/guild_info.json"
        info_file = open(info_dir, "r+")
        guild_info = json.load(info_file)
        if "role_reactions" in guild_info:
            try:
                channels: List[discord.TextChannel] = ctx.guild.channels
                channel:discord.TextChannel = get(channels, id=guild_info["role_reactions"]["channel"])
                msg: discord.Message = await channel.fetch_message(guild_info["role_reactions"]["message"])
                react_dict: dict = guild_info["role_reactions"]["reactions"]
                emojis: List[str] = guild_info["role_reactions"]["emojis_used"]
                title: str = guild_info["role_reactions"]["title"]
                if str(role.id) in react_dict:
                    if len(react_dict) == 1:
                        guild_info.pop("role_reactions", None)
                        await msg.delete()
                        await ctx.send("Role reaction message cleared.", hidden=True)
                    else:
                        r_emoji: str = react_dict[str(role.id)]["emoji"]
                        await msg.clear_reaction(r_emoji)
                        emojis.pop(r_emoji)
                        react_dict.pop(str(role.id))
                        new_content = title
                        # this is more expensive than I would like.
                        for role_id, ed_dict in react_dict.items():
                            emoji: str = ed_dict["emoji"]
                            description: str = ed_dict["description"]
                            new_content += f"\n\n{emoji}  `{description}`"
                        await msg.edit(content=new_content)
                        await ctx.send(f"`{role.name}` successfully removed! Click to dismiss.")
                else:
                    await ctx.send("This role is not being used for any role reaction.", hidden=True)
            except discord.NotFound:
                guild_info.pop("role_reactions")
                await ctx.send("There is no existing role reaction message.", hidden=True)
            save_guild_data(guild_info, info_file)

    @cog_ext.cog_subcommand(base="role", subcommand_group="reactions", name="delete",
    description="Delete role reaction message.")
    @commands.has_permissions(manage_roles=True)
    async def _role_reactions_delete(self, ctx: SlashContext):
        if ctx.author.bot:
            return
        info_dir = "./Servers/server_" + str(ctx.guild.id) + "/guild_info.json"
        info_file = open(info_dir, "r+")
        guild_info: dict = json.load(info_file)
        if "role_reactions" in guild_info:
            save_guild_data(guild_info, info_file)
            msg: int = guild_info["role_reactions"]["message"]
            channel_id: int = guild_info["role_reactions"]["channel"]
            channel: discord.TextChannel = get(ctx.guild.channels, id=channel_id)
            message: discord.Message = None 
            guild_info.pop("role_reactions")
            try:
                message = await channel.fetch_message(msg)
            except discord.NotFound:
                await ctx.send("No reaction message exists. Amending data.", hidden=True)
                info_file.close()
                return
            await message.delete()
            await ctx.send("Role reaction message successfully deleted", hidden=True)
        else:
            await ctx.send("No role reactions are set up.", hidden=True)
            info_file.close()
    
    @cog_ext.cog_subcommand(base="video", name="download", description="Download video from a variety of sites. 30 second cooldown per server.",
    options = [
        create_option (
            name="url",
            description="URL of video to download.",
            option_type = 3,
            required = True
        )
    ])
    @commands.cooldown(rate=1, per=30, type=BucketType.user)
    async def _video_download(self, ctx: SlashContext, url: str) -> None:
        # this will probably become a guild specific command for obvious reasons
        await ctx.defer()
        def prog_hook(dl):
            if dl["status"] == "finished":
                size = os.path.getsize("./" + dl["filename"])
                print(size)
                if size <= 5e6:
                    file = open(dl["filename"], "rb")
                    # setup a coroutine to send the file
                    async def send_file():
                        try:
                            await ctx.send(file=discord.File(file))
                        except discord.HTTPException:
                            await ctx.send("File is too large (5MB maximum)")
                        except:
                            pass
                        file.close()
                        os.unlink(dl["filename"])
                    # setup up an async task
                    self.bot.loop.create_task(send_file())
                else:
                    self.bot.loop.create_task(ctx.send("File is too large (5MB maximum)"))
                    os.unlink(dl["filename"])
        # filtering for other errors probably caused by invalid url
        try:
            download_vid(url=url, hook=prog_hook)
        except:
            await ctx.send("Unknown error. Check your url and try again.")
                
    @_video_download.error
    async def util_slash_error(self, ctx: SlashContext, err: Exception) -> None:
        if isinstance(err, commands.errors.CommandOnCooldown):
            await ctx.send(content=str(err), hidden=True)
        else:
            print(err)

def setup(bot):
    bot.add_cog(util_cmds(bot))
