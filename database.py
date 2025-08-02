import aiosqlite
import logging

DB_NAME = 'bot.db'

async def init_db():
    """Initializes the database and creates the users table if it doesn't exist."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language_code TEXT,
                footer_text TEXT
            )
        ''')
        await db.commit()
    logging.info("Database initialized.")

async def add_or_update_user(user_id: int, language_code: str):
    """Adds a new user or updates their language code."""
    async with aiosqlite.connect(DB_NAME) as db:
        # Check if user exists
        cursor = await db.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        user_exists = await cursor.fetchone()

        if user_exists:
            # Update language code if user exists
            await db.execute('UPDATE users SET language_code = ? WHERE user_id = ?', (language_code, user_id))
            logging.info(f"Updated language for user {user_id} to {language_code}.")
        else:
            # Insert new user if they don't exist
            await db.execute('INSERT INTO users (user_id, language_code) VALUES (?, ?)', (user_id, language_code))
            logging.info(f"Added new user {user_id} with language {language_code}.")

        await db.commit()

async def set_footer_text(user_id: int, footer_text: str):
    """Sets or updates the footer text for a specific user."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE users SET footer_text = ? WHERE user_id = ?', (footer_text, user_id))
        await db.commit()
        logging.info(f"Set footer for user {user_id}.")

async def get_user_language(user_id: int) -> str | None:
    """Retrieves the language code for a specific user."""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT language_code FROM users WHERE user_id = ?', (user_id,))
        row = await cursor.fetchone()
        if row:
            return row[0]
        return None
