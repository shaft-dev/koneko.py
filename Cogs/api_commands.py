import discord
from api_requests import InvalidParams, BadRequest, get_reddit_posts
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from discord.ext import commands
from random import choice
import discord

class ChanNotNSFW(Exception):
    """
    Throw when NSFW command requested for non-NSFW channel
    """
    pass

class VideoUnsupported(Exception):
    """
    Throw when Post passed to format is a vid post
    """
    pass

def format_reddit_embed(post: dict) -> discord.Embed:
    """
    Formats a post object into an embed to send to a text channel
    :param post: Reddit post information in dictionary format
    :return: discord embed object
    """
    if post["possible_type"] == "video":
        raise VideoUnsupported
    embed = discord.Embed()
    embed.color = 0xff5700
    embed.title = post["title"]
    embed.url = post["link"]
    if post["possible_type"] == "image":
        embed.set_image(url=post["content_url"])
    elif post["text_post"] == True:
        embed.add_field(name="Text post:", value=post["text"])
    elif post["possible_type"] == "link":
        embed.set_image(url=post["thumbnail"])
        embed.add_field(name="Link:", value=post["content_url"])
    embed.set_footer(text="Posted by u/" + post["op"] + " 🔺" + str(post["karma"]), 
    icon_url="https://cdn3.iconfinder.com/data/icons/2018-social-media-logotypes/1000/2018_social_media_popular_app_logo_reddit-512.png")
    return embed

class api_cmds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
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
    async def reddit(self, ctx: SlashContext, subreddit: str = "", 
    sort: str = "", num_posts: int = 0) -> None:
        """
        Make a request to reddit for post data and format it to a discord embed 
        then send it.
        :param ctx: SlashContext object
        :param subreddit: Name of subreddit to get json from
        :param sort: The type of reddit post sorting to use
        :param num_posts: The number of posts to look through
        :return: None
        """
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
        except:
            await ctx.send("An unknown error occured.")

def setup(bot):
    bot.add_cog(api_cmds(bot))
