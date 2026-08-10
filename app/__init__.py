import os
from flask import Flask, render_template, jsonify
from app.config import Config
from app.extensions import db, login_manager, csrf, limiter

def create_app(config_class=Config, config_override=None):
    app = Flask(__name__)
    app.config.from_object(config_class)
    if config_override:
        if isinstance(config_override, dict):
            app.config.update(config_override)
        else:
            app.config.from_object(config_override)

    # User loader for Flask-Login
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Ensure instance & upload directories exist
    if 'INSTANCE_DIR' in app.config:
        os.makedirs(app.config['INSTANCE_DIR'], exist_ok=True)
    os.makedirs(app.config['REPORTS_UPLOAD_DIR'], exist_ok=True)
    os.makedirs(app.config['LAB_EVIDENCE_UPLOAD_DIR'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # Register Security Headers
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "img-src 'self' data:; "
            "connect-src 'self';"
        )
        return response

    # Health Check Endpoint (Unauthenticated, Zero Data Exposure)
    @app.route('/health')
    def health():
        return jsonify({"status": "ok"}), 200

    # Register Blueprints
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.admin.routes import admin_bp
    from app.blueprints.quiz.routes import quiz_bp
    from app.blueprints.reports.routes import reports_bp
    from app.blueprints.lab.routes import lab_bp
    from app.blueprints.methodology.routes import methodology_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(lab_bp)
    app.register_blueprint(methodology_bp)

    # Root Route
    @app.route('/')
    def index():
        return render_template('index.html')

    # Custom Error Handlers (Safe Production Error Pages - Zero Traceback Leakage)
    @app.errorhandler(400)
    def bad_request_error(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden_access(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # Shell context for CLI
    @app.shell_context_processor
    def make_shell_context():
        from app.models import User, Category, Question, Option, QuizAttempt, AuditLog, LabEvidence, Badge
        return {
            'db': db,
            'User': User,
            'Category': Category,
            'Question': Question,
            'Option': Option,
            'QuizAttempt': QuizAttempt,
            'AuditLog': AuditLog,
            'LabEvidence': LabEvidence,
            'Badge': Badge
        }

    return app
