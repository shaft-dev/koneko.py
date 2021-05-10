from discord.ext import commands
import json
from discord.utils import get
import discord

class NotFoundError(Exception):
    """
    manual indicator that discord.NotFound was excepted
    """
    pass

class util_cmds(commands.Cog):
    """
    Utility Commands
    """
    def __init__(self, bot) -> None:
        self.bot = bot

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

    @commands.command(name="default_role", aliases=["dr", "def_role"])
    @commands.has_permissions(administrator=True)
    async def default_role(self, ctx: commands.Context, arg: str = None) -> None:
        """
        Allows a guild administrator to set a default role to give users
        when they join the guild
        :param ctx: command context object
        :param arg: should have a role name passed
        :return: None
        """
        if ctx.author.bot:
            return
        info_dir = "./Servers/server_" + str(ctx.guild.id) + "/guild_info.json"
        roles = ctx.guild.roles
        found = False
        for role in roles:
            if role.name.lower() == arg:
                found = True
                # lazy
                info_file = open(info_dir, "r")
                guild_info = dict()
                info = info_file.read()
                if info != "":
                    guild_info = json.loads(info)
                guild_info["default_role"] = role.id
                info_file.close()
                info_file = open(info_dir, "w")
                json.dump(guild_info, info_file)
                info_file.close()
                break
        # filter out for incorrect syntax eventually
        if not found:
            await ctx.send(f'Role "{arg}" not found. Multi-word roles need double-quote \
formatting to be recognized. Ex: `set default role "cool guy"`')
        else:
            await ctx.send(f'Default role changed to "{arg}" role.')

    @commands.command(name="role_react", aliases=["rr", "rr+"])
    @commands.has_permissions(manage_roles=True)
    async def role_react(self, ctx: commands.Context, *args: list) -> None:
        """
        Allows anyone with manage roles permissions to set up reactions for getting roles
        :param ctx: Context object
        :param args: list of arguments in order emoji, role name
        :return: None
        """
        if ctx.author.bot:
            return
        if len(args) < 2:
            await ctx.send("Please provide a role name and an emoji.")
            return
        info_dir = "./Servers/server_" + str(ctx.guild.id) + "/guild_info.json"
        emoji = "".join(args[0])
        role_name = str()
        for i in range(1, len(args)):
            if i == len(args) - 1:
                role_name += "".join(args[i])
            else:
                role_name += "".join(args[i]) + " "
        role = get(ctx.guild.roles, name=role_name)
        if role:
            info_file = open(info_dir, "r")
            guild_info = json.load(info_file)
            info_file.close()
            if not "role_reactions" in guild_info:
                guild_info["role_reactions"] = dict()
            # map the emoji to the role id
            if len(guild_info["role_reactions"]) == 0:
                msg = await ctx.send(f"React to get a role:\n\n{emoji}  `{role_name}`")
                guild_info["role_reactions"][str(msg.id)] = dict()
                guild_info["role_reactions"][str(msg.id)][emoji] = role.id
                await msg.add_reaction(emoji)
                await ctx.message.delete()
            else:
                # should only be one reaction message
                # will have to deal with message being deleted later - mostly dealt with
                try: 
                    # fix this eventually, it's currently a bandaid
                    key = list(guild_info["role_reactions"].keys())[0]
                    channels = ctx.guild.channels
                    msg = None
                    not_found = False
                    for channel in channels:
                        try:
                            msg = await channel.fetch_message(key)
                            not_found = False
                            break
                        except:
                            not_found = True
                    if not_found == True:
                        raise NotFoundError
                    if not emoji in guild_info["role_reactions"][str(msg.id)]:
                        guild_info["role_reactions"][str(msg.id)][emoji] = role.id
                        await msg.edit(content=msg.content + f"\n\n{emoji}  `{role_name}`")
                        await msg.add_reaction(emoji)
                        await ctx.message.delete()
                    else:
                        await ctx.send("Emoji is already being used for another role.")
                except NotFoundError:
                    guild_info.pop("role_reactions", None)
                    await ctx.send("Error: Reaction message not found. Please try again.")
            info_file = open(info_dir, "w")
            json.dump(guild_info, info_file)
            info_file.close()
        else:
            await ctx.send("Role not found. Roles are case sensitive.")
    
    @commands.command(name="role_react_remove", aliases = ["rrr", "rr-"])
    @commands.has_permissions(manage_roles=True)
    async def role_react_remove(self, ctx: commands.Context, arg: str) -> None:
        """
        Remove a role reaction from role_react message
        :param ctx: discord context object
        :param arg: argument passed, should be an emoji as str
        :return: None
        """
        if ctx.author.bot:
            return
        emoji = arg
        info_dir = "./Servers/server_" + str(ctx.guild.id) + "/guild_info.json"
        info_file = open(info_dir, "r")
        guild_info = json.load(info_file)
        info_file.close()
        if "role_reactions" in guild_info:
            key = list(guild_info["role_reactions"].keys())[0]
            try:
                channels = await ctx.guild.fetch_channels()
                # same bandaid
                msg = None
                not_found = False
                for channel in channels:
                    try:
                        msg = await channel.fetch_message(key)
                        not_found = False
                        break
                    except:
                        not_found = True
                if not_found:
                    raise NotFoundError
                react_dict = guild_info["role_reactions"][key]
                if emoji in react_dict:
                    if len(react_dict) == 1:
                        guild_info.pop("role_reactions", None)
                        await msg.delete()
                        await ctx.message.delete()
                    else:
                        await msg.clear_reaction(emoji)
                        react_dict.pop(emoji)
                        new_content = "React to get a role:"
                        # this is more expensive than I would like.
                        for emoji, role_id in react_dict.items():
                            role_name = get(ctx.guild.roles, id=role_id).name
                            new_content += f"\n\n {emoji}  `{role_name}`"
                        await msg.edit(content=new_content)
                        await ctx.message.delete()
                else:
                    await ctx.send("This emoji is not being used for any role reaction.")
            except NotFoundError:
                guild_info.pop("role_reactions")
                await ctx.send("There is no existing role reaction message.")
            info_file = open(info_dir, "w")
            json.dump(guild_info, info_file)
            info_file.close()

def setup(bot):
    bot.add_cog(util_cmds(bot))
