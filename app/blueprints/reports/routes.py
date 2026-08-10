import os
from flask import Blueprint, render_template, send_from_directory, flash, redirect, url_for, Response, current_app
from flask_login import login_required, current_user
from app.models.quiz import QuizAttempt
from app.services.security_utils import admin_required
from app.services.pdf_generator import generate_attempt_pdf_report
from app.services.csv_exporter import export_quiz_attempts_csv
from app.services.audit_logger import log_event

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
@admin_required
def index():
    attempts = QuizAttempt.query.filter_by(status='COMPLETED').order_by(QuizAttempt.completed_at.desc()).all()
    return render_template('reports/report_dashboard.html', attempts=attempts)


@reports_bp.route('/pdf/attempt/<int:attempt_id>')
@login_required
def download_attempt_pdf(attempt_id):
    """
    Generate and serve protected PDF report.
    Permission: Attempt owner or Admin only.
    """
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    if attempt.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized access to report.', 'danger')
        return redirect(url_for('quiz.dashboard'))

    pdf_path = generate_attempt_pdf_report(attempt)
    filename = os.path.basename(pdf_path)

    log_event('REPORT_GENERATED', f"PDF Assessment Report generated for attempt #{attempt.id}.", user=current_user)

    return send_from_directory(
        directory=current_app.config['REPORTS_UPLOAD_DIR'],
        path=filename,
        as_attachment=True,
        download_name=f"CyberAware_Report_Attempt_{attempt.id}.pdf"
    )


@reports_bp.route('/csv/attempts')
@login_required
@admin_required
def export_csv():
    """
    Export all system quiz attempt records as CSV spreadsheet.
    Permission: Admin only.
    """
    csv_data = export_quiz_attempts_csv()
    log_event('REPORT_GENERATED', "System quiz attempts exported to CSV format.", user=current_user)
    
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=CyberAware_Quiz_Attempts_Export.csv"}
    )
