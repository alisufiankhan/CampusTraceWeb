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

    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))

    from app.routes.items import items
    app.register_blueprint(items)
    
    from app.routes.claims import claims
    app.register_blueprint(claims)

    from app.models.item import Item
    from app.models.claim import Claim
    from app.models.handover import Handover
    from app.models.reward import Reward
    from app.models.searchlog import SearchLog
    from app.models.report import Report

    return app

app = create_app()
