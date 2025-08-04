import logging
from aiogram import Bot
import database

async def send_scheduled_post(job_id: str, bot: Bot):
    """
    This function is executed by the scheduler.
    It retrieves post details from the DB and sends the post.
    """
    logging.info(f"🕒 Executing scheduled job: {job_id}")
    
    try:
        post_data = await database.get_scheduled_post(job_id)

        if not post_data:
            logging.error(f"❌ Could not find scheduled post with job_id: {job_id}")
            return

        # Unpack data from the database record
        _, user_id, post_chat_id, post_message_id, target_channel_id, caption, scheduled_time = post_data
        
        logging.info(f"📤 Sending scheduled post: user={user_id}, channel={target_channel_id}, message={post_message_id}")

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
        
        # Also increment channel post count (channel-based system)
        try:
            await database.increment_channel_post_count(target_channel_id, user_id)
        except Exception as e:
            logging.error(f"Error incrementing channel post count for scheduled post: {e}")
        
        logging.info(f"✅ Successfully sent scheduled post from job {job_id} to channel {target_channel_id}")
        
        # Notify user about successful delivery
        try:
            user_lang = await database.get_user_language(user_id) or 'en'
            success_msg = "✅ پست زمان‌بندی شده شما با موفقیت ارسال شد!" if user_lang == 'fa' else "✅ Your scheduled post was sent successfully!"
            await bot.send_message(user_id, success_msg)
        except Exception as notify_error:
            logging.warning(f"Could not notify user {user_id} about successful delivery: {notify_error}")

    except Exception as e:
        logging.error(f"❌ Failed to send scheduled post for job {job_id}: {e}")
        
        # Try to notify user about the failure
        try:
            if 'user_id' in locals():
                user_lang = await database.get_user_language(user_id) or 'en'
                error_msg = f"❌ خطا در ارسال پست زمان‌بندی شده: {str(e)}" if user_lang == 'fa' else f"❌ Error sending scheduled post: {str(e)}"
                await bot.send_message(user_id, error_msg)
        except Exception as notify_error:
            logging.warning(f"Could not notify user about delivery failure: {notify_error}")

    finally:
        # Clean up the database
        try:
            await database.delete_scheduled_post(job_id)
            logging.info(f"🗑️ Cleaned up scheduled post {job_id} from database")
        except Exception as cleanup_error:
            logging.error(f"❌ Failed to cleanup scheduled post {job_id}: {cleanup_error}")