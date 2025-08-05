#!/usr/bin/env python3
"""
Quick database fix script to add missing columns
"""
import asyncio
import aiosqlite
import os

DB_NAME = 'data/bot.db'

async def fix_database():
    """Fix database by adding missing columns."""
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            print("🔧 Fixing database...")
            
            # Check if users table exists and has required columns
            cursor = await db.execute("PRAGMA table_info(users)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            print(f"📊 Current users table columns: {column_names}")
            
            # Add missing columns to users table
            if 'is_premium' not in column_names:
                print("➕ Adding is_premium column...")
                await db.execute('ALTER TABLE users ADD COLUMN is_premium INTEGER DEFAULT 0')
                
            if 'premium_until' not in column_names:
                print("➕ Adding premium_until column...")
                await db.execute('ALTER TABLE users ADD COLUMN premium_until TEXT')
                
            if 'created_at' not in column_names:
                print("➕ Adding created_at column...")
                await db.execute('ALTER TABLE users ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP')
            
            # Create missing tables
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_stats (
                    user_id INTEGER PRIMARY KEY,
                    posts_sent_this_month INTEGER DEFAULT 0,
                    last_reset_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    total_posts_sent INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS channel_premium (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    is_premium INTEGER DEFAULT 0,
                    premium_until TEXT,
                    posts_sent_this_month INTEGER DEFAULT 0,
                    last_reset_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    UNIQUE (channel_id, user_id)
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS payment_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    channel_title TEXT NOT NULL,
                    duration_months INTEGER NOT NULL,
                    amount INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    receipt_message_id INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    processed_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Initialize user_stats for existing users
            cursor = await db.execute('SELECT user_id FROM users')
            users = await cursor.fetchall()
            
            for user in users:
                user_id = user[0]
                cursor = await db.execute('SELECT user_id FROM user_stats WHERE user_id = ?', (user_id,))
                if not await cursor.fetchone():
                    await db.execute('INSERT INTO user_stats (user_id) VALUES (?)', (user_id,))
            
            # Initialize channel_premium for existing channels
            cursor = await db.execute('SELECT channel_id, user_id FROM channels')
            channels = await cursor.fetchall()
            
            for channel in channels:
                channel_id, user_id = channel
                cursor = await db.execute('SELECT id FROM channel_premium WHERE channel_id = ? AND user_id = ?', (channel_id, user_id))
                if not await cursor.fetchone():
                    await db.execute('INSERT INTO channel_premium (channel_id, user_id) VALUES (?, ?)', (channel_id, user_id))
            
            await db.commit()
            print("✅ Database fixed successfully!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(fix_database())
    print("🎉 Database is ready! You can now run: python bot.py")