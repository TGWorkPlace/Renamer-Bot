"""
Apache License 2.0
Copyright (c) 2022 @Codeflix_bots
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
Telegram Link : https://t.me/codeflix_bots
Repo Link : https://github.com/Codeflix-Bots/RenameBot
License Link :https://github.com/Codeflix-Bots/RenameBot/blob/main/LICENSE
"""

import re, os, time

id_pattern = re.compile(r'^.\d+$') 

class Config(object):
    # pyro client config
    API_ID    = os.environ.get("API_ID", "")
    API_HASH  = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "") 
   
    # database config
    DB_NAME = os.environ.get("DB_NAME","Cluster0")     
    DB_URL  = os.environ.get("DB_URL","")
 
    # other configs
    BOT_UPTIME  = time.time()
    START_PIC   = os.environ.get("START_PIC", "https://i.ibb.co/CpJ6G6kR/IMG-20251124-191548-741.jpg")
    ADMIN       = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '7721895501 8994051611').split()]
    FORCE_SUB   = os.environ.get("FORCE_SUB", "") 
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1003328703303"))

    # wes response configuration     
    WEBHOOK = bool(os.environ.get("WEBHOOK", "True"))


class Txt(object):
    # part of text configuration
    START_TXT = """<b>Há´€Éª {} ðŸ‘‹,
    
âž» TÊœÉªs Is AÉ´ Aá´…á´ á´€É´á´„á´‡á´… AÉ´á´… Yá´‡á´› Pá´á´¡á´‡Ê€êœ°á´œÊŸ ÉªÊŸÊŸá´‡É¢á´€ÊŸ Rá´‡É´á´€á´á´‡ Bá´á´›.
âž» UsÉªÉ´É¢ TÊœÉªs Bá´á´› Yá´á´œ Cá´€É´ Rá´‡É´á´€á´á´‡ & CÊœá´€É´É¢á´‡ TÊœá´œá´Ê™É´á´€ÉªÊŸ Oêœ° Yá´á´œÊ€ FÉªÊŸá´‡.
âž» Yá´á´œ Cá´€É´ AÊŸsá´ Cá´É´á´ á´‡Ê€á´› VÉªá´…á´‡á´ Tá´ FÉªÊŸá´‡ & FÉªÊŸá´‡ Tá´ VÉªá´…á´‡á´.
âž» TÊœÉªs Bá´á´› AÊŸêœ±á´ Sá´œá´˜á´˜á´Ê€á´›s Cá´œsá´›á´á´ TÊœá´œá´Ê™É´á´€ÉªÊŸ AÉ´á´… Cá´œsá´›á´á´ Cá´€á´˜á´›Éªá´É´.

ðŸ’º TÊœÉªs Bá´á´› Wá´€s CÊ€á´‡á´€á´›á´‡á´… BÊ : @Codeflix_Bots ðŸ’ž</b>"""

    ILLEGAL_TXT = """<b>Êœá´‡Ê€á´‡ Éªêœ± á´á´œÊ€ á´€ÊŸÊŸ Ê™á´á´› ÊŸÉªêœ±á´›</b>"""
    
    ABOUT_TXT = """<b>â•­â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€âŸ
â”œðŸ¤– á´y É´á´€á´á´‡ : {}
â”œðŸ–¥ï¸ Dá´‡á´ á´‡ÊŸá´á´©á´‡Ê€êœ± : <a href=https://t.me/codeflix_bots>**á´„á´á´…á´‡Ò“ÊŸÉªx Ê™á´á´›s**</a> ðŸ•·
â”œðŸ‘¨â€ðŸ’» PÊ€á´É¢Ê€á´€á´á´‡Ê€ : **á´Éªá´‹á´‡Ê**
â•°â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€âŸ </b>"""

    HELP_TXT = """
ðŸŒŒ <b><u>Há´á´¡ Tá´ Sá´‡á´› TÊœá´œá´Ê™É´ÉªÊŸá´‡</u></b>
  
<b>â€¢Â»</b> /start TÊœá´‡ Bá´á´› AÉ´á´… Sá´‡É´á´… AÉ´y PÊœá´á´›á´ Tá´ Aá´œá´›á´á´á´€á´›Éªá´„á´€ÊŸÊŸy Sá´‡á´› TÊœá´œá´Ê™É´ÉªÊŸá´‡.
<b>â€¢Â»</b> /del_thumb Uêœ±á´‡ TÊœÉªêœ± Cá´á´á´á´€É´á´… Tá´ Dá´‡ÊŸá´‡á´›á´‡ Yá´á´œÊ€ OÊŸá´… TÊœá´œá´Ê™É´ÉªÊŸá´‡.
<b>â€¢Â»</b> /view_thumb Uêœ±á´‡ TÊœÉªêœ± Cá´á´á´á´€É´á´… Tá´ VÉªá´‡á´¡ Yá´á´œÊ€ Cá´œÊ€Ê€á´‡É´á´› TÊœá´œá´Ê™É´ÉªÊŸá´‡.

ðŸ“‘ <b><u>Há´á´¡ Tá´ Sá´‡á´› Cá´œêœ±á´›á´á´ Cá´€á´©á´›Éªá´É´</u></b>

<b>â€¢Â»</b> /set_caption - Uêœ±á´‡ TÊœÉªêœ± Cá´á´á´á´€É´á´… Tá´ Sá´‡á´› á´€ Cá´œêœ±á´›á´á´ Cá´€á´©á´›Éªá´É´.
<b>â€¢Â»</b> /see_caption - Uêœ±á´‡ TÊœÉªêœ± Cá´á´á´á´€É´á´… Tá´ VÉªá´‡á´¡ Yá´á´œÊ€ Cá´œêœ±á´›á´á´ Cá´€á´©á´›Éªá´É´.
<b>â€¢Â»</b> /del_caption - Uêœ±á´‡ TÊœÉªêœ± Cá´á´á´á´€É´á´… Tá´ Dá´‡ÊŸá´‡á´›á´‡ Yá´á´œÊ€ Cá´œêœ±á´›á´á´ Cá´€á´©á´›Éªá´É´.

Exá´€á´á´©ÊŸá´‡:- /set_caption ðŸ“• FÉªÊŸá´‡ Ná´€á´á´‡: {filename}
ðŸ’¾ SÉªá´¢á´‡: {filesize}
â° Dá´œÊ€á´€á´›Éªá´É´: {duration}

âœï¸ <b><u>Há´á´¡ Tá´ Rá´‡É´á´€á´á´‡ A FÉªÊŸá´‡</u></b>

<b>â€¢Â»</b> Sá´‡É´á´… AÉ´y FÉªÊŸá´‡ AÉ´á´… Tyá´©á´‡ Ná´‡á´¡ FÉªÊŸá´‡ NÉ´á´€á´á´‡ \nAÉ´á´… Aá´‡ÊŸá´‡á´„á´› TÊœá´‡ Fá´Ê€á´á´€á´› [ document, video, audio ].           

â„¹ï¸ ð—”ð—»ð˜† ð—¢ð˜ð—µð—²ð—¿ ð—›ð—²ð—¹ð—½ ð—–ð—¼ð—»ð˜ð—®ð—°ð˜ :- <a href=https://t.me/IllegalDeveloperBot>ð˜½ð™¤ð™© ð˜¿ð™šð™«ð™šð™¡ð™¤ð™¥ð™šð™§</a>
"""

