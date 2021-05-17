# koneko.py
An in-progress python (from lua) rewrite of a multipurpose discord bot.

## Current available commands (with syntax nyaa!command)
### nyaa!default_role
> Aliases: nyaa!def_role, nyaa!dr <br>
> Required arguments: `role name (case-sensitive)`
<p>Sets a role to give users upon joining. Limited to users with administrator priveleges</p>

### nyaa!role_react
> Aliases: nyaa!rr, nyaa!rr+ <br>
> Required arguments: `Emoji` `role name (case-sensitive)`
<p>If one doesn't already exist, creates a role reaction message in the current channel. Adds selected role to message and allows user to react with provided emoji to gain provided role in a guild.</p>

### nyaa!role_react_remove
> Aliases: nyaa!rrr, nyaa!rr- <br>
> Required arguments: `Emoji`
<p>If a role reaction is setup for provided emoji, removes role reaction from image. If no role reactions are left in message, deletes role reaction message.</p>

## Current available slash commands
### /ping
> No arguments
<p>Sends the current bot latency.</p>

### /reddit
> Required arguments: `subreddit`
> Optional arguments: `sort` `num_posts`
<p>Retrieves a post from specified subreddit and sends a message in embed format with post data.</p>
