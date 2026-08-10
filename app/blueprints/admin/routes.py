from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models.user import User
from app.models.question import Question, Category, Option
from app.models.quiz import QuizAttempt
from app.models.audit import AuditLog
from app.services.security_utils import admin_required
from app.services.audit_logger import log_event

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.filter_by(role='STAFF').count()
    total_questions = Question.query.count()
    total_attempts = QuizAttempt.query.filter_by(status='COMPLETED').count()

    attempts = QuizAttempt.query.filter_by(status='COMPLETED').all()
    avg_score = round(sum(a.percentage_score for a in attempts) / len(attempts), 1) if attempts else 0.0

    # Category performance metrics
    categories = Category.query.all()
    cat_metrics = []
    for cat in categories:
        q_count = Question.query.filter_by(category_id=cat.id).count()
        cat_metrics.append({
            'name': cat.name,
            'question_count': q_count
        })

    recent_attempts = QuizAttempt.query.order_by(QuizAttempt.started_at.desc()).limit(10).all()

    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_questions=total_questions,
        total_attempts=total_attempts,
        avg_score=avg_score,
        cat_metrics=cat_metrics,
        recent_attempts=recent_attempts
    )


@admin_bp.route('/questions')
@login_required
@admin_required
def question_list():
    category_id = request.args.get('category_id', type=int)
    query = Question.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    questions = query.order_by(Question.id.desc()).all()
    categories = Category.query.all()
    return render_template('admin/question_list.html', questions=questions, categories=categories, selected_category=category_id)


@admin_bp.route('/questions/new', methods=['GET', 'POST'])
@login_required
@admin_required
def question_create():
    categories = Category.query.all()
    if request.method == 'POST':
        category_id = request.form.get('category_id', type=int)
        question_text = request.form.get('question_text', '').strip()
        difficulty = request.form.get('difficulty', 'MEDIUM')
        explanation = request.form.get('explanation', '').strip()
        remediation_advice = request.form.get('remediation_advice', '').strip()

        option_texts = request.form.getlist('option_text[]')
        correct_index = request.form.get('correct_option', type=int)

        if not category_id or not question_text or not explanation or len(option_texts) < 2:
            flash('Please complete all required fields and provide at least 2 options.', 'danger')
            return render_template('admin/question_form.html', categories=categories)

        question = Question(
            category_id=category_id,
            question_text=question_text,
            difficulty=difficulty,
            explanation=explanation,
            remediation_advice=remediation_advice
        )
        db.session.add(question)
        db.session.flush()

        for idx, opt_text in enumerate(option_texts):
            opt_text = opt_text.strip()
            if opt_text:
                is_correct = (idx == correct_index)
                option = Option(question_id=question.id, option_text=opt_text, is_correct=is_correct)
                db.session.add(option)

        db.session.commit()
        log_event('QUESTION_CREATED', f"Question #{question.id} created under category ID {category_id}.")
        flash('Question added successfully!', 'success')
        return redirect(url_for('admin.question_list'))

    return render_template('admin/question_form.html', categories=categories, question=None)


@admin_bp.route('/questions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def question_edit(id):
    question = Question.query.get_or_404(id)
    categories = Category.query.all()

    if request.method == 'POST':
        question.category_id = request.form.get('category_id', type=int)
        question.question_text = request.form.get('question_text', '').strip()
        question.difficulty = request.form.get('difficulty', 'MEDIUM')
        question.explanation = request.form.get('explanation', '').strip()
        question.remediation_advice = request.form.get('remediation_advice', '').strip()

        # Update options
        Option.query.filter_by(question_id=question.id).delete()
        option_texts = request.form.getlist('option_text[]')
        correct_index = request.form.get('correct_option', type=int)

        for idx, opt_text in enumerate(option_texts):
            opt_text = opt_text.strip()
            if opt_text:
                is_correct = (idx == correct_index)
                option = Option(question_id=question.id, option_text=opt_text, is_correct=is_correct)
                db.session.add(option)

        db.session.commit()
        log_event('QUESTION_UPDATED', f"Question #{question.id} updated.")
        flash('Question updated successfully!', 'success')
        return redirect(url_for('admin.question_list'))

    return render_template('admin/question_form.html', categories=categories, question=question)


@admin_bp.route('/questions/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def question_delete(id):
    question = Question.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()
    log_event('QUESTION_DELETED', f"Question #{id} deleted.")
    flash('Question deleted successfully.', 'info')
    return redirect(url_for('admin.question_list'))


@admin_bp.route('/users')
@login_required
@admin_required
def users_list():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users_list.html', users=users)


@admin_bp.route('/audit-logs')
@login_required
@admin_required
def audit_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return render_template('admin/audit_logs.html', logs=logs)
