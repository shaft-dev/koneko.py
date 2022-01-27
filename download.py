# basically the embedding demo

from __future__ import unicode_literals
import youtube_dl
import os

class ytdlLogger(object):
    def debug(self, msg):
        # don't really care
        pass

    def warning(self, msg):
        # still don't care
        pass

    def error(self, msg):
        print(msg)

def get_vid_length(url: str = None) -> float:
    if not url:
        return
    ytdl = youtube_dl.YoutubeDL()
    info = ytdl.extract_info(url, download=False)
    duration = info["duration"]
    formats = info["formats"]
    format = formats[0]
    if format.get("filesize"):
        return duration, format.get("filesize")
    return duration, None

def download_vid(url: str = None, hook = None):
    if not url or not hook:
        return None
    opts = {
    "format": "mp4",
    'logger': ytdlLogger(),
    'progress_hooks': [hook],
    }
    with youtube_dl.YoutubeDL(opts) as ydl:
        return ydl.download([url])

def default_hook(dl):
    if dl["status"] == "finished":
        print("done")
