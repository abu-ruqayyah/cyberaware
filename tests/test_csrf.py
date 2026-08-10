def test_post_without_csrf_rejected(app):
    app.config['WTF_CSRF_ENABLED'] = True
    client = app.test_client()
    response = client.post('/auth/login', data={'username': 'teststaff', 'password': 'StaffSecret123!'})
    assert response.status_code == 400
