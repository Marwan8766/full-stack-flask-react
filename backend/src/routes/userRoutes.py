from flask import Blueprint, request, jsonify
from src.controllers.authController import protect
from src.controllers.userController import get_existing_value

user = Blueprint("users", __name__, url_prefix="/api/v1/users")

@user.route('/get_existing_value', methods=['GET'])
@protect  # Apply the protect middleware here
def get_existing_value_route():
    return get_existing_value()
