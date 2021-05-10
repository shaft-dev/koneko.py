import discord
from api_requests import InvalidParams, BadRequest, get_reddit_posts
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
    
    @commands.command(name="reddit", aliases=["r", "red"])
    async def reddit_req(self, ctx: commands.Context, *args: list) -> None:
        """
        Make a request to reddit for json to format into a post to send to
        a text channel
        :param ctx: discord Context object
        :param args: A list of command arguments
        """
        if ctx.author.bot:
            return
        try:
            # this is horrendous
            passed = len(args)
            sub, s_type, limit = str(), str(), str()
            if passed >= 1:
                sub = sub.join(args[0])
            if passed >= 2:
                s_type = sub.join(args[1])
            if passed >= 3:
                limit = sub.join(args[2])
            posts = get_reddit_posts(sub, s_type, limit)
            post = choice(posts)
            # for some reason having an issue if i dont do == true/false
            if post["nsfw"] == True and ctx.channel.is_nsfw() == False:
                raise ChanNotNSFW
            embed = format_reddit_embed(post)
            embed.set_author(name="For: " + ctx.author.display_name, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        except BadRequest:
            await ctx.send("Something went wrong with the post request.")
        except InvalidParams:
            await ctx.send("Invalid parameters supplied to function.\
            \nFormat required: `reddit subreddit sort_type number_of_posts`")
        except ChanNotNSFW:
            await ctx.send("Post is nsfw. Try again in an nsfw channel or set this channel to nsfw.")
        except VideoUnsupported:
            await ctx.send("Post selected is of unsupported rich embed type `video`.")

def setup(bot):
    bot.add_cog(api_cmds(bot))
