from datetime import datetime
from pytz import timezone
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from config import Config
from aiohttp import web
from route import web_server
from pyrogram import utils as pyroutils
import asyncio
import gc
import os
import sys

# Netlify sets CI=true; you can also check NETLIFY or another env var you set
if os.environ.get("NETLIFY") or os.environ.get("CI"):
    print("Skipping bot run in build environment.")
    sys.exit(0)

# file_rename.py already forces a manual gc.collect() + malloc_trim right
# after every download/upload task finishes (see release_memory() there),
# which is when memory actually needs reclaiming. Raising the automatic
# collector's thresholds means it fires less often in between those points,
# trading a bit of GC precision for noticeably less CPU spent on collections
# that mostly just re-scan long-lived objects (the Client, DB connections,
# plugin modules) for no gain.
gc.set_threshold(50000, 50, 50)

asyncio.set_event_loop(asyncio.new_event_loop())

pyroutils.MIN_CHAT_ID = -999999999999
pyroutils.MIN_CHANNEL_ID = -100999999999999

class Bot(Client):

    def __init__(self):
        super().__init__(
            name="renamer",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            # Lowered from 200 -> 4. 200 dispatcher workers were kept alive
            # permanently and were a big chunk of the idle/baseline memory
            # footprint. This bot only ever has ONE admin and processes
            # renames one-at-a-time through its own queue, so 4 workers is
            # already more than enough headroom and frees up RAM that Koyeb
            # was reporting as 100%.
            workers=1,
            plugins={"root": "plugins"},
            sleep_threshold=15,
            # Each concurrent transmission holds its own chunk buffers in
            # memory. Since file_rename.py already serializes all
            # downloads/uploads through a single-task queue, there's only
            # ever one active transfer at a time - so a high value here just
            # burns RAM on buffers with nothing else to use them
            # concurrently. Lowered from 4 -> 2 to shrink peak memory during
            # large (up to 2GB) file transfers, while still splitting each
            # transfer across a couple of connections for decent speed.
            max_concurrent_transmissions=2,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username  
        self.uptime = Config.BOT_UPTIME     
        if Config.WEBHOOK:
            app = web.AppRunner(await web_server())
            await app.setup()       
            await web.TCPSite(app, "0.0.0.0", 8080).start()     
        print(f"{me.first_name} Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️")
        for id in Config.ADMIN:
            try: await self.send_message(id, f"**__{me.first_name}  Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️__**")                                
            except: pass
        if Config.LOG_CHANNEL:
            try:
                curr = datetime.now(timezone("Asia/Kolkata"))
                date = curr.strftime('%d %B, %Y')
                time = curr.strftime('%I:%M:%S %p')
                await self.send_message(Config.LOG_CHANNEL, f"**__{me.mention} Iꜱ Rᴇsᴛᴀʀᴛᴇᴅ !!**\n\n📅 Dᴀᴛᴇ : `{date}`\n⏰ Tɪᴍᴇ : `{time}`\n🌐 Tɪᴍᴇᴢᴏɴᴇ : `Asia/Kolkata`\n\n🉐 Vᴇʀsɪᴏɴ : `v{__version__} (Layer {layer})`</b>")                                
            except:
                print("Pʟᴇᴀꜱᴇ Mᴀᴋᴇ Tʜɪꜱ Iꜱ Aᴅᴍɪɴ Iɴ Yᴏᴜʀ Lᴏɢ Cʜᴀɴɴᴇʟ")

Bot().run()
