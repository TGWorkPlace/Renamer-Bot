import motor.motor_asyncio
import datetime
import logging
from config import Config
from .utils import send_log

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Database:
    def __init__(self, uri, database_name):
        try:
            self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
            self._client.server_info()  # This will raise an exception if the connection fails
            logging.info("Successfully connected to MongoDB")
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise e  # Re-raise the exception after logging it
        
        self.db = self._client[database_name]
        self.col = self.db.user

    def new_user(self, id):
        return dict(
            _id=int(id),
            join_date=datetime.date.today().isoformat(),
            file_id=None,
            caption=None,
            metadata=False,  # Changed to False by default
            metadata_code="Telegram : @Codeflix_Bots",
            format_template=None,
            media_type=None,
            title=None,  # Changed to None
            author=None,  # Changed to None
            artist=None,  # Changed to None
            audio=None,  # Changed to None
            subtitle=None,  # Changed to None
            video=None,  # Changed to None
            ban_status=dict(
                is_banned=False,
                ban_duration=0,
                banned_on=datetime.date.max.isoformat(),
                ban_reason=''
            )
        )

    async def add_user(self, b, m):
        u = m.from_user
        if not await self.is_user_exist(u.id):
            user = self.new_user(u.id)
            try:
                await self.col.insert_one(user)
                await send_log(b, u)
            except Exception as e:
                logging.error(f"Error adding user {u.id}: {e}")

    async def is_user_exist(self, id):
        try:
            user = await self.col.find_one({'_id': int(id)})
            return bool(user)
        except Exception as e:
            logging.error(f"Error checking if user {id} exists: {e}")
            return False

    async def total_users_count(self):
        try:
            count = await self.col.count_documents({})
            return count
        except Exception as e:
            logging.error(f"Error counting users: {e}")
            return 0

    async def get_all_users(self):
        try:
            all_users = self.col.find({})
            return all_users
        except Exception as e:
            logging.error(f"Error getting all users: {e}")
            return None

    async def remove_ban(self, id):
        try:
            ban_status = dict(
                is_banned=False,
                ban_duration=0,
                banned_on=datetime.date.max.isoformat(),
                ban_reason=''
            )
            await self.col.update_one({'_id': int(id)}, {'$set': {'ban_status': ban_status}})
        except Exception as e:
            logging.error(f"Error removing ban for user {id}: {e}")

    async def ban_user(self, user_id, ban_duration=0, ban_reason="No Reason"):
        try:
            ban_status = dict(
                is_banned=True,
                ban_duration=ban_duration,
                banned_on=datetime.date.today().isoformat(),
                ban_reason=ban_reason
            )
            await self.col.update_one({'_id': int(user_id)}, {'$set': {'ban_status': ban_status}})
        except Exception as e:
            logging.error(f"Error banning user {user_id}: {e}")

    async def get_ban_status(self, id):
        try:
            default = dict(
                is_banned=False,
                ban_duration=0,
                banned_on=datetime.date.max.isoformat(),
                ban_reason=''
            )
            user = await self.col.find_one({'_id': int(id)})
            if not user:
                return default
            return user.get('ban_status', default)
        except Exception as e:
            logging.error(f"Error getting ban status for user {id}: {e}")
            return dict(
                is_banned=False,
                ban_duration=0,
                banned_on=datetime.date.max.isoformat(),
                ban_reason=''
            )

    async def delete_user(self, user_id):
        try:
            await self.col.delete_many({'_id': int(user_id)})
        except Exception as e:
            logging.error(f"Error deleting user {user_id}: {e}")

    async def set_thumbnail(self, id, file_id):
        try:
            await self.col.update_one({'_id': int(id)}, {'$set': {'file_id': file_id}})
        except Exception as e:
            logging.error(f"Error setting thumbnail for user {id}: {e}")

    async def get_thumbnail(self, id):
        try:
            user = await self.col.find_one({'_id': int(id)})
            return user.get('file_id', None) if user else None
        except Exception as e:
            logging.error(f"Error getting thumbnail for user {id}: {e}")
            return None

    async def set_caption(self, id, caption):
        try:
            await self.col.update_one({'_id': int(id)}, {'$set': {'caption': caption}})
        except Exception as e:
            logging.error(f"Error setting caption for user {id}: {e}")

    async def get_caption(self, id):
        try:
            user = await self.col.find_one({'_id': int(id)})
            return user.get('caption', None) if user else None
        except Exception as e:
            logging.error(f"Error getting caption for user {id}: {e}")
            return None

    async def set_format_template(self, id, format_template):
        try:
            await self.col.update_one({'_id': int(id)}, {'$set': {'format_template': format_template}})
        except Exception as e:
            logging.error(f"Error setting format template for user {id}: {e}")

    async def get_format_template(self, id):
        try:
            user = await self.col.find_one({'_id': int(id)})
            return user.get('format_template', None) if user else None
        except Exception as e:
            logging.error(f"Error getting format template for user {id}: {e}")
            return None

    async def set_media_preference(self, id, media_type):
        try:
            await self.col.update_one({'_id': int(id)}, {'$set': {'media_type': media_type}})
        except Exception as e:
            logging.error(f"Error setting media preference for user {id}: {e}")

    async def get_media_preference(self, id):
        try:
            user = await self.col.find_one({'_id': int(id)})
            return user.get('media_type', None) if user else None
        except Exception as e:
            logging.error(f"Error getting media preference for user {id}: {e}")
            return None

    async def get_metadata(self, user_id):
        try:
            user = await self.col.find_one({'_id': int(user_id)})
            return user.get('metadata', False) if user else False  # Changed default to False
        except Exception as e:
            logging.error(f"Error getting metadata for user {user_id}: {e}")
            return False  # Changed default to False

    async def set_metadata(self, user_id, metadata):
        try:
            await self.col.update_one({'_id': int(user_id)}, {'$set': {'metadata': metadata}})
        except Exception as e:
            logging.error(f"Error setting metadata for user {user_id}: {e}")

    async def get_title(self, user_id):
        try:
            user = await self.col.find_one({'_id': int(user_id)})
            return user.get('title', None) if user else None  # Returns None instead of default
        except Exception as e:
            logging.error(f"Error getting title for user {user_id}: {e}")
            return None

    async def set_title(self, user_id, title):
        try:
            await self.col.update_one({'_id': int(user_id)}, {'$set': {'title': title}})
        except Exception as e:
            logging.error(f"Error setting title for user {user_id}: {e}")

    async def get_author(self, user_id):
        try:
            user = await self.col.find_one({'_id': int(user_id)})
            return user.get('author', None) if user else None  # Returns None instead of default
        except Exception as e:
            logging.error(f"Error getting author for user {user_id}: {e}")
            return None

    async def set_author(self, user_id, author):
        try:
            await self.col.update_one({'_id': int(user_id)}, {'$set': {'author': author}})
        except Exception as e:
            logging.error(f"Error setting author for user {user_id}: {e}")

    async def get_artist(self, user_id):
        try:
            user = await self.col.find_one({'_id': int(user_id)})
            return user.get('artist', None) if user else None  # Returns None instead of default
        except Exception as e:
            logging.error(f"Error getting artist for user {user_id}: {e}")
            return None

    async def set_artist(self, user_id, artist):
        try:
            await self.col.update_one({'_id': int(user_id)}, {'$set': {'artist': artist}})
        except Exception as e:
            logging.error(f"Error setting artist for user {user_id}: {e}")

    async def get_audio(self, user_id):
        try:
            user = await self.col.find_one({'_id': int(user_id)})
            return user.get('audio', None) if user else None  # Returns None instead of default
        except Exception as e:
            logging.error(f"Error getting audio for user {user_id}: {e}")
            return None

    async def set_audio(self, user_id, audio):
        try:
            await self.col.update_one({'_id': int(user_id)}, {'$set': {'audio': audio}})
        except Exception as e:
            logging.error(f"Error setting audio for user {user_id}: {e}")

    async def get_subtitle(self, user_id):
        try:
            user = await self.col.find_one({'_id': int(user_id)})
            return user.get('subtitle', None) if user else None  # Returns None instead of default
        except Exception as e:
            logging.error(f"Error getting subtitle for user {user_id}: {e}")
            return None

    async def set_subtitle(self, user_id, subtitle):
        try:
            await self.col.update_one({'_id': int(user_id)}, {'$set': {'subtitle': subtitle}})
        except Exception as e:
            logging.error(f"Error setting subtitle for user {user_id}: {e}")

    async def get_video(self, user_id):
        try:
            user = await self.col.find_one({'_id': int(user_id)})
            return user.get('video', None) if user else None  # Returns None instead of default
        except Exception as e:
            logging.error(f"Error getting video for user {user_id}: {e}")
            return None

    async def set_video(self, user_id, video):
        try:
            await self.col.update_one({'_id': int(user_id)}, {'$set': {'video': video}})
        except Exception as e:
            logging.error(f"Error setting video for user {user_id}: {e}")

codeflixbots = Database(Config.DB_URL, Config.DB_NAME)


db = Database(Config.DB_URL, Config.DB_NAME)
