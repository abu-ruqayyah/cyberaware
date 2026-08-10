from app.services.pdf_generator import generate_attempt_pdf_report
from app.services.csv_exporter import export_quiz_attempts_csv
from app.models import QuizAttempt, User
import os

def test_pdf_report_generation(app):
    with app.app_context():
        user = User.query.filter_by(username='teststaff').first()
        attempt = QuizAttempt(user_id=user.id, total_questions=1, score_achieved=1, percentage_score=100.0, assessment_level='Excellent', status='COMPLETED')
        from app.extensions import db
        db.session.add(attempt)
        db.session.commit()

        pdf_path = generate_attempt_pdf_report(attempt)
        assert os.path.exists(pdf_path)
        assert pdf_path.endswith('.pdf')

def test_csv_exporter(app):
    with app.app_context():
        csv_content = export_quiz_attempts_csv()
        assert 'Attempt ID' in csv_content
        assert 'Staff Username' in csv_content
