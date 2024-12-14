from flask import Flask, send_from_directory
from flask_cors import CORS
import threading
from pathlib import Path


def create_server(directory):
    """Create a Flask app configured to serve files from the specified directory."""
    app = Flask(__name__)
    CORS(app)

    @app.route("/<path:path>", methods=["GET"])
    def serve_file(path):
        return send_from_directory(directory, path)

    return app


def run_flask_in_thread(directory=None, port=8001):
    """Run the Flask server to serve files from the specified directory."""
    if directory is None:
        directory = Path("cachedir/").absolute().as_posix()
    app = create_server(directory)
    threading.Thread(target=app.run, kwargs={"port": port}, daemon=True).start()
    print(f"Flask server is running on port {port} serving files from {directory}")
