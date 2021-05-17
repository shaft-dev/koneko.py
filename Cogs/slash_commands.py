from operator import pos
from api_requests import get_reddit_posts
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from Cogs.api_commands import format_reddit_embed, ChanNotNSFW, VideoUnsupported
from random import choice
from api_requests import BadRequest

# just testing some stuff out with slashes.

class slash_cmds(commands.Cog):
    """
    slash commands container
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @cog_ext.cog_slash(name="ping", description="Get bot latency 🏓")
    async def ping(self, ctx: SlashContext):
        await ctx.send(f"pong! {self.bot.latency * 1000}ms response")

    @cog_ext.cog_slash(name="reddit", description="Get a post from reddit", 
    options = [
        create_option (
            name="subreddit",
            description="The subreddit to get a post from",
            option_type=3,
            required=True
        ),
        create_option (
            name="sort",
            description="Post sorting type.",
            option_type=3,
            choices = [
                create_choice (
                    name="Hot",
                    value="hot"
                ),
                create_choice (
                    name="Top",
                    value="top"
                ),
                create_choice (
                    name="New",
                    value="new"
                ),
                create_choice (
                    name="Rising",
                    value="rising"
                ),
                create_choice (
                    name="Controversial",
                    value="controversial"
                )
            ],
            required=False
        ),
        create_option (
            name="num_posts",
            description="Number of posts to choose from. Max 75.",
            option_type=4,
            required=False
        ),
    ])
    async def reddit(self, ctx: SlashContext, subreddit: str = "", sort: str = "", num_posts: int = 0) -> None:
        if num_posts:
            num_posts = str(num_posts)
        try:
            posts = get_reddit_posts(subreddit, sort, num_posts)
            if len(posts) > 0:
                await ctx.defer()
                post = choice(posts)
                if post["nsfw"] == True and ctx.channel.is_nsfw() == False:
                    raise ChanNotNSFW
                embed = format_reddit_embed(post)
                embed.set_author(name="For: " + ctx.author.display_name, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
        except BadRequest:
            await ctx.send("Something went wrong with the post request.")
        except ChanNotNSFW:
            await ctx.send("Post is nsfw. Try again in an nsfw channel or set this channel to nsfw.")
        except VideoUnsupported:
            await ctx.send("Post selected is of unsupported rich embed type `video`.")


def setup(bot: commands.Bot):
    bot.add_cog(slash_cmds(bot))
