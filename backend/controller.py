from flask import Flask, request, jsonify
from flask_cors import CORS
from settings import *
import receiver

app = Flask(__name__)
CORS(app)

@app.route("/configuration", methods=["POST"])
def manage_configuration():
    data = dict(request.json)

    with Session(db_engine) as session:
        saved_configuration = session.scalars(select(Configuration))

        for setting in saved_configuration:
            if setting.key in data.keys():
                setting.value = data[setting.key]
                data.pop(setting.key)

        for key in data.keys():
            session.add(Configuration(key, data[key]))

        session.commit()

    return jsonify({"message": "Configuration was updated successfully"})

@app.route("/flights", methods=["GET"])
def get_flights():
    return jsonify({"flights": receiver.flights})

if __name__ == "__main__":
    receiver.start()
    app.run(host="0.0.0.0")
    receiver.stop()