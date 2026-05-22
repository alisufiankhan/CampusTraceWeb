import requests

base_url = 'http://localhost:5000'

def test():
    s_admin = requests.Session()
    # Admin login
    r = s_admin.post(base_url + '/auth/login', data={'user_id': 'A001', 'password': 'admin123', 'role': 'admin'})
    if r.status_code != 200 or 'Admin Dashboard' not in r.text:
        print("Admin login failed")
        return False
    print("Admin logged in")

    # Register Electronic
    r = s_admin.post(base_url + '/items/register', data={
        'desc': 'Lost iPhone 13', 'location': 'Library', 'date_found': '10-05-2026', 'category': 'electronic',
        'brand': 'Apple', 'color': 'Black', 'serial_number': 'SN12345'
    })
    
    # Register Document
    r = s_admin.post(base_url + '/items/register', data={
        'desc': 'Student ID Card', 'location': 'Cafeteria', 'date_found': '11-05-2026', 'category': 'document',
        'doc_type': 'ID Card', 'issued_by': 'University'
    })

    # Register Personal
    r = s_admin.post(base_url + '/items/register', data={
        'desc': 'Water Bottle', 'location': 'Gym', 'date_found': '12-05-2026', 'category': 'personal',
        'item_color': 'Blue', 'size': 'Large', 'material': 'Plastic'
    })
    
    # View all items
    r = s_admin.get(base_url + '/items/all')
    if 'Lost iPhone 13' not in r.text or 'Student ID Card' not in r.text:
        print("Failed to register or view items")
        return False
    print("Items registered successfully")
    
    # Admin logout
    s_admin.get(base_url + '/auth/logout')

    # Student 1 Login
    s_stud1 = requests.Session()
    r = s_stud1.post(base_url + '/auth/login', data={'user_id': 'S001', 'password': 'ali123', 'role': 'student'})
    
    # Search for item
    r = s_stud1.post(base_url + '/items/search', data={'keyword': 'iphone'})
    if 'Lost iPhone 13' not in r.text:
        print("Search failed to find item")
        return False
        
    # Claim item (Need item_id, it will be 1 for iPhone)
    r = s_stud1.post(base_url + '/claims/claims/submit', data={'item_id': '1', 'proof': 'I have the original box'})
    
    # View my claims
    r = s_stud1.get(base_url + '/claims/student/my-claims')
    if 'Lost iPhone 13' not in r.text:
        print("Failed to submit claim or view my claims")
        return False
    print("Student claim submitted successfully")
    
    # Student 2 Login (to claim another item for rejection)
    s_stud2 = requests.Session()
    r = s_stud2.post(base_url + '/auth/login', data={'user_id': 'S002', 'password': 'amina123', 'role': 'student'})
    r = s_stud2.post(base_url + '/claims/claims/submit', data={'item_id': '2', 'proof': 'It is my ID card'})
    s_stud2.get(base_url + '/auth/logout')

    # Admin Login again
    s_admin = requests.Session()
    s_admin.post(base_url + '/auth/login', data={'user_id': 'A001', 'password': 'admin123', 'role': 'admin'})
    
    # Approve claim 1
    # Assuming claim_id format is CLM001
    r = s_admin.post(base_url + '/claims/admin/claims/approve/CLM001')
    
    # Process Handover for claim 1
    r = s_admin.post(base_url + '/claims/admin/handover/CLM001', data={'witness': 'John Doe', 'condition': 'Good'})
    
    # Reject claim 2
    r = s_admin.post(base_url + '/claims/admin/claims/reject/CLM002')
    
    print("Admin claims processed")
    
    s_admin.get(base_url + '/auth/logout')
    
    # Check student 2
    s_stud2 = requests.Session()
    s_stud2.post(base_url + '/auth/login', data={'user_id': 'S002', 'password': 'amina123', 'role': 'student'})
    r = s_stud2.get(base_url + '/claims/student/my-claims')
    if 'rejected' not in r.text.lower():
        print("Rejection failed to show up")
        return False
        
    print("Flow completely successful!")
    return True

if __name__ == "__main__":
    test()
