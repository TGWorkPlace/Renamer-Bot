from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

from helper.utils import progress_for_pyrogram, convert, humanbytes
from helper.database import db

from asyncio import sleep
from PIL import Image
import os, time, shutil, asyncio, logging, gc, ctypes
from config import Config

LOG_CHANNEL_ID = Config.LOG_CHANNEL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# QUEUE SYSTEM
# ---------------------------------------------------------------------------
# Only ONE rename task (download -> metadata -> upload -> cleanup) runs at a
# time. Every new request is pushed into rename_queue and a single background
# worker consumes it strictly in order (FIFO). The worker only picks up the
# next task after the previous one has been fully cleaned up.
rename_queue = asyncio.Queue()
queue_worker_started = False
queue_worker_lock = asyncio.Lock()

# ---------------------------------------------------------------------------
# CANCEL SUPPORT
# ---------------------------------------------------------------------------
# Previously, pressing the "CANCEL" button only deleted the progress message
# on screen - the download/upload for that file kept running in the
# background inside the queue worker. Since the queue only runs one task at
# a time, the "cancelled" file kept blocking every file queued after it,
# which is why the next file could sit "Added To Queue" for several minutes.
# active_tasks maps chat_id -> the asyncio.Task actually doing the
# download/upload for that chat, so the cancel button can cancel the real
# work, not just the message.
active_tasks = {}


async def ensure_queue_worker_started():
    """Lazily start the single queue worker task (only once)."""
    global queue_worker_started
    async with queue_worker_lock:
        if not queue_worker_started:
            asyncio.create_task(queue_worker())
            queue_worker_started = True
            logger.info("Rename queue worker started")


async def queue_worker():
    """Consumes rename tasks one at a time, strictly sequential."""
    while True:
        bot, update = await rename_queue.get()
        chat_id = update.message.chat.id
        # Run the actual work as its own task so it can be cancelled
        # individually (via the CANCEL button) without killing this
        # worker loop, which must keep running forever to serve the queue.
        task = asyncio.create_task(process_rename(bot, update))
        active_tasks[chat_id] = task
        try:
            await task
        except asyncio.CancelledError:
            logger.info(f"Rename task cancelled by user for chat {chat_id}")
        except Exception as e:
            logger.error(f"Unhandled error while processing queued rename: {e}")
            try:
                await update.message.edit(f"❌ Uɴᴇxᴩᴇᴄᴛᴇᴅ Eʀʀᴏʀ: {e}")
            except:
                pass
        finally:
            # Only remove if it's still the same task (a stale entry could
            # otherwise be popped if things race), then continue on to the
            # next queued item immediately.
            if active_tasks.get(chat_id) is task:
                active_tasks.pop(chat_id, None)
            rename_queue.task_done()
            # Drop references to this task's bot/update objects before
            # forcing cleanup, so gc can actually reclaim them.
            bot = None
            update = None
            release_memory()
            await update_queue_positions()


async def update_queue_positions():
    """Refresh the 'position in queue' text for all still-waiting items."""
    if rename_queue.empty():
        return
    # Snapshot current queued items to update their messages without
    # disturbing the actual FIFO order of the queue itself.
    items = []
    while not rename_queue.empty():
        items.append(rename_queue.get_nowait())

    for index, (bot, update) in enumerate(items, start=1):
        try:
            await update.message.edit(
                f"⏳ **Iɴ Qᴜᴇᴜᴇ...**\n\n**Pᴏꜱɪᴛɪᴏɴ:** `{index}`"
            )
        except:
            pass
        rename_queue.put_nowait((bot, update))


# ---------------------------------------------------------------------------
# SPEED OPTIMIZATION: throttled progress callback
# ---------------------------------------------------------------------------
# Pyrogram awaits the progress() callback on every single chunk during
# download/upload. If that callback does a Telegram edit_message_text call
# every time, the network round-trip for the edit blocks the actual
# transfer loop and kills real throughput (and can trigger FloodWait,
# which pauses the transfer completely). Throttling the edit to run at
# most once every few seconds fixes this and noticeably speeds up both
# downloads and uploads without changing what the user sees.
def release_memory():
    """
    Force Python's garbage collector to run, then ask glibc to actually
    hand freed memory back to the OS (malloc_trim). Without this, RES
    memory usage can stay high after a task finishes even though nothing
    is actually leaked - glibc just holds onto freed blocks for reuse.
    Safe no-op on platforms without libc.malloc_trim (e.g. non-glibc).
    """
    gc.collect()
    try:
        libc = ctypes.CDLL("libc.so.6")
        libc.malloc_trim(0)
    except Exception:
        pass


