from app import db

class Reward(db.Model):
    __tablename__ = "reward"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reward_id = db.Column(db.String(50), unique=True)
    offered_by = db.Column(db.String(50))
    desc = db.Column(db.String(500))
    status = db.Column(db.String(50), default="Active")
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"))

    item = db.relationship("Item", backref="reward")

    def offer_reward(self):
        self.status = "Active"
        db.session.commit()

    def cancel_reward(self):
        self.status = "Cancelled"
        db.session.commit()

    def get_reward_status(self):
        return self.status
