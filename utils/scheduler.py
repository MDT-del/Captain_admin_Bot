import logging
from aiogram import Bot
import database

async def send_scheduled_post(job_id: str, bot: Bot):
    """
    This function is executed by the scheduler.
    It retrieves post details from the DB and sends the post.
    """
    logging.info(f"Executing scheduled job: {job_id}")
    post_data = await database.get_scheduled_post(job_id)

    if not post_data:
        logging.error(f"Could not find scheduled post with job_id: {job_id}")
        return

    # Unpack data from the database record
    _, user_id, post_chat_id, post_message_id, target_channel_id, caption, _ = post_data

    try:
        # Send the post with the caption that already includes footer (if any)
        await bot.copy_message(
            chat_id=target_channel_id,
            from_chat_id=post_chat_id,
            message_id=post_message_id,
            caption=caption if caption else None,
            parse_mode="HTML"
        )
        
        # Increment user's post count for scheduled posts too
        await database.increment_user_post_count(user_id)
        
        logging.info(f"Successfully sent scheduled post from job {job_id} to channel {target_channel_id}")

    except Exception as e:
        logging.error(f"Failed to send scheduled post for job {job_id}: {e}")

    finally:
        # Clean up the database
        await database.delete_scheduled_post(job_id)
