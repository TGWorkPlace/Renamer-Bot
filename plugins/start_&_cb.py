"""
Apache License 2.0
Copyright (c) 2022 @PYRO_BOTZ

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
License Link : https://github.com/Codeflix-Bots/RenameBot/blob/main/LICENSE
"""

import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery
from helper.database import db
from config import Config, Txt  
  

@Client.on_message(filters.private & filters.command("start") & filters.user(Config.ADMIN))
async def start(client, message):
    user = message.from_user
    await db.add_user(client, message)                
    button = InlineKeyboardMarkup([[
        InlineKeyboardButton("👨‍💻 Dᴇᴠꜱ 👨‍💻", callback_data='dev')
        ],[
        InlineKeyboardButton('📯 Uᴩᴅᴀᴛᴇꜱ', url='https://t.me/codeflix_bots'),
        InlineKeyboardButton('💁‍♂️ Sᴜᴩᴩᴏʀᴛ', url='https://t.me/weebs_support')
        ],[
        InlineKeyboardButton('🎛️ Aʙᴏᴜᴛ', callback_data='about'),
        InlineKeyboardButton('🛠️ Hᴇʟᴩ', callback_data='help')
    ]])
    if Config.START_PIC:
        await message.reply_photo(Config.START_PIC, caption=Txt.START_TXT.format(user.mention), reply_markup=button)       
    else:
        await message.reply_text(text=Txt.START_TXT.format(user.mention), reply_markup=button, disable_web_page_preview=True)
   

@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data 
    if data == "start":
        await query.message.edit_text(
            text=Txt.START_TXT.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup = InlineKeyboardMarkup([[
                InlineKeyboardButton("👨‍💻 Dᴇᴠꜱ 👨‍💻", callback_data='dev')
                ],[
                InlineKeyboardButton('📯 Uᴩᴅᴀᴛᴇꜱ', url='https://t.me/codeflix_bots'),
                InlineKeyboardButton('💁‍♂️ Sᴜᴩᴩᴏʀᴛ', url='https://t.me/weebs_support')
                ],[
                InlineKeyboardButton('🎛️ Aʙᴏᴜᴛ', callback_data='about'),
                InlineKeyboardButton('🛠️ Hᴇʟᴩ', callback_data='help')
            ]])
        )
    elif data == "help":
        await query.message.edit_text(
            text=Txt.HELP_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                #⚠️ don't change source code & source link ⚠️ #
                InlineKeyboardButton("≛ ᴏᴡɴᴇʀ", url="https://t.me/sewxiy")
                ],[
                InlineKeyboardButton("🧐 ʀᴇᴘᴏʀᴛ ᴀʙᴜꜱᴇ", url='https://t.me/weebs_support')
                ],[
                InlineKeyboardButton("✗ Cʟᴏꜱᴇ", callback_data = "close"),
                InlineKeyboardButton("« Bᴀᴄᴋ", callback_data = "start")
            ]])            
        )
    elif data == "codeflix":
        await query.message.edit_text(
            text=Txt.ILLEGAL_TXT.format(client.mention),
            disable_web_page_preview = True,
            reply_markup=InlineKeyboardMarkup([[
                #⚠️ don't change source code & source link ⚠️ #
                InlineKeyboardButton("ᴍᴏᴠɪᴇ ʙᴏᴛ¹", url="https://t.me/lucy_filter_bot"),
                InlineKeyboardButton("ᴀɪ ʙᴏᴛ²", url="https://t.me/daisyprobot")           
                ],[
                InlineKeyboardButton("sᴇʀɪᴇs ғʟɪx", url="https://t.me/seriesflix_original")
                ],[
                InlineKeyboardButton("ᴍᴏᴠɪᴇ ғʟɪx", url="https://t.me/movieflix_original")
                ],[
                InlineKeyboardButton("✗ Cʟᴏꜱᴇ", callback_data = "close"),
                InlineKeyboardButton("« Bᴀᴄᴋ", callback_data = "start")
            ]])            
        )
    elif data == "about":
        await query.message.edit_text(
            text=Txt.ABOUT_TXT.format(client.mention),
            disable_web_page_preview = True,
            reply_markup=InlineKeyboardMarkup([[
                #⚠️ don't change source code & source link ⚠️ #
                InlineKeyboardButton("ᴏᴜʀ ʙᴏᴛꜱ", callback_data = "codeflix")
                ],[
                InlineKeyboardButton("✗ Cʟᴏꜱᴇ", callback_data = "close"),
                InlineKeyboardButton("Developer", callback_data = "dev")
            ]])            
        )
    elif data == "dev":
        await query.message.edit_text(
            text=Txt.DEV_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                #⚠️ don't change source code & source link ⚠️ #
                InlineKeyboardButton("≛ ᴏᴡɴᴇʀ", url="https://t.me/Illegal_Developer")
                ],[
                InlineKeyboardButton("🧐 ʀᴇᴘᴏʀᴛ ᴀʙᴜꜱᴇ", url="https://t.me/IllegalDeveloperBot")
                ],[
                InlineKeyboardButton("✗ Cʟᴏꜱᴇ", callback_data = "close"),
                InlineKeyboardButton("« Bᴀᴄᴋ", callback_data = "start")
            ]])          
        )
    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
            await query.message.continue_propagation()
        except:
            await query.message.delete()
            await query.message.continue_propagation()




