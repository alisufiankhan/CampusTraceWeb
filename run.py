from app import app, db
from app.models.person import Person
from app.models.student import Student
from app.models.admin import Admin

def seed_data():
    admin = Person.query.filter_by(user_id="A001").first()
    if not admin:
        admin = Admin(
            name="Admin One",
            user_id="A001",
            contact="0300-1234567",
            admin_code="ADM001",
            shift="Morning",
            role="admin"
        )
        admin.set_password("admin123")
        
        s1 = Student(
            name="Ali Sufian",
            user_id="S001",
            contact="0301-1234567",
            roll_number="B25F0559AI154",
            dept="AI",
            role="student"
        )
        s1.set_password("ali123")
        
        s2 = Student(
            name="Amina Shafique",
            user_id="S002",
            contact="0302-1234567",
            roll_number="B25F2267AI157",
            dept="AI",
            role="student"
        )
        s2.set_password("amina123")
        
        s3 = Student(
            name="Umama Khurram",
            user_id="S003",
            contact="0303-1234567",
            roll_number="B25F2677AI147",
            dept="AI",
            role="student"
        )
        s3.set_password("umama123")
        
        db.session.add_all([admin, s1, s2, s3])
        db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(host="0.0.0.0", port=5000, debug=True)
