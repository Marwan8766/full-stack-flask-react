from database import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    email_confirm_otp = db.Column(db.String(6), nullable=True)
    email_confirm_otp_expires_at = db.Column(db.DateTime, nullable=True)
    email_confirmed = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Integer,default=1000)
