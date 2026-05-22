from app import db
from datetime import datetime, date

class Item(db.Model):
    __tablename__ = "item"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_id = db.Column(db.String(50), unique=True, nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_found = db.Column(db.String(20))
    location = db.Column(db.String(200))
    status = db.Column(db.String(50), default="Found")
    item_type = db.Column(db.String(50), nullable=False)

    __mapper_args__ = {
        "polymorphic_on": item_type,
        "polymorphic_identity": "item"
    }

    def get_details(self):
        return {
            "id": self.id,
            "item_id": self.item_id,
            "desc": self.desc,
            "date_found": self.date_found,
            "location": self.location,
            "status": self.status,
            "item_type": self.item_type
        }

    def update_status(self, new_status):
        self.status = new_status
        db.session.commit()

    def is_expired(self):
        try:
            found_date = datetime.strptime(self.date_found, "%d-%m-%Y").date()
            today = date.today()
            diff = (today - found_date).days
            return diff > 30
        except:
            return False

    def to_dict(self):
        return self.get_details()

    @staticmethod
    def generate_item_id():
        from app.models.item import Item
        count = Item.query.count()
        return "ITEM" + str(count+1).zfill(3)

class ElectronicItem(Item):
    brand = db.Column(db.String(100))
    color = db.Column(db.String(50))
    serial_number = db.Column(db.String(100))

    __mapper_args__ = {
        "polymorphic_identity": "electronic"
    }

    def get_details(self):
        details = super().get_details()
        details["brand"] = self.brand
        details["color"] = self.color
        details["serial_number"] = self.serial_number
        return details

    def to_dict(self):
        return self.get_details()

class DocumentItem(Item):
    doc_type = db.Column(db.String(100))
    issued_by = db.Column(db.String(100))

    __mapper_args__ = {
        "polymorphic_identity": "document"
    }

    def get_details(self):
        details = super().get_details()
        details["doc_type"] = self.doc_type
        details["issued_by"] = self.issued_by
        return details

    def to_dict(self):
        return self.get_details()

class PersonalItem(Item):
    item_color = db.Column(db.String(50))
    size = db.Column(db.String(50))
    material = db.Column(db.String(100))

    __mapper_args__ = {
        "polymorphic_identity": "personal"
    }

    def get_details(self):
        details = super().get_details()
        details["color"] = self.item_color
        details["size"] = self.size
        details["material"] = self.material
        return details

    def to_dict(self):
        return self.get_details()
