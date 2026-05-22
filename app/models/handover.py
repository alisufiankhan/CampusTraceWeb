from app import db
from datetime import datetime

class Handover(db.Model):
    __tablename__ = "handover"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    handover_id = db.Column(db.String(50), unique=True)
    condition = db.Column(db.String(200))
    witness = db.Column(db.String(100))
    claim_id = db.Column(db.Integer, db.ForeignKey("claim.id"))
    date_processed = db.Column(db.DateTime, default=datetime.utcnow)

    claim = db.relationship("Claim", backref="handover")

    def confirm_handover(self):
        return (
            f"Handover {self.handover_id} "
            f"confirmed. Witness: "
            f"{self.witness}"
        )

    def generate_receipt(self):
        return {
            "handover_id": self.handover_id,
            "condition": self.condition,
            "witness": self.witness,
            "date_processed": str(self.date_processed),
            "claim": self.claim.process_transaction() if self.claim else None
        }

    def process_transaction(self):
        return self.generate_receipt()

    @staticmethod
    def generate_handover_id():
        count = Handover.query.count()
        return "HDO" + str(count+1).zfill(3)
