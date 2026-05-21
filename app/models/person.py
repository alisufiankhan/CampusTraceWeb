from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class Person(UserMixin, db.Model):
    __tablename__ = "person"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    contact = db.Column(db.String(20))
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), nullable=False)
    
    __mapper_args__ = {
        "polymorphic_on": role,
        "polymorphic_identity": "person"
    }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_info(self):
        return {
            "name": self.name,
            "user_id": self.user_id,
            "contact": self.contact,
            "role": self.role
        }

    def get_id(self):
        return str(self.id)
