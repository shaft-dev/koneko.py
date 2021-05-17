import requests
import json
from typing import List

class BadRequest(Exception):
    """
    Throw when a request fails
    """
    pass

class InvalidParams(Exception):
    """
    Throw for bad parameters passed to request function
    """
    pass

def get_reddit_posts(sub: str = "", type: str = "hot", limit: str = "20") -> List[dict]:
    """
    Takes in a subreddit, post type, and number of posts to look through and makes a request to reddit.
    :param sub: The subreddit name
    :param type: The sorting type
    :param limit: Number of posts to request. Limited to 75 max.
    :return: List of post information in dictionary format
    """
    # trying to do most edge checking before actual request happens
    type = type.lower()
    possible_types = ["hot", "top", "new", "controversial", "rising"]
    if type not in possible_types:
        type = "hot"
    # adjust for max and bad params passed
    try:
        j = int(limit)
        if j > 75:
            limit = "75"
        elif j < 20:
            limit = "20"
    except:
        limit = "20"
    if sub != "":
        try:
            # algorithms has made me hate string concatenation. dumbass O(n^2) operation
            req_url = "https://reddit.com/r/" + sub + "/" + type + "/.json?limit=" + limit
            j = requests.get(url=req_url, 
                headers={"user-agent": "Koneko.py v0.0.1"})
            parsed = json.loads(j.content)
            post_dict = parsed["data"]["children"]
            posts = list()
            for p in post_dict:
                post = p["data"]
                if not post["stickied"]:
                    to_append = {"text": post["selftext"], "op": post["author"], "title": post["title"], 
                    "karma": post["score"], "nsfw": post["over_18"], "text_post": post["is_self"], 
                    "link": "https://reddit.com" + post["permalink"], "content_url": post["url"], 
                    "thumbnail": post["thumbnail"]}
                    to_append["possible_type"] = ""
                    if "post_hint" in post:
                        to_append["possible_type"] = post["post_hint"]
                    posts.append(to_append)
            return posts
        except KeyError:
            print("Issue with creating data")
        except:
            raise BadRequest("Likely not a sub or other issue caught.")
    raise InvalidParams("Insufficient parameters supplied.")
