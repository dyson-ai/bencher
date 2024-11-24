from flask import Flask, send_from_directory
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app)

@app.route('/<path:path>', methods=['GET'])
def serve_file(path):
    return send_from_directory('/home/ags/projects/bencher/cachedir', path)

def run_flask():
    app.run(port=8001)


def run_flask_in_thread():
    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

if __name__ == "__main__":
    app.run(port=8001)
