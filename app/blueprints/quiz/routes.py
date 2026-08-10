import random
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.question import Question, Category
from app.models.quiz import QuizAttempt, Badge, UserBadge
from app.services.scoring import evaluate_quiz_submission
from app.services.audit_logger import log_event

quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')

@quiz_bp.route('/dashboard')
@login_required
def dashboard():
    attempts = QuizAttempt.query.filter_by(user_id=current_user.id, status='COMPLETED').order_by(QuizAttempt.completed_at.desc()).all()
    user_badges = UserBadge.query.filter_by(user_id=current_user.id).all()
    
    best_score = max((a.percentage_score for a in attempts), default=0.0)
    avg_score = round(sum(a.percentage_score for a in attempts) / len(attempts), 1) if attempts else 0.0

    return render_template(
        'quiz/dashboard.html',
        attempts=attempts,
        user_badges=user_badges,
        best_score=best_score,
        avg_score=avg_score
    )


@quiz_bp.route('/start', methods=['GET', 'POST'])
@login_required
def start_quiz():
    categories = Category.query.all()
    
    if request.method == 'POST':
        category_id = request.form.get('category_id', type=int)
        
        query = Question.query.filter_by(is_active=True)
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        available_questions = query.all()
        if not available_questions:
            flash('No active questions found for the selected category. Please contact an administrator.', 'warning')
            return redirect(url_for('quiz.start_quiz'))

        # Select up to 10 randomized questions
        num_questions = min(10, len(available_questions))
        selected_questions = random.sample(available_questions, num_questions)

        attempt = QuizAttempt(
            user_id=current_user.id,
            total_questions=num_questions,
            status='IN_PROGRESS',
            started_at=datetime.utcnow()
        )
        db.session.add(attempt)
        db.session.commit()

        log_event('QUIZ_STARTED', f"Quiz attempt #{attempt.id} started with {num_questions} questions.", user=current_user)

        # Store question sequence in session for this attempt
        q_ids = [q.id for q in selected_questions]
        return redirect(url_for('quiz.play_quiz', attempt_id=attempt.id, q_ids=','.join(map(str, q_ids))))

    return render_template('quiz/select_quiz.html', categories=categories)


@quiz_bp.route('/play/<int:attempt_id>')
@login_required
def play_quiz(attempt_id):
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    if attempt.user_id != current_user.id:
        flash('Unauthorized access to quiz attempt.', 'danger')
        return redirect(url_for('quiz.dashboard'))
    
    if attempt.status == 'COMPLETED':
        return redirect(url_for('quiz.results', attempt_id=attempt.id))

    q_ids_str = request.args.get('q_ids', '')
    if not q_ids_str:
        flash('Invalid quiz session.', 'danger')
        return redirect(url_for('quiz.start_quiz'))

    try:
        q_ids = [int(x) for x in q_ids_str.split(',') if x.strip()]
    except ValueError:
        flash('Invalid question set parameters.', 'danger')
        return redirect(url_for('quiz.start_quiz'))

    questions = Question.query.filter(Question.id.in_(q_ids)).all()
    
    # Shuffle options client-side or server-side without exposing correct flags
    quiz_payload = []
    for q in questions:
        options_data = [{'id': opt.id, 'text': opt.option_text} for opt in q.options]
        random.shuffle(options_data)
        quiz_payload.append({
            'id': q.id,
            'category': q.category.name if q.category else 'General',
            'question_text': q.question_text,
            'difficulty': q.difficulty,
            'options': options_data
        })

    return render_template(
        'quiz/quiz_runner.html',
        attempt=attempt,
        questions_payload=quiz_payload,
        q_ids_str=q_ids_str
    )


@quiz_bp.route('/submit/<int:attempt_id>', methods=['POST'])
@login_required
def submit_quiz(attempt_id):
    """
    SERVER-SIDE SCORING ENFORCEMENT:
    Receives JSON or Form payload of {question_id: selected_option_id}.
    Delegates calculation strictly to scoring.py.
    """
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    if attempt.user_id != current_user.id:
        flash('Unauthorized quiz submission.', 'danger')
        return redirect(url_for('quiz.dashboard'))

    if attempt.status == 'COMPLETED':
        return redirect(url_for('quiz.results', attempt_id=attempt.id))

    # Parse user answers
    if request.is_json:
        data = request.get_json()
        user_answers = data.get('answers', {})
        time_spent = data.get('time_spent', 0)
    else:
        user_answers = {}
        for key, val in request.form.items():
            if key.startswith('question_'):
                q_id = key.replace('question_', '')
                user_answers[q_id] = val
        time_spent = request.form.get('time_spent', type=int, default=0)

    # Server-Side Scoring Execution
    result = evaluate_quiz_submission(attempt.id, user_answers, total_time_spent=time_spent)

    if request.is_json:
        return jsonify({
            'success': True,
            'redirect_url': url_for('quiz.results', attempt_id=attempt.id)
        })

    flash('Quiz completed! Your score has been calculated.', 'success')
    return redirect(url_for('quiz.results', attempt_id=attempt.id))


@quiz_bp.route('/results/<int:attempt_id>')
@login_required
def results(attempt_id):
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    if attempt.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized access to quiz results.', 'danger')
        return redirect(url_for('quiz.dashboard'))

    # Calculate category performance breakdown for results page
    category_summary = {}
    for ans in attempt.answers:
        q = ans.question
        cat_name = q.category.name if q and q.category else 'General'
        if cat_name not in category_summary:
            category_summary[cat_name] = {'total': 0, 'correct': 0, 'remediation': q.remediation_advice if q else ''}
        category_summary[cat_name]['total'] += 1
        if ans.is_correct:
            category_summary[cat_name]['correct'] += 1

    return render_template(
        'quiz/results.html',
        attempt=attempt,
        category_summary=category_summary
    )


@quiz_bp.route('/leaderboard')
@login_required
def leaderboard():
    # Top performing staff members by best percentage score
    subquery = db.session.query(
        QuizAttempt.user_id,
        db.func.max(QuizAttempt.percentage_score).label('best_score'),
        db.func.count(QuizAttempt.id).label('attempts_count')
    ).filter(QuizAttempt.status == 'COMPLETED').group_by(QuizAttempt.user_id).subquery()

    top_staff = db.session.query(
        User,
        subquery.c.best_score,
        subquery.c.attempts_count
    ).join(subquery, User.id == subquery.c.user_id).order_by(subquery.c.best_score.desc()).limit(10).all()

    return render_template('quiz/leaderboard.html', top_staff=top_staff)
