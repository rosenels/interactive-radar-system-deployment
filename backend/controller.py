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

@app.route("/configuration", methods=["GET"])
def get_configuration():
    data = {}

    token_details = authentication.validate_token(request.args.get("token"))

    if token_details["active"] == False:
        return make_response({"message": "Unauthorized"}, 401)

    if os.getenv("KEYCLOAK_ADMIN_USER_ROLE") not in token_details["resource_access"][os.getenv("KEYCLOAK_ADMIN_USER_RESOURCE")]["roles"]:
        return make_response({"message": "Unauthorized"}, 401)

    with Session(db_engine) as session:
        saved_configuration = session.scalars(select(Configuration))

        for setting in saved_configuration:
            data[setting.key] = setting.value

    return make_response({"configuration": data}, 200)

@app.route("/configuration", methods=["POST"])
def update_configuration():
    data = dict(request.json)

    token_details = authentication.validate_token(data.pop("token"))

    if token_details["active"] == False:
        return make_response({"message": "Unauthorized"}, 401)

    if os.getenv("KEYCLOAK_ADMIN_USER_ROLE") not in token_details["resource_access"][os.getenv("KEYCLOAK_ADMIN_USER_RESOURCE")]["roles"]:
        return make_response({"message": "Unauthorized"}, 401)

    with Session(db_engine) as session:
        saved_configuration = session.scalars(select(Configuration))

        for setting in saved_configuration:
            if setting.key in data.keys():
                setting.value = data[setting.key]
                data.pop(setting.key)

        for key in data.keys():
            session.add(Configuration(key, data[key]))

        session.commit()

    return make_response({"message": "Configuration was updated successfully"}, 200)

if __name__ == "__main__":
    receiver.start()
    app.run(host="0.0.0.0")
    receiver.stop()