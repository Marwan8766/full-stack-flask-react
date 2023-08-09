import datetime
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from src import create_app
from src.routes.authRoutes import auth
from src.routes.userRoutes import user
from dotenv import load_dotenv
import os
from database import db
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import eventlet  # Import eventlet



load_dotenv('./config.env')

jwt = JWTManager()

migrate = Migrate()


test_config = {
    "SQLALCHEMY_DATABASE_URI": os.environ.get("SQLALCHEMY_DATABASE_URI"),
    "MAIL_SERVER": '74.125.206.108',
    "MAIL_PORT": 465,  
    "MAIL_USE_TLS": False,
    "MAIL_USERNAME": os.environ.get("EMAIL_USERNAME"),
    "MAIL_PASSWORD": os.environ.get("EMAIL_PASSWORD"),
    "TESTING":False,
    "MAIL_DEBUG":True,
    "MAIL_SUPPRESS_SEND":False,
    "MAIL_USE_SSL": True,
    "JWT_SECRET_KEY": os.environ.get("JWT_SECRET_KEY"),
    "JWT_ACCESS_TOKEN_EXPIRES": datetime.timedelta(seconds=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES")))
}
from src.services.send_email import mail


app = create_app(test_config)

db.init_app(app)
mail.init_app(app)
jwt.init_app(app)
migrate.init_app(app, db)  
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")  # or async_mode='gevent'



@socketio.on('calculate_percentage')
def calculate_percentage(data):
    try:
        num1 = int(data['num1'])
        num2 = int(data['num2'])
        print("num1 :",num1)
        print("num2 :",num2)
        percentage = (num2 - num1) / num1 * 100
        emit('percentage_result', {'percentage': percentage})
    except Exception as e:
        print('error ',str(e))
        emit('error', {'message': str(e)})



#  Apply CORS to the app
CORS(app, origins="*")  # Allow access from all origins

app.register_blueprint(auth)

app.register_blueprint(user)


if __name__ == "__main__":
    with app.app_context():
      db.create_all()
    socketio.run(app)
    # app.run()
