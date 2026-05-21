from app import db
from datetime import datetime

class SearchLog(db.Model):
    __tablename__ = "searchlog"
    id = db.Column(db.Integer, primary_key=True)
    log_id = db.Column(db.String(100), unique=True)
    keyword = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    student_id = db.Column(db.String(50))

    def log_search(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_history(student_id):
        return SearchLog.query.filter_by(student_id=student_id).order_by(SearchLog.timestamp.desc()).all()
