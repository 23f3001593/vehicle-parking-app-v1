from flask import make_response, jsonify
from werkzeug.exceptions import HTTPException

class ValidationError(HTTPException):
    def __init__(self, message, status_code=400):
        self.response = make_response(
            jsonify({"message": message}), status_code
        )

class NotFoundError(HTTPException):
    def __init__(self, message, status_code=404):
        self.response = make_response(
            jsonify({"message": message}), status_code
        )

class AlreadyExistError(HTTPException):
    def __init__(self, message, status_code=409):
        self.response = make_response(
            jsonify({"message": message}), status_code
        )

class MissingFieldsError(HTTPException):
    def __init__(self, message, status_code=422):
        self.response = make_response(
            jsonify({"message": message}), status_code
        )