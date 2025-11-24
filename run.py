#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import sys
import threading
import time
import asyncio

def start_web_server():
    """Start a simple HTTP server for health checks"""
    try:
        port = int(os.environ.get('PORT', 5000))
        print(f"🌐 Starting web server on port {port}...", flush=True)
        
        # Try Flask first
        try:
            from app import app
            print(f"✅ Flask app imported successfully", flush=True)
            app.run(host="0.0.0.0", port=port, threaded=True, debug=False)
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
        sys.exit(1)

def run_bot():
    print("🤖 Starting Telegram Bot...", flush=True)
    try:
        # Ensure sessions directory exists
        os.makedirs("sessions", exist_ok=True)
        
        # Import the Extractor module to initialize the bot client
        import Extractor
        
        # Run the bot using the existing __main__.py functionality
        from Extractor import __main__
        
        # Run the bot in a blocking way using asyncio.run
        # This will block the thread until the bot is stopped
        asyncio.run(__main__.sumit_boot())
        print("✅ Bot has stopped", flush=True)
        
    except Exception as e:
        print(f"❌ Unexpected error in bot process: {e}", flush=True)
        sys.exit(1)

if __name__ == "__main__":
    # 1) Load .env locally; on Heroku/Render this is a no-op since env vars are already set
    load_dotenv()

    # 2) Verify we have the creds we need
    from config import API_ID, API_HASH, BOT_TOKEN
    if not all([API_ID, API_HASH, BOT_TOKEN]):
        sys.exit("⚠️  Missing API_ID, API_HASH, or BOT_TOKEN in the environment")

    print("🚀 Starting Services...", flush=True)
    
    # Run the web server in the main thread to ensure proper port binding on Render
    # Run the bot in a separate thread
    bot_thread = threading.Thread(target=run_bot, name="telegram_bot", daemon=False)
    bot_thread.start()
    
    # Give the bot thread a moment to start
    time.sleep(2)
    
    # Check if bot thread is still alive
    if bot_thread.is_alive():
        print("✅ Bot thread is running", flush=True)
    else:
        print("⚠️ Bot thread exited unexpectedly", flush=True)
        # If bot thread exited, exit the program
        sys.exit(1)
    
    # Run web server in main thread
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