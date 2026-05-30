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
        from flask import render_template
        from app.models.item import Item
        from app.models.claim import Claim
        
        # Query counts for live visual statistics
        total_found = Item.query.filter(Item.status.in_(["Found", "UnderReview"])).count()
        total_returned = Item.query.filter_by(status="Returned").count()
        total_pending_claims = Claim.query.filter_by(status="Pending").count()
        
        return render_template('landing.html', 
                               total_found=total_found, 
                               total_returned=total_returned,
                               total_pending_claims=total_pending_claims)

    @app.context_processor
    def inject_counts():
        from app.models.item import Item
        pending_reports_count = 0
        try:
            pending_reports_count = Item.query.filter_by(status="PendingVerification").count()
        except:
            pass
        return dict(pending_reports_count=pending_reports_count)

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
