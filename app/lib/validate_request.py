from types import FunctionType
from flask import request
from functools import wraps
from jsonschema import validate, ValidationError


def validate_body(body_schema: dict) -> FunctionType:
    """
    Returns a decorator that validates request body based on `body_schema`
    according to JSON schema standard. If not valid, route returns 400 response.
    """

    def decorator(api_method: FunctionType) -> None:
        @wraps(api_method)
        def wrapper(*args, **kwargs):
            data = request.get_json()

            try:
                validate(data, body_schema)
                return api_method(*args, **kwargs)
            except ValidationError as error:
                return {"status": "fail", "data": error.message}, 400

        return wrapper

    return decorator
