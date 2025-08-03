import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# It's highly recommended to use environment variables for sensitive data.
# Create a .env file in the root of your project and add your bot token like this:
# BOT_TOKEN='123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Basic validation to ensure the token is set
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in the environment variables or .env file.")

# Developer ID for special privileges
DEVELOPER_ID = int(os.getenv("DEVELOPER_ID", "0"))

# Premium system settings
FREE_USER_POST_LIMIT = 10  # Posts per month for free users
