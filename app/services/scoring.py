from datetime import datetime
from app.extensions import db
from app.models.question import Question, Option, Category
from app.models.quiz import QuizAttempt, AnswerLog, Badge, UserBadge
from app.services.audit_logger import log_event

def evaluate_assessment_level(percentage):
    """Map percentage score to organizational training assessment classification."""
    if percentage >= 90.0:
        return "Excellent (Low Awareness Risk)"
    elif percentage >= 80.0:
        return "Very Good (Moderate-Low Risk)"
    elif percentage >= 70.0:
        return "Good (Acceptable Threshold)"
    elif percentage >= 60.0:
        return "Needs Improvement (Elevated Awareness Risk)"
    else:
        return "High Awareness Risk (Critical Risk)"

def evaluate_quiz_submission(attempt_id, user_answers_dict, total_time_spent=0):
    """
    SERVER-SIDE SCORING ENGINE:
    - Receives dict of {question_id: selected_option_id}
    - Fetches correct answers directly from database
    - Compares answers server-side
    - Computes score, percentage, category breakdowns, and assessment level
    - Evaluates and awards gamification badges
    - Persists results to DB
    """
    attempt = QuizAttempt.query.get(attempt_id)
    if not attempt or attempt.status == 'COMPLETED':
        return None

    score_achieved = 0
    total_questions = len(user_answers_dict) if user_answers_dict else attempt.total_questions
    category_scores = {}  # category_id: {'name': str, 'total': int, 'correct': int, 'remediation': list}

    for q_id_str, selected_opt_id in user_answers_dict.items():
        try:
            q_id = int(q_id_str)
            selected_opt_id = int(selected_opt_id) if selected_opt_id else None
        except (ValueError, TypeError):
            continue

        question = Question.query.get(q_id)
        if not question:
            continue

        category = question.category
        cat_id = category.id if category else 0
        cat_name = category.name if category else 'General'

        if cat_id not in category_scores:
            category_scores[cat_id] = {
                'name': cat_name,
                'total': 0,
                'correct': 0,
                'remediation_advice': question.remediation_advice or "Review security best practices for this area."
            }

        category_scores[cat_id]['total'] += 1

        correct_option = Option.query.filter_by(question_id=q_id, is_correct=True).first()
        is_correct = False

        if selected_opt_id and correct_option and selected_opt_id == correct_option.id:
            is_correct = True
            score_achieved += 1
            category_scores[cat_id]['correct'] += 1

        # Record individual answer log entry
        answer_log = AnswerLog(
            attempt_id=attempt.id,
            question_id=q_id,
            selected_option_id=selected_opt_id,
            is_correct=is_correct,
            time_spent_seconds=0
        )
        db.session.add(answer_log)

    percentage = round((score_achieved / total_questions * 100.0), 2) if total_questions > 0 else 0.0
    assessment_level = evaluate_assessment_level(percentage)

    attempt.score_achieved = score_achieved
    attempt.total_questions = total_questions
    attempt.percentage_score = percentage
    attempt.assessment_level = assessment_level
    attempt.time_spent_seconds = total_time_spent
    attempt.completed_at = datetime.utcnow()
    attempt.status = 'COMPLETED'

    # Gamification: Check and award badges
    earned_badges = check_and_award_badges(attempt, percentage, category_scores)

    db.session.commit()

    log_event(
        event_type='QUIZ_COMPLETED',
        description=f"Quiz attempt #{attempt.id} completed. Score: {score_achieved}/{total_questions} ({percentage}%). Level: {assessment_level}",
        user=attempt.user
    )

    return {
        'attempt_id': attempt.id,
        'score_achieved': score_achieved,
        'total_questions': total_questions,
        'percentage': percentage,
        'assessment_level': assessment_level,
        'category_scores': category_scores,
        'earned_badges': earned_badges
    }

def check_and_award_badges(attempt, percentage, category_scores):
    """Award achievement badges based on server-evaluated metrics."""
    newly_earned = []
    user = attempt.user

    # Badge 1: First Quiz Completed
    first_badge = Badge.query.filter_by(criteria_code='FIRST_QUIZ').first()
    if first_badge:
        has_badge = UserBadge.query.filter_by(user_id=user.id, badge_id=first_badge.id).first()
        if not has_badge:
            ub = UserBadge(user_id=user.id, badge_id=first_badge.id)
            db.session.add(ub)
            newly_earned.append(first_badge)

    # Badge 2: Security Champion (Score >= 90%)
    if percentage >= 90.0:
        champ_badge = Badge.query.filter_by(criteria_code='SECURITY_CHAMPION').first()
        if champ_badge:
            has_badge = UserBadge.query.filter_by(user_id=user.id, badge_id=champ_badge.id).first()
            if not has_badge:
                ub = UserBadge(user_id=user.id, badge_id=champ_badge.id)
                db.session.add(ub)
                newly_earned.append(champ_badge)

    # Badge 3: Phishing Destroyer (100% in Phishing category)
    for cat_data in category_scores.values():
        if 'phishing' in cat_data['name'].lower() and cat_data['total'] > 0 and cat_data['correct'] == cat_data['total']:
            phish_badge = Badge.query.filter_by(criteria_code='PHISHING_DESTROYER').first()
            if phish_badge:
                has_badge = UserBadge.query.filter_by(user_id=user.id, badge_id=phish_badge.id).first()
                if not has_badge:
                    ub = UserBadge(user_id=user.id, badge_id=phish_badge.id)
                    db.session.add(ub)
                    newly_earned.append(phish_badge)
            break

    return newly_earned
