from flask import Flask, request, make_response
from flask_cors import CORS
from settings import *
import authentication
import receiver

app = Flask(__name__)
CORS(app)

@app.route("/flights", methods=["GET"])
def get_flights():
    return make_response({"flights": receiver.flights}, 200)

@app.route("/flights/<string:icao>", methods=["POST"])
def control_flight(icao):
    data = dict(request.json)

    parsed_token = authentication.parse_token(data.get("token"))

    if not authentication.is_token_active(parsed_token):
        return make_response({"message": "Unauthorized"}, 401)

    with Session(db_engine) as session:
        flight_info = session.scalar(select(FlightInformation).where(FlightInformation.icao == icao).order_by(FlightInformation.timestamp.desc()))

        if flight_info is None:
            return make_response({"message": "There is no flight with this ICAO address"}, 400)

        else:
            new_instructions = InstructionsFromATC(
                atc_user_id=authentication.get_user_id(parsed_token),
                altitude=data.get("altitude", None),
                ground_speed=data.get("ground_speed", None),
                track=data.get("track", None),
                vertical_rate=data.get("vertical_rate", None)
            )
            new_instructions.flight_info.append(flight_info)
            session.add(new_instructions)

            session.commit()

    return make_response({"message": "Instructions were applied successfully"}, 200)

@app.route("/configuration", methods=["GET"])
def get_configuration():
    data = {
        "RAW_IN_DEFAULT_PORT": RAW_IN_DEFAULT_PORT,
        "SBS_DEFAULT_PORT": SBS_DEFAULT_PORT
    }

    parsed_token = authentication.parse_token(request.args.get("token"))

    if not authentication.is_admin_user_token(parsed_token):
        return make_response({"message": "Unauthorized"}, 401)

    with Session(db_engine) as session:
        saved_configuration = session.scalars(select(Configuration))

        for setting in saved_configuration:
            try:
                data[setting.key] = float(setting.value)
            except:
                data[setting.key] = setting.value

    return make_response({"configuration": data}, 200)

@app.route("/configuration", methods=["POST"])
def update_configuration():
    data = dict(request.json)

    parsed_token = authentication.parse_token(data.pop("token"))

    if not authentication.is_admin_user_token(parsed_token):
        return make_response({"message": "Unauthorized"}, 401)

    with Session(db_engine) as session:
        saved_configuration = session.scalars(select(Configuration))

        for setting in saved_configuration: # update existing values for coresponding keys
            if setting.key in data.keys():
                setting.value = data.pop(setting.key)

        for key in data.keys(): # add new key - value pairs
            session.add(Configuration(key, data[key]))

        session.commit()

    load_settings() # update settings variables values from the database

    return make_response({"message": "Configuration was updated successfully"}, 200)

if __name__ == "__main__":
    receiver.start()
    app.run(host="0.0.0.0")
    receiver.stop()