from werkzeug.exceptions import BadRequest


def required_fields(data, *fields):
    if data is None:
        raise BadRequest("request body must contain data")

    if not isinstance(data, dict):
        raise BadRequest("request body must be an object")

    for field in fields:
        if field not in data:
            raise BadRequest(f"missing required field: {field}")
