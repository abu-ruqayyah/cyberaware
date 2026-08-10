from app.models import Question, Category

def test_admin_create_question(client, app):
    # Disable CSRF for form test client or use CSRF helper
    app.config['WTF_CSRF_ENABLED'] = False
    with client:
        client.post('/auth/login', data={'username': 'testadmin', 'password': 'AdminSecret123!'})
        cat = Category.query.first()
        
        response = client.post('/admin/questions/new', data={
            'category_id': cat.id,
            'question_text': 'What is Phishing?',
            'difficulty': 'EASY',
            'explanation': 'Deceptive communications',
            'remediation_advice': 'Check headers',
            'option_text[]': ['Fraudulent email', 'Safe website'],
            'correct_option': 0
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Question added successfully' in response.data
