import os
import tempfile
import shutil
import pytest
from app import create_app
from app.extensions import db
from app.models import User, Category, Question, Option, Badge

@pytest.fixture
def app():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test_platform.db')
    
    app = create_app(config_override={
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SECRET_KEY': 'test-secret-key-cyberaware',
        'WTF_CSRF_ENABLED': False,
        'RATELIMIT_ENABLED': False,
        'REPORTS_UPLOAD_DIR': os.path.join(temp_dir, 'reports'),
        'LAB_EVIDENCE_UPLOAD_DIR': os.path.join(temp_dir, 'lab_evidence')
    })

    with app.app_context():
        db.create_all()

        # Seed Test Admin
        admin = User(
            username='testadmin',
            email='admin@test.local',
            full_name='Test Admin User',
            role='ADMIN'
        )
        admin.set_password('AdminSecret123!')
        db.session.add(admin)

        # Seed Test Staff
        staff = User(
            username='teststaff',
            email='staff@test.local',
            full_name='Zainab Test',
            department='QA',
            role='STAFF'
        )
        staff.set_password('StaffSecret123!')
        db.session.add(staff)

        # Seed Category & Question
        cat = Category(name='Password Security', description='Testing passwords', icon_class='bi-key')
        db.session.add(cat)
        db.session.flush()

        q1 = Question(
            category_id=cat.id,
            question_text='What is a strong password?',
            difficulty='EASY',
            explanation='Long passphrases are strong.',
            remediation_advice='Use long passphrases.'
        )
        db.session.add(q1)
        db.session.flush()

        opt1 = Option(question_id=q1.id, option_text='123456', is_correct=False)
        opt2 = Option(question_id=q1.id, option_text='Correct-Horse-Battery-2026', is_correct=True)
        db.session.add(opt1)
        db.session.add(opt2)

        # Seed Badge
        badge = Badge(name='First Quiz', description='Completed first quiz', badge_icon='bi-award', criteria_code='FIRST_QUIZ')
        db.session.add(badge)

        db.session.commit()

    yield app

    with app.app_context():
        db.session.remove()
        db.engine.dispose()

    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception:
        pass

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
