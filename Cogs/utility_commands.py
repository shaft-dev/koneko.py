from discord.ext import commands
import json
from discord.utils import get

class util_cmds(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
    @commands.command()
    async def info(self, ctx: commands.Context, arg: str = None) -> None:
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

    @commands.command(name="role_react", aliases=["rr"])
    @commands.has_permissions(manage_roles=True)
    async def role_react(self, ctx: commands.Context, *args: list) -> None:
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
                msg = await ctx.send(f"React to get a role:\n\n`{emoji}: {role_name}`")
                guild_info["role_reactions"][str(msg.id)] = dict()
                guild_info["role_reactions"][str(msg.id)][emoji] = role.id
                await msg.add_reaction(emoji)
            else:
                # should only be one reaction message
                # will have to deal with message being deleted later
                msg = await ctx.fetch_message(list(guild_info["role_reactions"].keys())[0])
                if not emoji in guild_info["role_reactions"][str(msg.id)]:
                    guild_info["role_reactions"][str(msg.id)][emoji] = role.id
                    await msg.edit(content=msg.content + f"\n\n`{emoji}: {role_name}`")
                    await msg.add_reaction(emoji)
                else:
                    await ctx.send("Emoji is already being used for another role.")
            info_file = open(info_dir, "w")
            json.dump(guild_info, info_file)
            info_file.close()
        else:
            await ctx.send("Role not found. Roles are case sensitive.")
        
def setup(bot):
    bot.add_cog(util_cmds(bot))
