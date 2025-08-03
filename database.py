import aiosqlite
import logging
from typing import List, Tuple, Optional

DB_NAME = 'data/bot.db'

async def init_db():
    """Initializes the database and creates tables if they don't exist."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language_code TEXT,
                footer_text TEXT,
                is_premium INTEGER DEFAULT 0,
                premium_until TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE (channel_id, user_id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_posts (
                job_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                post_chat_id INTEGER NOT NULL,
                post_message_id INTEGER NOT NULL,
                target_channel_id INTEGER NOT NULL,
                caption TEXT,
                scheduled_time_utc TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id INTEGER PRIMARY KEY,
                posts_sent_this_month INTEGER DEFAULT 0,
                last_reset_date TEXT DEFAULT CURRENT_TIMESTAMP,
                total_posts_sent INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        await db.commit()
    logging.info("Database initialized with users, channels, scheduled_posts, and user_stats tables.")

# --- User Functions ---
async def add_or_update_user(user_id: int, language_code: str):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        if await cursor.fetchone():
            await db.execute('UPDATE users SET language_code = ? WHERE user_id = ?', (language_code, user_id))
        else:
            await db.execute('INSERT INTO users (user_id, language_code) VALUES (?, ?)', (user_id, language_code))
            # Initialize user stats
            await db.execute('INSERT INTO user_stats (user_id) VALUES (?)', (user_id,))
        await db.commit()

async def set_footer_text(user_id: int, footer_text: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE users SET footer_text = ? WHERE user_id = ?', (footer_text, user_id))
        await db.commit()

async def get_user_language(user_id: int) -> Optional[str]:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT language_code FROM users WHERE user_id = ?', (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else None

async def get_user_footer(user_id: int) -> Optional[str]:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT footer_text FROM users WHERE user_id = ?', (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else None

# --- Channel Functions ---
async def is_channel_registered(channel_id: int, user_id: int) -> bool:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT 1 FROM channels WHERE channel_id = ? AND user_id = ?', (channel_id, user_id))
        return await cursor.fetchone() is not None

async def add_channel(channel_id: int, user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT INTO channels (channel_id, user_id) VALUES (?, ?)', (channel_id, user_id))
        await db.commit()

async def get_user_channels(user_id: int) -> List[Tuple[int]]:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT channel_id FROM channels WHERE user_id = ?', (user_id,))
        return await cursor.fetchall()

# --- Scheduled Post Functions ---
async def add_scheduled_post(job_id: str, user_id: int, post_chat_id: int, post_message_id: int, target_channel_id: int, caption: Optional[str], scheduled_time_utc: str):
    """Adds a new scheduled post to the database."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO scheduled_posts (job_id, user_id, post_chat_id, post_message_id, target_channel_id, caption, scheduled_time_utc)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (job_id, user_id, post_chat_id, post_message_id, target_channel_id, caption, scheduled_time_utc))
        await db.commit()
        logging.info(f"Scheduled post with job_id {job_id} added to DB.")

async def get_scheduled_post(job_id: str) -> Optional[tuple]:
    """Retrieves a scheduled post by its job_id."""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT * FROM scheduled_posts WHERE job_id = ?', (job_id,))
        return await cursor.fetchone()

async def delete_scheduled_post(job_id: str):
    """Deletes a scheduled post from the database by its job_id."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM scheduled_posts WHERE job_id = ?', (job_id,))
        await db.commit()
        logging.info(f"Scheduled post with job_id {job_id} deleted from DB.")

async def remove_channel(channel_id: int, user_id: int):
    """Removes a channel from user's registered channels."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM channels WHERE channel_id = ? AND user_id = ?', (channel_id, user_id))
        await db.commit()
        logging.info(f"Channel {channel_id} removed for user {user_id}")

# --- Premium and Stats Functions ---
async def is_user_premium(user_id: int) -> bool:
    """Checks if user has premium access."""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT is_premium, premium_until FROM users WHERE user_id = ?', (user_id,))
        row = await cursor.fetchone()
        if not row:
            return False
        
        is_premium, premium_until = row
        if not is_premium:
            return False
            
        if premium_until:
            from datetime import datetime
            try:
                premium_date = datetime.fromisoformat(premium_until)
                return datetime.now() < premium_date
            except:
                return False
        return True

async def set_user_premium(user_id: int, premium_until: str = None):
    """Sets user as premium until specified date."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE users SET is_premium = 1, premium_until = ? WHERE user_id = ?', 
                        (premium_until, user_id))
        await db.commit()
        logging.info(f"User {user_id} set as premium until {premium_until}")

async def get_user_post_count_this_month(user_id: int) -> int:
    """Gets user's post count for current month."""
    from datetime import datetime
    current_month = datetime.now().strftime('%Y-%m')
    
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('''
            SELECT posts_sent_this_month, last_reset_date FROM user_stats WHERE user_id = ?
        ''', (user_id,))
        row = await cursor.fetchone()
        
        if not row:
            # Initialize stats for new user
            await db.execute('INSERT INTO user_stats (user_id) VALUES (?)', (user_id,))
            await db.commit()
            return 0
            
        posts_count, last_reset = row
        
        # Check if we need to reset monthly count
        if last_reset:
            try:
                last_reset_month = datetime.fromisoformat(last_reset).strftime('%Y-%m')
                if last_reset_month != current_month:
                    # Reset monthly count
                    await db.execute('''
                        UPDATE user_stats SET posts_sent_this_month = 0, last_reset_date = CURRENT_TIMESTAMP 
                        WHERE user_id = ?
                    ''', (user_id,))
                    await db.commit()
                    return 0
            except:
                pass
                
        return posts_count or 0

async def increment_user_post_count(user_id: int):
    """Increments user's post count."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            UPDATE user_stats 
            SET posts_sent_this_month = posts_sent_this_month + 1,
                total_posts_sent = total_posts_sent + 1
            WHERE user_id = ?
        ''', (user_id,))
        await db.commit()

async def can_user_send_post(user_id: int) -> tuple[bool, int]:
    """Checks if user can send a post. Returns (can_send, remaining_posts)."""
    from config import FREE_USER_POST_LIMIT, DEVELOPER_ID
    
    # Developer has unlimited access
    if user_id == DEVELOPER_ID:
        return True, -1
        
    # Premium users have unlimited access
    if await is_user_premium(user_id):
        return True, -1
        
    # Check free user limit
    current_posts = await get_user_post_count_this_month(user_id)
    remaining = FREE_USER_POST_LIMIT - current_posts
    
    return remaining > 0, remaining
