from flask import Blueprint
from src.controllers.authController import signup
from src.controllers.authController import login
from src.controllers.authController import confirm_email
from src.controllers.authController import resend_otp

auth = Blueprint("auth",__name__,url_prefix="/api/v1/auth")

@auth.route('/signup', methods=['POST'])
def signup_route():
    return signup()

@auth.route('/confirm_email', methods=['PATCH'])
def confirm_email_route():
    return confirm_email()

@auth.route('/resendOTP', methods=['PATCH'])
def resend_otp_route():
    return resend_otp()

@auth.route('/login', methods=['POST'])
def login_route():
    return login()