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

def setup(bot):
    bot.add_cog(api_cmds(bot))
