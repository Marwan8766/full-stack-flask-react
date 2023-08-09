from database import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.UserModel.user_model import User
import random

class UserService:
    @staticmethod
    def create_user(name, email, password):
        hashed_password = UserService._hash_password(password)
        user = User(name=name, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_user_by_id(user_id, require_email_confirmed=True):
        user = User.query.get(user_id)
        if user and require_email_confirmed and not user.email_confirmed:
            return None
        return user

    @staticmethod
    def _hash_password(password):
        return generate_password_hash(password)

    @staticmethod
    def verify_password(user, password):
        return check_password_hash(user.password, password)

    @staticmethod
    def create_email_confirm_otp(user):
        if user is None:
            raise ValueError("User not found")
    
        otp = UserService._generate_otp()
        print('otp ',otp)
        hashed_otp = UserService._hash_otp(otp)
        user.email_confirm_otp = hashed_otp
        user.email_confirm_otp_expires_at = datetime.utcnow() + timedelta(seconds=90)
        db.session.commit()
        return otp

    @staticmethod
    def verify_email_confirm_otp(user, otp):
        hashed_otp = UserService._hash_otp(otp)
        return user.email_confirm_otp == hashed_otp and user.email_confirm_otp_expires_at > datetime.utcnow()
        return True

    @staticmethod
    def _generate_otp():
        # Generate a random 5-digit OTP
        return str(random.randint(10000, 99999))

    @staticmethod
    def _hash_otp(otp):
        return generate_password_hash(otp)
