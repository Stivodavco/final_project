from app import app
from flask_login import LoginManager
from models.user import User
import os

def setup_login_manager():
    app.secret_key = os.environ.get("SECRET_KEY")

    login_manager = LoginManager()
    login_manager.init_app(app)

    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))