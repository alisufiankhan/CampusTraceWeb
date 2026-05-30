import os
os.environ['TEST_DATABASE_URL'] = 'sqlite:///:memory:'

import sys
import unittest
from flask import current_app
from app import create_app, db
from app.models.student import Student
from app.models.admin import Admin
from app.models.item import Item
from app.models.claim import Claim
from app.models.report import Report
from app.models.person import Person

app = create_app()
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

class AppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        self.client = self.app.test_client()
        # Clean db
        db.session.rollback()
        db.session.query(Claim).delete()
        from app.models.handover import Handover
        db.session.query(Handover).delete()
        db.session.query(Item).delete()
        db.session.query(Person).delete()
        db.session.commit()
        
        # Create test users
        self.admin = Admin(name='Admin Test', user_id='A001')
        self.admin.set_password('adminpass')
        self.student = Student(name='Student Test', user_id='S001', roll_number='R001')
        self.student.set_password('studentpass')
        db.session.add(self.admin)
        db.session.add(self.student)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        
    def login(self, user_id, password, role):
        self.client.get('/auth/logout', follow_redirects=True)
        return self.client.post('/auth/login', data=dict(
            user_id=user_id,
            password=password,
            role=role
        ), follow_redirects=True)

    def test_01_student_login(self):
        rv = self.login('S001', 'studentpass', 'student')
        self.assertIn(b'Student Dashboard', rv.data)

    def test_02_admin_login(self):
        rv = self.login('A001', 'adminpass', 'admin')
        self.assertIn(b'Admin Dashboard', rv.data)
        
    def test_03_student_report_item(self):
        self.login('S001', 'studentpass', 'student')
        rv = self.client.post('/items/report-found', data=dict(
            desc='Test Wallet',
            location='Cafeteria',
            date_found='2026-05-28',
            category='personal',
            item_color='Black',
            size='Small',
            material='Leather'
        ), follow_redirects=True)
        item = Item.query.first()
        self.assertIsNotNone(item)
        self.assertEqual(item.status, 'PendingVerification')

    def test_04_admin_register_item(self):
        self.login('A001', 'adminpass', 'admin')
        rv = self.client.post('/items/register', data=dict(
            desc='Test Laptop',
            location='Library',
            date_found='2026-05-28',
            category='electronic',
            brand='Apple',
            color='Silver',
            serial_number='12345'
        ), follow_redirects=True)
        item = Item.query.first()
        self.assertIsNotNone(item)
        self.assertEqual(item.status, 'Found')

    def test_05_student_submit_claim(self):
        item = Item(item_id='ITM001', desc='Phone', location='Lab', date_found='2026-05-28', status='Found', item_type='electronic')
        db.session.add(item)
        db.session.commit()
        
        self.login('S001', 'studentpass', 'student')
        rv = self.client.post('/claims/submit', data=dict(
            item_id=item.item_id,
            proof='I have the matching case'
        ), follow_redirects=True)
        
        claim = Claim.query.first()
        self.assertIsNotNone(claim)
        self.assertEqual(claim.status, 'Pending')
        self.assertEqual(item.status, 'UnderReview')
        
    def test_06_admin_approve_claim(self):
        item = Item(item_id='ITM001', desc='Phone', location='Lab', date_found='2026-05-28', status='UnderReview', item_type='electronic')
        admin = Person.query.filter_by(user_id='A001').first()
        student = Person.query.filter_by(user_id='S001').first()
        claim = Claim(claim_id='CLM001', proof='Proof', status='Pending', item=item, person_id=student.id)
        db.session.add(item)
        db.session.add(claim)
        db.session.commit()
        
        self.login('A001', 'adminpass', 'admin')
        rv = self.client.post(f'/admin/claims/approve/{claim.claim_id}', follow_redirects=True)
        
        db.session.refresh(claim)
        db.session.refresh(item)
        self.assertEqual(claim.status, 'Approved')
        
    def test_07_process_handover(self):
        item = Item(item_id='ITM001', desc='Phone', location='Lab', date_found='2026-05-28', status='Claimed', item_type='electronic')
        student = Person.query.filter_by(user_id='S001').first()
        claim = Claim(claim_id='CLM001', proof='Proof', status='Approved', item=item, person_id=student.id)
        db.session.add(item)
        db.session.add(claim)
        db.session.commit()
        
        self.login('A001', 'adminpass', 'admin')
        rv = self.client.post(f'/admin/handover/{claim.claim_id}', data=dict(
            witness='Another Admin',
            condition='Good'
        ), follow_redirects=True)
        
        db.session.refresh(claim)
        db.session.refresh(item)
        self.assertEqual(item.status, 'Returned')
        
    def test_08_student_flagging(self):
        self.login('A001', 'adminpass', 'admin')
        student = Student.query.filter_by(user_id='S001').first()
        
        for i in range(3):
            item = Item(item_id=f'ITM{i}', desc='Phone', location='Lab', date_found='2026-05-28', status='UnderReview', item_type='electronic')
            claim = Claim(claim_id=f'CLM{i}', proof='Proof', status='Pending', item=item, person_id=student.id)
            db.session.add(item)
            db.session.add(claim)
            db.session.commit()
            self.client.post(f'/admin/claims/reject/{claim.claim_id}', follow_redirects=True)
            
        db.session.refresh(student)
        self.assertTrue(student.is_flagged)

    def test_09_competing_claims_on_under_review_item(self):
        # Setup an item that is already claimed by Student A (UnderReview)
        student_a = Student(name='Student A', user_id='S002', roll_number='R002')
        student_a.set_password('pass2')
        db.session.add(student_a)
        db.session.commit()

        item = Item(item_id='ITM009', desc='Keys', location='Gym', date_found='2026-05-28', status='UnderReview', item_type='personal')
        db.session.add(item)
        db.session.commit()

        claim_a = Claim(claim_id='CLM009A', proof='My keyring', status='Pending', item_id=item.id, person_id=student_a.id)
        db.session.add(claim_a)
        db.session.commit()

        # Login as student_b (S001) and submit competing claim for same item (already UnderReview)
        self.login('S001', 'studentpass', 'student')
        rv = self.client.post('/claims/submit', data=dict(
            item_id=item.item_id,
            proof='I have matching key count'
        ), follow_redirects=True)

        # Retrieve claims for this item
        claims = Claim.query.filter_by(item_id=item.id).all()
        self.assertEqual(len(claims), 2)  # Two competing claims should exist
        
        claim_b = Claim.query.filter_by(claim_id='CLM00001').first() # first auto generated id is CLM00001 in cleaned database
        if not claim_b:
            claim_b = Claim.query.filter_by(person_id=self.student.id).first()
            
        self.assertIsNotNone(claim_b)
        self.assertEqual(claim_b.status, 'Pending')
        self.assertEqual(item.status, 'UnderReview')

if __name__ == '__main__':
    unittest.main(verbosity=2)
