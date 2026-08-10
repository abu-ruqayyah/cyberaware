from app.services.scoring import evaluate_assessment_level, evaluate_quiz_submission
from app.models import QuizAttempt, User, Question, Option

def test_assessment_level_mapping():
    assert "Excellent" in evaluate_assessment_level(95.0)
    assert "Very Good" in evaluate_assessment_level(85.0)
    assert "Good" in evaluate_assessment_level(75.0)
    assert "Needs Improvement" in evaluate_assessment_level(65.0)
    assert "High Awareness Risk" in evaluate_assessment_level(50.0)

def test_server_side_scoring_execution(app):
    with app.app_context():
        user = User.query.filter_by(username='teststaff').first()
        question = Question.query.first()
        correct_option = Option.query.filter_by(question_id=question.id, is_correct=True).first()

        attempt = QuizAttempt(user_id=user.id, total_questions=1, status='IN_PROGRESS')
        from app.extensions import db
        db.session.add(attempt)
        db.session.commit()

        # Submit correct answer
        user_answers = {str(question.id): str(correct_option.id)}
        result = evaluate_quiz_submission(attempt.id, user_answers, total_time_spent=15)

        assert result is not None
        assert result['score_achieved'] == 1
        assert result['percentage'] == 100.0
        assert "Excellent" in result['assessment_level']
