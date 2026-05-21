from app import db
from app.models.person import Person

class Student(Person):
    roll_number = db.Column(db.String(50))
    dept = db.Column(db.String(50))
    rejections = db.Column(db.Integer, default=0)
    is_flagged = db.Column(db.Boolean, default=False)
    
    __mapper_args__ = {
        "polymorphic_identity": "student"
    }

    def increment_rejections(self):
        self.rejections += 1
        if self.rejections >= 3:
            self.is_flagged = True
        db.session.commit()
        return self.is_flagged

    def view_status(self):
        from app.models.claim import Claim
        claims = Claim.query.filter_by(person_id=self.id).all()
        return claims
