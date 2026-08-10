def test_register_staff(client):
    response = client.post('/auth/register', data={
        'username': 'newstaff',
        'email': 'newstaff@test.local',
        'full_name': 'New Staff Member',
        'department': 'Operations',
        'password': 'Password123!',
        'confirm_password': 'Password123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful' in response.data or b'Log In' in response.data

def test_login_success(client):
    response = client.post('/auth/login', data={
        'username': 'teststaff',
        'password': 'StaffSecret123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome back' in response.data

def test_login_invalid_password(client):
    response = client.post('/auth/login', data={
        'username': 'teststaff',
        'password': 'WrongPassword!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username/email or password' in response.data

def test_logout(client):
    client.post('/auth/login', data={'username': 'teststaff', 'password': 'StaffSecret123!'})
    response = client.post('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'logged out securely' in response.data
