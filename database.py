import aiosqlite
import logging
from typing import List, Tuple

DB_NAME = 'bot.db'

async def init_db():
    """Initializes the database and creates tables if they don't exist."""
    async with aiosqlite.connect(DB_NAME) as db:
        # Create users table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language_code TEXT,
                footer_text TEXT
            )
        ''')
        # Create channels table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE (channel_id, user_id)
            )
        ''')
        await db.commit()
    logging.info("Database initialized with users and channels tables.")

async def add_or_update_user(user_id: int, language_code: str):
    """Adds a new user or updates their language code."""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        user_exists = await cursor.fetchone()
        if user_exists:
            await db.execute('UPDATE users SET language_code = ? WHERE user_id = ?', (language_code, user_id))
        else:
            await db.execute('INSERT INTO users (user_id, language_code) VALUES (?, ?)', (user_id, language_code))
        await db.commit()

async def set_footer_text(user_id: int, footer_text: str):
    """Sets or updates the footer text for a specific user."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE users SET footer_text = ? WHERE user_id = ?', (footer_text, user_id))
        await db.commit()

async def get_user_language(user_id: int) -> str | None:
    """Retrieves the language code for a specific user."""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT language_code FROM users WHERE user_id = ?', (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else None

async def is_channel_registered(channel_id: int, user_id: int) -> bool:
    """Checks if a channel is already registered by a specific user."""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT 1 FROM channels WHERE channel_id = ? AND user_id = ?', (channel_id, user_id))
        return await cursor.fetchone() is not None

async def add_channel(channel_id: int, user_id: int):
    """Adds a new channel for a user."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT INTO channels (channel_id, user_id) VALUES (?, ?)', (channel_id, user_id))
        await db.commit()
        logging.info(f"Added channel {channel_id} for user {user_id}.")

async def get_user_channels(user_id: int) -> List[Tuple[int]]:
    """Retrieves a list of all channels registered by a specific user."""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT channel_id FROM channels WHERE user_id = ?', (user_id,))
        return await cursor.fetchall()
