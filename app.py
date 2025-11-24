import os
from flask import Flask

# Create the Flask app
app = Flask(__name__)
print("✅ app.py is initializing...", flush=True)

# Get port from environment variable or default to 5000
PORT = int(os.environ.get("PORT", 5000))

@app.route("/")
def home():
    return "Hello, Render! The bot is running."

@app.route("/health")
def health():
    return {"status": "healthy", "port": PORT, "service": "bot"}

if __name__ == "__main__":
    # When run directly, start the server
    app.run(host="0.0.0.0", port=PORT, threaded=True, debug=False)