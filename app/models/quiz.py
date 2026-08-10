from datetime import datetime
from app.extensions import db

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    score_achieved = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    percentage_score = db.Column(db.Float, default=0.0)
    assessment_level = db.Column(db.String(40), nullable=True)
    time_spent_seconds = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='IN_PROGRESS')  # IN_PROGRESS, COMPLETED, TIMED_OUT

    # Relationships
    answers = db.relationship('AnswerLog', backref='attempt', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<QuizAttempt {self.id} User {self.user_id} Score: {self.percentage_score}%>'


class AnswerLog(db.Model):
    __tablename__ = 'answer_logs'

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    selected_option_id = db.Column(db.Integer, db.ForeignKey('options.id'), nullable=True)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)
    time_spent_seconds = db.Column(db.Integer, default=0)


class Badge(db.Model):
    __tablename__ = 'badges'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    badge_icon = db.Column(db.String(100), nullable=False, default='bi-award')
    criteria_code = db.Column(db.String(50), nullable=False)  # FIRST_QUIZ, PERFECT_SCORE, PHISHING_EXPERT, etc.

    # Relationships
    user_badges = db.relationship('UserBadge', backref='badge', lazy=True)

    def __repr__(self):
        return f'<Badge {self.name}>'


class UserBadge(db.Model):
    __tablename__ = 'user_badges'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<UserBadge User {self.user_id} Badge {self.badge_id}>'