#âš ï¸ Dá´É´'á´› Rá´‡á´á´á´ á´‡ Oá´œÊ€ CÊ€á´‡á´…Éªá´›êœ± https://github.com/Codeflix-BotsðŸ™ðŸ¥²
    DEV_TXT = """<b><u>Sá´©á´‡á´„Éªá´€ÊŸ TÊœá´€É´á´‹êœ± & Dá´‡á´ á´‡ÊŸá´á´©á´‡Ê€êœ±</b></u>
Â»<a href=https://t.me/codeflix_bots>**Codeflix bots**</a>ðŸ•·
Â»**Kunal Singh â™¡**"""

    PROGRESS_BAR = """<b>\n
â•­â•â•â•â• âš¡ï¸ Sá´›á´€á´›s âš¡ï¸ â•â•â•â•â•®
â”‚ ðŸ’  SÉªá´¢á´‡   : {1} / {2}
â”‚ ðŸŽ¯ Dá´É´á´‡   : {0}%
â”‚ âš¡ Sá´˜á´‡á´‡á´… : {3}/s
â”‚ ðŸ•’ Eá´›á´€    : {4}
â•°â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•¯ </b>"""
    
    SEND_METADATA = """
<b>--Metadata Settings:--</b>

âžœ /metadata: Turn on or off metadata.

<b>Description</b> : Metadata will change MKV video files including all audio, streams, and subtitle titles."""
   
    META_TXT = """
**á´á´€É´á´€É¢ÉªÉ´É¢ á´á´‡á´›á´€á´…á´€á´›á´€ Ò“á´Ê€ Êá´á´œÊ€ á´ Éªá´…á´‡á´s á´€É´á´… Ò“ÉªÊŸá´‡s**

**á´ á´€Ê€Éªá´á´œêœ± á´á´‡á´›á´€á´…á´€á´›á´€:**

- **á´›Éªá´›ÊŸá´‡**: Descriptive title of the media.
- **á´€á´œá´›Êœá´Ê€**: The creator or owner of the media.
- **á´€Ê€á´›Éªêœ±á´›**: The artist associated with the media.
- **á´€á´œá´…Éªá´**: Title or description of audio content.
- **êœ±á´œÊ™á´›Éªá´›ÊŸá´‡**: Title of subtitle content.
- **á´ Éªá´…á´‡á´**: Title or description of video content.

**á´„á´á´á´á´€É´á´…êœ± á´›á´ á´›á´œÊ€É´ á´É´ á´Ò“Ò“ á´á´‡á´›á´€á´…á´€á´›á´€:**
âžœ /metadata: Turn on or off metadata.

**á´„á´á´á´á´€É´á´…êœ± á´›á´ êœ±á´‡á´› á´á´‡á´›á´€á´…á´€á´›á´€:**

âžœ /settitle: Set a custom title of media.
âžœ /setauthor: Set the author.
âžœ /setartist: Set the artist.
âžœ /setaudio: Set audio title.
âžœ /setsubtitle: Set subtitle title.
âžœ /setvideo: Set video title.

**á´‡xá´€á´á´˜ÊŸá´‡:** /settitle Your Title Here

**á´œêœ±á´‡ á´›Êœá´‡êœ±á´‡ á´„á´á´á´á´€É´á´…êœ± á´›á´ á´‡É´Ê€Éªá´„Êœ Êá´á´œÊ€ á´á´‡á´…Éªá´€ á´¡Éªá´›Êœ á´€á´…á´…Éªá´›Éªá´É´á´€ÊŸ á´á´‡á´›á´€á´…á´€á´›á´€ ÉªÉ´êœ°á´Ê€á´á´€á´›Éªá´É´!**
"""



´‡ á´›Êœá´‡êœ±á´‡ á´„á´á´á´á´€É´á´…êœ± á´›á´ á´‡É´Ê€Éªá´„Êœ Êá´á´œÊ€ á´á´‡á´…Éªá´€ á´¡Éªá´›Êœ á´€á´…á´…Éªá´›Éªá´É´á´€ÊŸ á´á´‡á´›á´€á´…á´€á´›á´€ ÉªÉ´êœ°á´Ê€á´á´€á´›Éªá´É´!**
"""