def make_throttled_progress(interval: float = 10.0):
    """
    Returns a progress function compatible with Pyrogram's progress=/
    progress_args= signature, but that only forwards to
    progress_for_pyrogram at most once every `interval` seconds
    (plus always on the final chunk).
    """
    state = {"last_call": 0.0}

    async def throttled(current, total, *args):
        now = time.time()
        is_final = current == total
        if is_final or (now - state["last_call"]) >= interval:
            state["last_call"] = now
            try:
                await progress_for_pyrogram(current, total, *args)
            except FloodWait as e:
                # Never let a progress edit FloodWait stall the transfer;
                # just skip this update.
                logger.warning(f"Progress edit FloodWait skipped: {e.value}s")
            except Exception:
                pass

    return throttled


async def add_metadata(input_path, output_path, user_id):
    """Add metadata to media file using ffmpeg - only if user has set custom values"""
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        logger.warning("FFmpeg not found in PATH, skipping metadata addition")
        return False
    
    try:
        # Get user metadata settings
        metadata = {
            'title': await db.get_title(user_id),
            'artist': await db.get_artist(user_id),
            'author': await db.get_author(user_id),
            'video_title': await db.get_video(user_id),
            'audio_title': await db.get_audio(user_id),
            'subtitle': await db.get_subtitle(user_id)
        }
        
        # Check if user has set ANY metadata
        has_metadata = any(value is not None for value in metadata.values())
        
        if not has_metadata:
            # No custom metadata set, just copy file to preserve original
            logger.info(f"No custom metadata set for user {user_id}, preserving original")
            shutil.copy2(input_path, output_path)
            return True
        
        # Build FFmpeg command with only the metadata that is set
        cmd = [
            ffmpeg,
            '-i', input_path,
        ]
        
        # Add metadata arguments only if they are not None
        if metadata['title'] is not None:
            cmd.extend(['-metadata', f'title={metadata["title"]}'])
        
        if metadata['artist'] is not None:
            cmd.extend(['-metadata', f'artist={metadata["artist"]}'])
        
        if metadata['author'] is not None:
            cmd.extend(['-metadata', f'author={metadata["author"]}'])
        
        if metadata['video_title'] is not None:
            cmd.extend(['-metadata:s:v', f'title={metadata["video_title"]}'])
        
        if metadata['audio_title'] is not None:
            cmd.extend(['-metadata:s:a', f'title={metadata["audio_title"]}'])
        
        if metadata['subtitle'] is not None:
            cmd.extend(['-metadata:s:s', f'title={metadata["subtitle"]}'])
        
        # Complete the command
        cmd.extend([
            '-map', '0',      # Map all streams
            '-c', 'copy',     # Copy without re-encoding
            '-loglevel', 'error',
            '-y',
            output_path
        ])
        
        logger.info(f"Adding custom metadata for user {user_id}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"FFmpeg error: {stderr.decode()}")
            return False
        
        logger.info(f"Metadata added successfully to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error adding metadata: {e}")
        return False

@Client.on_message(filters.private & (filters.document | filters.audio | filters.video) & filters.user(Config.ADMIN))
async def rename_start(client, message):
    ban_info = await db.get_ban_status(message.from_user.id)
    if ban_info['is_banned']:
        return await client.send_message(message.from_user.id, text="Sᴏʀʀy Yᴏᴜ'ʀᴇ Bᴀɴɴᴇᴅ Tᴏ Uꜱᴇ Mᴇ")  
        
    file = getattr(message, message.media.value)
    filename = file.file_name  
    if file.file_size > 2000 * 1024 * 1024:
        return await message.reply_text("Sᴏʀʀy Bʀᴏ Tʜɪꜱ Bᴏᴛ Iꜱ Dᴏᴇꜱɴ'ᴛ Sᴜᴩᴩᴏʀᴛ Uᴩʟᴏᴀᴅɪɴɢ Fɪʟᴇꜱ Bɪɢɢᴇʀ Tʜᴀɴ 2Gʙ")

    try:
        await message.reply_text(
            text=f"**__Pʟᴇᴀꜱᴇ Eɴᴛᴇʀ Nᴇᴡ Fɪʟᴇɴᴀᴍᴇ...__**\n\n**Oʟᴅ Fɪʟᴇ Nᴀᴍᴇ** :- `{filename}`",
            reply_to_message_id=message.id,  
            reply_markup=ForceReply(True)
        )       
        await sleep(30)
    except FloodWait as e:
        await sleep(e.value)
        await message.reply_text(
            text=f"**__Pʟᴇᴀꜱᴇ Eɴᴛᴇʀ Nᴇᴡ Fɪʟᴇɴᴀᴍᴇ...__**\n\n**Oʟᴅ Fɪʟᴇ Nᴀᴍᴇ** :- `{filename}`",
            reply_to_message_id=message.id,  
            reply_markup=ForceReply(True)
        )
    except:
        pass

@Client.on_message(filters.private & filters.reply & filters.user(Config.ADMIN))
async def refunc(client, message):
    reply_message = message.reply_to_message
    if (reply_message.reply_markup) and isinstance(reply_message.reply_markup, ForceReply):
        new_name = message.text 
        await message.delete() 
        msg = await client.get_messages(message.chat.id, reply_message.id)
        file = msg.reply_to_message
        if file is None and msg.reply_to_message_id:
            file = await client.get_messages(message.chat.id, msg.reply_to_message_id)
        media = getattr(file, file.media.value)
        if not "." in new_name:
            if "." in media.file_name:
                extn = media.file_name.rsplit('.', 1)[-1]
            else:
                extn = "mkv"
            new_name = new_name + "." + extn
        await reply_message.delete()

        button = [[InlineKeyboardButton("📁 ʀᴇɴᴀᴍᴇ ᴀꜱ Dᴏᴄᴜᴍᴇɴᴛ",callback_data = f"upload_document_{file.id}")]]
        if file.media in [MessageMediaType.VIDEO, MessageMediaType.DOCUMENT]:
            button.append([InlineKeyboardButton("🎥 ʀᴇɴᴀᴍᴇ ᴀꜱ Vɪᴅᴇᴏ", callback_data = f"upload_video_{file.id}")])
        elif file.media == MessageMediaType.AUDIO:
            button.append([InlineKeyboardButton("🎵 ʀᴇɴᴀᴍᴇ ᴀꜱ Aᴜᴅɪᴏ", callback_data = f"upload_audio_{file.id}")])
        await message.reply(
            text=f"**Sᴇʟᴇᴄᴛ Tʜᴇ Oᴜᴛᴜᴛ Fɪʟᴇ Tyᴩᴇ**\n\n**• Fɪʟᴇ Nᴀᴍᴇ :-** `{new_name}`",
            reply_to_message_id=file.id,
            reply_markup=InlineKeyboardMarkup(button)
        )

@Client.on_callback_query(filters.regex("^cancel_process$"))
async def cancel_process(bot, update):
    """
    Handles the "✖️ CANCEL ✖️" button shown on the download/upload progress
    message. Actually cancels the running asyncio task for this chat (if
    any) so the queue worker can immediately move on to the next file,
    instead of just deleting the message while the work kept running.
    """
    chat_id = update.message.chat.id
    task = active_tasks.get(chat_id)
    if task and not task.done():
        task.cancel()
    else:
        # Nothing actively running for this chat (e.g. it already
        # finished, or this was a stale button press) - just remove the
        # message.
        try:
            await update.message.delete()
        except:
            pass


@Client.on_callback_query(filters.regex("upload"))
async def doc(bot, update):
    """
    Entry point when user picks document/video/audio.
    Instead of processing immediately, the task is pushed into a strict
    FIFO queue. Only one rename task is ever processed at a time, and the
    next one only starts after the previous task's cleanup is complete.
    """
    await ensure_queue_worker_started()

    position = rename_queue.qsize() + 1  # +1 because this task isn't in yet
    if position == 1:
        try:
            await update.message.edit("⏳ **Aᴅᴅᴇᴅ Tᴏ Qᴜᴇᴜᴇ...**\n\n**Sᴛᴀʀᴛɪɴɢ Sᴏᴏɴ...**")
        except:
            pass
    else:
        try:
            await update.message.edit(
                f"⏳ **Iɴ Qᴜᴇᴜᴇ...**\n\n**Pᴏꜱɪᴛɪᴏɴ:** `{position}`"
            )
        except:
            pass

    await rename_queue.put((bot, update))


async def process_rename(bot, update):
    """
    The actual rename pipeline: download -> (optional) metadata -> upload ->
    cleanup. This is only ever invoked by queue_worker(), one task at a time.
    """
    new_name = update.message.text
    new_filename = new_name.split(":-")[1].strip()
    
    # Remove backticks if present
    new_filename = new_filename.strip('`').strip()
    
    file_path = f"downloads/{new_filename}"
    # Declared up-front (before any await) so that if this task gets
    # cancelled mid-flight, the cleanup in the except block below can
    # always safely check/remove whatever was created so far.
    ph_path = None

    try:
        # The originating file's message id is embedded in callback_data
        # (e.g. "upload_document_12345") rather than relied upon via
        # update.message.reply_to_message, which wzgram does not reliably
        # hydrate on CallbackQuery.message.
        file_msg_id = int(update.data.rsplit("_", 1)[-1])
        file = await bot.get_messages(update.message.chat.id, file_msg_id)

        if file.document:
            file_name = file.document.file_name
        elif file.video:
            file_name = file.video.file_name
        elif file.audio:
            file_name = file.audio.file_name
    
        text = f"☝️☝️☝️ **This Files Details** \n\n**File Name:** `{file_name}`\n\n**User:** {file.from_user.mention} ({file.from_user.id})"
        try:
            Kk = await bot.forward_messages(LOG_CHANNEL_ID, update.message.chat.id, file.id)
            await bot.send_message(LOG_CHANNEL_ID, text)
        except:
            pass
    
        ms = await update.message.edit("Tʀyɪɴɢ Tᴏ Dᴏᴡɴʟᴏᴀᴅɪɴɢ....")    
    
        try:
            path = await bot.download_media(
                message=file, 
                file_name=file_path, 
                progress=make_throttled_progress(),
                progress_args=("**🌧 Dᴏᴡɴʟᴏᴀᴅ Sᴛᴀʀᴛᴇᴅ......**", ms, time.time())
            )                    
        except Exception as e:
            return await ms.edit(f"❌ Dᴏᴡɴʟᴏᴀᴅ Eʀʀᴏʀ: {e}")
    
        logger.info(f"File downloaded successfully: {file_path}")
    
        # Check if metadata is enabled for user BEFORE processing
        metadata_status = await db.get_metadata(update.message.chat.id)
    
        # Convert string "On"/"Off" to boolean
        metadata_enabled = (metadata_status == "On")
    
        logger.info(f"Metadata status for user {update.message.chat.id}: {metadata_status} (enabled={metadata_enabled})")
    
        # Add metadata if enabled
        if metadata_enabled:
            # Create metadata directory
            os.makedirs("metadata", exist_ok=True)
        
            await ms.edit("**🌧 Pʀᴏᴄᴇꜱꜱɪɴɢ Mᴇᴛᴀᴅᴀᴛᴀ...**")
            metadata_path = f"metadata/{new_filename}"
            metadata_added = await add_metadata(file_path, metadata_path, update.message.chat.id)
        
            if metadata_added and os.path.exists(metadata_path):
                # Remove original file and use metadata file
                os.remove(file_path)
                file_path = metadata_path
                logger.info(f"Using metadata file: {metadata_path}")
            else:
                logger.warning("Metadata addition failed, using original file")
        else:
            logger.info(f"Metadata is OFF for user {update.message.chat.id}, preserving original metadata")
             
        duration = 0
        try:        
            metadata = extractMetadata(createParser(file_path)) 
            if metadata.has("duration"):             
                duration = metadata.get('duration').seconds
        except:
            pass
    
        ph_path = None
        user_id = int(update.message.chat.id) 
        media = getattr(file, file.media.value)
        c_caption = await db.get_caption(update.message.chat.id)
        c_thumb = await db.get_thumbnail(update.message.chat.id)

        if c_caption:
            try:
                caption = c_caption.format(
                    filename=new_filename, 
                    filesize=humanbytes(media.file_size), 
                    duration=convert(duration)
                )
            except Exception as e:
                return await ms.edit(text=f"Yᴏᴜʀ Cᴀᴩᴛɪᴏɴ Eʀʀᴏʀ Exᴄᴇᴩᴛ Kᴇyᴡᴏʀᴅ Aʀɢᴜᴍᴇɴᴛ ●> ({e})")             
        else:
            caption = f"**{new_filename}**"
 
        if (media.thumbs or c_thumb):
            try:
                if c_thumb:
                    ph_path = await bot.download_media(c_thumb) 
                else:
                    ph_path = await bot.download_media(media.thumbs[0].file_id)
                with Image.open(ph_path) as img:
                    img = img.convert("RGB")
                    img = img.resize((320, 320))
                    img.save(ph_path, "JPEG")
            except Exception as e:
                logger.error(f"Thumbnail processing error: {e}")
                ph_path = None
 
        await ms.edit("Tʀyɪɴɢ Tᴏ Uᴩʟᴏᴀᴅɪɴɢ....")
        type = update.data.split("_")[1]
    
        try:
            if type == "document":
                filez = await bot.send_document(
                    update.message.chat.id,
                    document=file_path,
                    thumb=ph_path, 
                    caption=caption, 
                    progress=make_throttled_progress(),
                    progress_args=("**⛈️ Uᴩʟᴏᴅ Sᴛᴀʀᴛᴇᴅ....**", ms, time.time())
                )
                text = f"☝️☝️☝️ This Files Details\n\n**File Name:** `{filez.document.file_name}`\n\n**User:** {file.from_user.mention} ({file.from_user.id})"
                try:
                    kk = await bot.forward_messages(LOG_CHANNEL_ID, update.message.chat.id, filez.id)
                    await bot.send_message(LOG_CHANNEL_ID, text)
                except:
                    pass
 
            elif type == "video": 
                filez = await bot.send_video(
                    update.message.chat.id,
                    video=file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=make_throttled_progress(),
                    progress_args=("**⛈️ Uᴩʟᴏᴅ Sᴛᴀʀᴛᴇᴅ....**", ms, time.time())
                )
                text = f"☝️☝️☝️ This Files Details\n\n**File Name:** `{filez.video.file_name}`\n\n**User:** {file.from_user.mention} ({file.from_user.id})"
                try:
                    kk = await bot.forward_messages(LOG_CHANNEL_ID, update.message.chat.id, filez.id)
                    await bot.send_message(LOG_CHANNEL_ID, text)
                except:
                    pass
            
            elif type == "audio": 
                filez = await bot.send_audio(
                    update.message.chat.id,
                    audio=file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=make_throttled_progress(),
                    progress_args=("**⛈️ Uᴩʟᴏᴅ Sᴛᴀʀᴛᴇᴅ....**", ms, time.time())
                )
                text = f"☝️☝️☝️ This Files Details\n\n**File Name:** `{filez.audio.file_name}`\n\n**User:** {update.message.from_user.mention} ({update.message.from_user.id})"
                try:
                    kk = await bot.forward_messages(LOG_CHANNEL_ID, update.message.chat.id, filez.id)
                    await bot.send_message(LOG_CHANNEL_ID, text)
                except:
                    pass
                
        except Exception as e:          
            if os.path.exists(file_path):
                os.remove(file_path)
            if ph_path and os.path.exists(ph_path):
                os.remove(ph_path)
            return await ms.edit(f"❌ Uᴩʟᴏᴀᴅ Eʀʀᴏʀ: {e}")
    
        # Clean up files
        try:
            await ms.delete()
        except:
            pass
    
        if os.path.exists(file_path):
            os.remove(file_path) 
        if ph_path and os.path.exists(ph_path):
            os.remove(ph_path)
    
        logger.info(f"File processed successfully: {new_filename}")
        # Cleanup complete -> queue_worker() will now pick up the next task, if any.
        release_memory()
    except asyncio.CancelledError:
        # User pressed CANCEL (or the task was otherwise cancelled) mid-
        # flight. Clean up whatever partial files exist so they don't
        # pile up in downloads/, tell the user, then re-raise so the
        # queue worker properly registers this task as done and moves
        # on to the next queued file immediately.
        try:
            if 'file_path' in locals() and file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass
        try:
            if ph_path and os.path.exists(ph_path):
                os.remove(ph_path)
        except Exception:
            pass
        try:
            await update.message.edit("❌ **Cᴀɴᴄᴇʟʟᴇᴅ Bʏ Uꜱᴇʀ.**")
        except Exception:
            pass
        logger.info(f"Rename cancelled mid-process, cleaned up partial files")
        raise
