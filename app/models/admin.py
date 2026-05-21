from app import db
from app.models.person import Person
import uuid

class Admin(Person):
    admin_code = db.Column(db.String(50))
    shift = db.Column(db.String(50))
    
    __mapper_args__ = {
        "polymorphic_identity": "admin"
    }

    def approve_claim(self, claim):
        claim.status = "Approved"
        claim.item.update_status("Claimed")
        db.session.commit()
        return "Claim approved successfully"

    def reject_claim(self, claim, student):
        claim.status = "Rejected"
        student.increment_rejections()
        db.session.commit()
        return "Claim rejected"

    def process_handover(self, claim, witness, condition):
        from app.models.handover import Handover
        handover = Handover(
            handover_id="HDO" + str(uuid.uuid4())[:6].upper(),
            condition=condition,
            witness=witness,
            claim_id=claim.id
        )
        claim.item.update_status("Returned")
        db.session.add(handover)
        db.session.commit()
        return handover
