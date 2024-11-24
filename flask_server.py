from flask import Flask, send_from_directory
from flask_cors import CORS  # Import the CORS module

app = Flask(__name__)
CORS(app)  # Enable CORS for the entire application


@app.route("/<path:path>", methods=["GET"])
def serve_file(path):
    return send_from_directory("/home/ags/projects/bencher/cachedir", path)


if __name__ == "__main__":
    app.run(port=8001)
