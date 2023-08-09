from flask import request


def get_existing_value():
    existing_value = request.user.value
    return {"status":"success","existing_value":existing_value}