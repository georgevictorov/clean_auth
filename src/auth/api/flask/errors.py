from flask import jsonify
from werkzeug.exceptions import BadRequest

from auth.domain import errors

ERROR_CODES = {
    errors.ValidationError: 400,
    errors.TokenDecodeError: 401,
    errors.InvalidCredentials: 401,
    errors.UserNotFound: 404,
    errors.ConflictError: 409,
}


def get_status_code(err):
    for error_type, status_code in ERROR_CODES.items():
        if isinstance(err, error_type):
            return status_code
    return 400


def register_error_handlers(app):
    @app.errorhandler(errors.DomainError)
    def handle_domain_error(err):
        return jsonify({"msg": str(err)}), get_status_code(err)

    @app.errorhandler(errors.InfrastructureError)
    def handle_infrastructure_error(err):  # noqa
        return jsonify({"msg": "try back later..."}), 500

    @app.errorhandler(BadRequest)
    def handle_bad_request(err):
        return jsonify({"msg": err.description}), 400

    @app.errorhandler(Exception)
    def handle_unexpected_error(err):  # noqa
        return jsonify({"msg": "try back later..."}), 500
