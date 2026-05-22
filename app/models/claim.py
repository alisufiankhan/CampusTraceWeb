from app import db
from datetime import datetime
import uuid

class Claim(db.Model):
    __tablename__ = "claim"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    claim_id = db.Column(db.String(50), unique=True, nullable=False)
    proof = db.Column(db.String(1000), nullable=False)
    status = db.Column(db.String(50), default="Pending")
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"), nullable=False)
    transaction_id = db.Column(db.String(100))
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)

    item = db.relationship("Item", backref="claims")
    person = db.relationship("Person", backref="claims")

    def submit_claim(self):
        self.status = "Pending"
        self.transaction_id = str(uuid.uuid4())
        db.session.commit()
        return "Claim submitted"

    def validate_claim(self):
        if self.proof and len(self.proof.strip()) > 0:
            return True
        return False

    def set_disputed(self):
        self.status = "Disputed"
        db.session.commit()

    def process_transaction(self):
        return {
            "claim_id": self.claim_id,
            "proof": self.proof,
            "status": self.status,
            "item": self.item.get_details() if self.item else None,
            "person_name": self.person.name if self.person else None,
            "date_submitted": str(self.date_submitted),
            "transaction_id": self.transaction_id
        }

    @staticmethod
    def generate_claim_id():
        count = Claim.query.count()
        return "CLM" + str(count+1).zfill(3)
