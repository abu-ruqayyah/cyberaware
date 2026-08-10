def test_unauthenticated_admin_access(client):
    response = client.get('/admin/dashboard')
    assert response.status_code in [302, 401]

def test_staff_denied_admin_access(client):
    # Log in as Staff
    client.post('/auth/login', data={'username': 'teststaff', 'password': 'StaffSecret123!'})
    
    # Try accessing Admin dashboard
    response = client.get('/admin/dashboard')
    assert response.status_code == 403

def test_admin_allowed_access(client):
    # Log in as Admin
    client.post('/auth/login', data={'username': 'testadmin', 'password': 'AdminSecret123!'})
    
    response = client.get('/admin/dashboard')
    assert response.status_code == 200
    assert b'Trainer Command Center' in response.data
