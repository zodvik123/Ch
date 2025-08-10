import pyrogram
from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode
import json, asyncio, os, sys, time
import traceback
from capsolv import *
from plugins.utility.command_debounce import is_duplicate_command
from concurrent.futures import ThreadPoolExecutor

# File path for the JSON file
USER_MESSAGE_MAP_FILE = "user_message_map.json"

# Initialize the bot with API credentials
bot = Client(
    "BOT",
    api_id='24820228', # Replace with your actual API ID     
    api_hash='5ae29104667a2d4e01e4f82ae5f28668', # Replace with your actual API Hash
    bot_token="77098912960", # Replace with your actual Bot Token
    plugins=dict(root="plugins"),
    workers=16  # Increase worker threads for better concurrency
)

bot.set_parse_mode(ParseMode.HTML)

# Create a thread pool for handling CPU-bound tasks
thread_pool = ThreadPoolExecutor(max_workers=8)

# Create a middleware to prevent duplicate command execution and manage async processing
@bot.on_message(filters.command(commands=[], prefixes=[".", "/"]), group=-1)
async def command_debounce_middleware(client, message):
    # Extract the command name
    command = message.text.split()[0][1:] if message.text else ""
    if not command:
        # Not a command, continue processing
        await message.continue_propagation()
    
    # Check if this is a duplicate command execution
    if await is_duplicate_command(message.from_user.id, command, message.id):
        # This is a duplicate command, stop processing
        return
    
    # Not a duplicate, continue processing
    await message.continue_propagation()


def load_user_message_map():
    global user_message_map  # Ensure we're using the global variable
    if os.path.exists(USER_MESSAGE_MAP_FILE):
        with open(USER_MESSAGE_MAP_FILE, "r") as file:
            try:
                user_message_map = json.load(file)
            except json.JSONDecodeError:
                # Handle case where file content is not valid JSON
                user_message_map = {}
    else:
        user_message_map = {}

def save_user_message_map():
    unique_user_message_map = {}
    for user_id, message_id in user_message_map.items():
        unique_user_message_map[user_id] = message_id
    
    with open(USER_MESSAGE_MAP_FILE, "w") as file:
        json.dump(unique_user_message_map, file)

# Initialize user_message_map
load_user_message_map()

def update_user_message_map(user_id, message_id):
    user_message_map[str(user_id)] = message_id
    save_user_message_map()

async def watchdog():
    while True:
        try:
            await asyncio.sleep(25)
        except asyncio.CancelledError:
            print("Watchdog task was cancelled.")
            break
        except Exception as e:
            os.execl(sys.executable, sys.executable, *sys.argv)

# Run the bot with watchdog
if __name__ == "__main__":
    try:
        print("Bot started successfully!")
        # loop = asyncio.get_event_loop()
        # watchdog_task = loop.create_task(watchdog())
        bot.run()
    except Exception as e:
        print(f"Unhandled exception: {e}")
        traceback.print_exc()
        sys.exit(1)

