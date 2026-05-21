from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.person import Person
        return Person.query.get(int(user_id))

    from app.routes.auth import auth
    from app.routes.admin_routes import admin_routes
    from app.routes.student_routes import student_routes

    app.register_blueprint(auth)
    app.register_blueprint(admin_routes)
    app.register_blueprint(student_routes)

    # Amina and Umama will register items and claims blueprints here

    return app

app = create_app()
