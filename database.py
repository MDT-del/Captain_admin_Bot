import aiosqlite
import logging
from typing import List, Tuple, Optional

DB_NAME = 'bot.db'

async def init_db():
    """Initializes the database and creates tables if they don't exist."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language_code TEXT,
                footer_text TEXT
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
        await db.commit()
    logging.info("Database initialized with users, channels, and scheduled_posts tables.")

# --- User Functions ---
async def add_or_update_user(user_id: int, language_code: str):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        if await cursor.fetchone():
            await db.execute('UPDATE users SET language_code = ? WHERE user_id = ?', (language_code, user_id))
        else:
            await db.execute('INSERT INTO users (user_id, language_code) VALUES (?, ?)', (user_id,))
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
