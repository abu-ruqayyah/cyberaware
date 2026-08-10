from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, limiter
from app.models.user import User
from app.services.audit_logger import log_event

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('quiz.dashboard'))

    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username_or_email or not password:
            flash('Please enter both username/email and password.', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Account is deactivated. Please contact an administrator.', 'danger')
                return render_template('auth/login.html')

            login_user(user, remember=True)
            user.last_login = datetime.utcnow()
            db.session.commit()

            event_type = 'ADMIN_LOGIN' if user.is_admin else 'STAFF_LOGIN'
            log_event(event_type, f"User '{user.username}' logged in successfully.", user=user)

            flash(f'Welcome back, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('quiz.dashboard'))
        else:
            log_event('FAILED_LOGIN', f"Failed login attempt for input: '{username_or_email}'")
            flash('Invalid username/email or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('quiz.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        full_name = request.form.get('full_name', '').strip()
        department = request.form.get('department', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not email or not full_name or not password:
            flash('All required fields must be filled out.', 'danger')
            return render_template('auth/register_staff.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register_staff.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('auth/register_staff.html')

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email address is already registered.', 'warning')
            return render_template('auth/register_staff.html')

        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            department=department or 'General',
            role='STAFF'
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        log_event('STAFF_REGISTERED', f"New staff account created: '{username}' ({email})", user=new_user)
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register_staff.html')


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    log_event('LOGOUT', f"User '{current_user.username}' logged out.", user=current_user)
    logout_user()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('auth.login'))
