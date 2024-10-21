from flask import Flask, jsonify
from flask_cors import CORS
import receiver

app = Flask(__name__)
CORS(app)

@app.route("/flights", methods=["GET"])
def get_flights():
    return jsonify({"flights": receiver.flights})

if __name__ == "__main__":
    receiver.start()
    app.run(host="0.0.0.0")
    receiver.stop()