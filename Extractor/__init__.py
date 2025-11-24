import asyncio
import logging
import os
from Extractor.client import app

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)

async def info_bot():
    global BOT_ID, BOT_NAME, BOT_USERNAME
    try:
        # Only start and stop the app if it's not already connected
        if not app.is_connected:
            await app.start()
            getme = await app.get_me()
            BOT_ID = getme.id
            BOT_USERNAME = getme.username
            if getme.last_name:
                BOT_NAME = getme.first_name + " " + getme.last_name
            else:
                BOT_NAME = getme.first_name
            await app.stop()
        else:
            # If already connected, just get the info
            getme = await app.get_me()
            BOT_ID = getme.id
            BOT_USERNAME = getme.username
            if getme.last_name:
                BOT_NAME = getme.first_name + " " + getme.last_name
            else:
                BOT_NAME = getme.first_name
    except Exception as e:
        print(f"Error initializing bot info: {e}")

# Only run info_bot if this module is imported (not when run directly)
if __name__ != "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(info_bot())
    except Exception as e:
        print(f"Error in Extractor init: {e}")