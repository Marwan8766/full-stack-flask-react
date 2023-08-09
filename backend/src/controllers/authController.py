from datetime import datetime
from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import decode_token, jwt_required, create_access_token, get_jwt_identity
from werkzeug.exceptions import BadRequest, Unauthorized
from src.models.UserModel.user_services import UserService
from src.services.send_email import send_email
from email_validator import validate_email, EmailNotValidError
from database import db



# helper functions

def is_valid_email(email):
    try:
        valid = validate_email(email)
        return valid.email
    except EmailNotValidError:
        return False
    
def send_email_with_otp(user, email):
    otp = UserService.create_email_confirm_otp(user)
    print('sending email to ',user.email,' with otp: ',otp)
    subject = "Email Confirmation OTP"
    html_body = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f0f0f0;
                }}
                .container {{
                    padding: 20px;
                    background-color: #ffffff;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    font-size: 24px;
                    color: #333333;
                    margin-bottom: 20px;
                }}
                .message {{
                    font-size: 16px;
                    color: #555555;
                    margin-bottom: 20px;
                }}
                .otp {{
                    font-size: 20px;
                    color: #009688;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">Email Confirmation OTP</div>
                <div class="message">Your OTP for email confirmation:</div>
                <div class="otp">{otp}</div>
            </div>
        </body>
        </html>
    """
    send_email(subject, email, text_body=None, html_body=html_body)


def create_token(user_id):
    access_token = create_access_token(user_id)
    return access_token

def validate_jwt_token(token):
    try:
        # Decode the JWT token
        decoded_token = decode_token(token)
                
        return True  # Return True if token is valid
    except Exception as e:
        return False  # Return False if token is invalid

# //////////////////////////////////////////////////////////////////////

# controllers

def signup():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    # if one of the required fields isnot available return error
    if not name or not email or not password:
        return {"status": "error", "message": "Name, email, and password are required"}, 400

    # if enetered email isnot a valid email address return error   
    if is_valid_email(email) is False:    
        return {"status": "error", "message": "Invalid email format"}, 400

    # find that user
    existing_user = UserService.get_user_by_email(email)
    print('user id: ',existing_user.id)
    # print('user name: ',existing_user.name)
    # print('user pass: ',existing_user.password)
    # print('user email: ',existing_user.email)
    print('user confirmotp: ',existing_user.email_confirm_otp)
    # print('user confirmotpexoires: ',existing_user.email_confirm_otp_expires_at)
    # db.session.delete(existing_user)
    # db.session.commit()
    # if user not found create one
    if existing_user is None:
      user = UserService.create_user(name, email, password)
      print('user: ',user.email)
      send_email_with_otp(user,email)
      return {"status": "success", "message": "Check your email for the new OTP to confirm your email"},200

    # check if his email is already confirmed then return error
    if existing_user and existing_user.email_confirmed:
        return {"status": "error", "message": "Email already exists"}, 409

    #  if email isnot confirmed and otp hasnot expired yet then return error
    if existing_user and not existing_user.email_confirmed:
        current_time = datetime.utcnow()
        if existing_user.email_confirm_otp_expires_at > current_time:
            return {"status": "error", "message": "Email OTP is still valid. Resend OTP if needed."}, 400
        
        # else the user hasnot confirmed his email yet and the otp has expired
        else:
            send_email_with_otp(existing_user,email)
            return {"status": "success", "message": "Check your email for the new OTP to confirm your email"},200




def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    # if email or password arenot provided return error 
    if not email or not password:
        return {"status": "error", "message": "Email and password are required"}, 400
    
    # if email isnot valid email adress return error
    if  is_valid_email(email) is False:
        return {"status":"error","message":"You must provide a valid email address"}, 400

   # find that user by email  
    user = UserService.get_user_by_email(email)

   # if user not found return error  
    if not user:
         return {"status":"error","message":"incorrect email or password"}, 404
   
   # if password isnot correct return error  
    if not UserService.verify_password(user,password):
         return {"status":"error","message":"incorrect email or password"}, 404
    
    # if email isnot confirmed return error
    if not user.email_confirmed:
        return {"status":"error","message":"You must confirm your email first"}, 403
    
    # if everything is ok retun success with the token 
    print('id: ',user.id)
    token = create_token(user.id)
    return {"status": "success", "token": token},200


def confirm_email():
    data = request.json
    email = data.get("email")
    otp = data.get("otp")

    # Check if both email and OTP are provided
    if not email or not otp:
        return {"status": "error", "message": "Email and OTP are required"}, 400

    # Get the user by email
    user = UserService.get_user_by_email(email)
    if user is None:
        return {"status": "error", "message": "User not found"}, 404

    # Check if the user's email is not already confirmed
    if not user.email_confirmed:
        # Check if the OTP has expired
        if user.email_confirm_otp_expires_at < datetime.utcnow():
            return {"status": "error", "message": "OTP has expired"}, 400

        # Verify the provided OTP
        if not UserService.verify_email_confirm_otp(user, otp):
            return {"status": "error", "message": "Invalid OTP"}, 400

        # Update the user's email confirmation status and commit changes
        user.email_confirmed = True
        db.session.commit()

        # Create and return JWT token or other response as needed
        token = create_token(user.id)
        return {"status": "success", "token": token}

    # If the email is already confirmed, return success message
    return {"status": "success", "message": "Email already confirmed"}

def resend_otp():
    data = request.json
    email = data.get("email")
   
    # if the email isnot provided return error
    if not email:
        return {"status": "error", "message": "Email is required"}, 400
    
    # if email isnot valid email adress return error
    if  is_valid_email(email) is False:
        return {"status":"error","message":"You must provide a valid email address"}, 400

   # find that user by email  
    user = UserService.get_user_by_email(email)

   # if user not found return error  
    if not user:
        return {"status":"error","message":"this email doesn't exist"}, 404
   
   # if the otp hasnot expired yet send error 
    current_time = datetime.utcnow()
    if user.email_confirm_otp_expires_at > current_time:
        return {"status": "error", "message": "Email OTP is still valid. Resend OTP if needed."}, 400
    
    # if everything is ok send the email and return success
    send_email_with_otp(user,email)
    return {"status": "success", "message": "Check your email for the OTP to confirm your email"}


def protect(view_function):
    @wraps(view_function)
    @jwt_required()
    def wrapper(*args, **kwargs):
        try:
            # Get the token from Authorization bearer token header
            authorization_header = request.headers.get("Authorization")
            
            # If authorization header is not provided or doesn't start with "Bearer", return error
            if not authorization_header or not authorization_header.startswith("Bearer "):
                return jsonify({"status": "error", "message": "Invalid access"}), 401
            
            # Extract the token from the authorization header
            token = authorization_header.split(" ")[1]
            
            # Validate the token
            if not validate_jwt_token(token):
                return jsonify({"status": "error", "message": "Invalid token"}), 401
            
            # Find the user using the identity on the jwt
            user_id = get_jwt_identity()
            user = UserService.get_user_by_id(user_id)
            
            # Put user on request
            request.user = user
            
            return view_function(*args, **kwargs)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 401
    
    return wrapper


