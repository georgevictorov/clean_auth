from dataclasses import asdict

from flask import jsonify, request

from auth.api.flask.validation import required_fields
from auth.application_layer.dto import auth, session


def register_auth_routes(app, service):
    @app.route("/ping", methods=["GET"])
    def ping():
        return jsonify({"msg": "pong"}), 200

    @app.route("/login", methods=["POST"])
    def login():
        data = request.get_json()

        required_fields(data, "username", "password")

        cmd = auth.LoginRequest(
            username=data["username"],
            password=data["password"]
        )

        result = service.login(cmd)

        return jsonify(asdict(result)), 200

    @app.route("/refresh", methods=["POST"])
    def refresh():
        data = request.get_json()

        required_fields(data, "refresh_token")

        cmd = session.RefreshRequest(
            refresh_token=data["refresh_token"]
        )

        result = service.refresh(cmd)

        return jsonify(asdict(result)), 200

    @app.route("/logout", methods=["POST"])
    def logout():
        data = request.get_json()

        required_fields(data, "refresh_token")

        cmd = auth.LogoutRequest(
            refresh_token=data["refresh_token"]
        )

        service.logout(cmd)

        return jsonify({"msg": "ok"}), 204


def register_key_routes(app, service):
    @app.route("/.well-known/paserk.json", methods=["GET"])
    def get_public_keys():
        result = service.get_public_keys()
        return jsonify(asdict(result)), 200
