import asyncio
import importlib
import signal
import threading
import time
import sys
import os
from pyrogram import idle
from Extractor.modules import ALL_MODULES
from Extractor.client import app

# Graceful shutdown
should_exit = asyncio.Event()

def shutdown():
    print("Shutting down gracefully...")
    should_exit.set()  # triggers exit from idle

def start_web_server():
    """Start a simple HTTP server for health checks when running directly"""
    try:
        port = int(os.environ.get('PORT', 5000))
        print(f"🌐 Starting web server on port {port}...", flush=True)
        
        # Try Flask first
        try:
            from app import app as flask_app
            print(f"✅ Flask app imported successfully", flush=True)
            flask_app.run(host="0.0.0.0", port=port, threaded=True, debug=False)
        except Exception as e:
            print(f"⚠️ Flask app error: {e}, trying simple HTTP server", flush=True)
            # Fallback to simple HTTP server
            from http.server import HTTPServer, BaseHTTPRequestHandler
            
            class HealthHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/health':
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        response = '{"status": "healthy", "service": "bot"}'
                        self.wfile.write(response.encode())
                    elif self.path == '/':
                        self.send_response(200)
                        self.send_header('Content-type', 'text/plain')
                        self.end_headers()
                        response = 'Hello, Render! The bot is running.'
                        self.wfile.write(response.encode())
                    else:
                        self.send_response(404)
                        self.end_headers()
            
            server = HTTPServer(('0.0.0.0', port), HealthHandler)
            print(f"✅ Simple HTTP server listening on port {port}", flush=True)
            server.serve_forever()
            
    except Exception as e:
        print(f"❌ Web server error: {e}", flush=True)

async def sumit_boot():
    print("🔧 Initializing bot...", flush=True)
    
    # Set up signal handlers
    signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(should_exit.set()))
    signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(should_exit.set()))
    
    # Check if app is already started
    if not app.is_connected:
        # Start the bot client
        print("🔌 Starting bot client...", flush=True)
        await app.start()
        print("✅ Bot client started", flush=True)
    else:
        print("✅ Bot client already started", flush=True)
    
    print(f"📦 Loading {len(ALL_MODULES)} modules...", flush=True)
    for all_module in ALL_MODULES:
        try:
            importlib.import_module("Extractor.modules." + all_module)
            print(f"✅ Loaded module: {all_module}", flush=True)
        except Exception as e:
            print(f"❌ Failed to load module {all_module}: {e}", flush=True)

    print("» ʙᴏᴛ ᴅᴇᴘʟᴏʏ sᴜᴄᴄᴇssғᴜʟʟʏ ✨ 🎉", flush=True)
    
    # Instead of blocking with idle(), we wait for the exit event
    print("⏳ Waiting for exit signal...", flush=True)
    await should_exit.wait()
    
    # Stop the bot client only if it was started by us
    if app.is_connected:
        print("🔌 Stopping bot client...", flush=True)
        await app.stop()
    print("» ɢᴏᴏᴅ ʙʏᴇ ! sᴛᴏᴘᴘɪɴɢ ʙᴏᴛ.", flush=True)

# New function for non-blocking operation
async def start_bot():
    """Start the bot without blocking indefinitely"""
    # Check if app is already started
    if not app.is_connected:
        # Start the bot client
        await app.start()
    
    for all_module in ALL_MODULES:
        importlib.import_module("Extractor.modules." + all_module)

    print("» ʙᴏᴛ sᴛᴀʀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ✨ 🎉")
    # Return control but keep the bot running
    return True

if __name__ == "__main__":
    print("🚀 Starting Services (Direct Mode)...", flush=True)
    
    # Start the bot in a separate thread
    def run_bot():
        try:
            asyncio.run(sumit_boot())
        except Exception as e:
            print(f"Error running bot: {e}", flush=True)
    
    bot_thread = threading.Thread(target=run_bot, name="telegram_bot", daemon=False)
    bot_thread.start()
    
    # Give the bot thread a moment to start
    time.sleep(2)
    
    # Check if bot thread is still alive
    if bot_thread.is_alive():
        print("✅ Bot thread is running", flush=True)
    else:
        print("⚠️ Bot thread exited unexpectedly", flush=True)
        sys.exit(1)
    
    # Start web server in main thread
    start_web_server()
    
    # Keep the main thread alive and monitor
    try:
        while True:
            time.sleep(1)
            if not bot_thread.is_alive():
                print("⚠️ Bot thread died!", flush=True)
                sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 Stopping services...", flush=True)