import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models.lab import LabEvidence
from app.services.security_utils import admin_required, allowed_file, get_secure_filename
from app.services.audit_logger import log_event

lab_bp = Blueprint('lab', __name__, url_prefix='/lab')

@lab_bp.route('/')
@login_required
def index():
    evidences = LabEvidence.query.order_by(LabEvidence.date_performed.desc()).all()
    return render_template('lab/index.html', evidences=evidences)


@lab_bp.route('/evidence/<int:id>')
@login_required
def detail(id):
    evidence = LabEvidence.query.get_or_404(id)
    return render_template('lab/detail.html', evidence=evidence)


@lab_bp.route('/upload', methods=['GET', 'POST'])
@login_required
@admin_required
def upload():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        tool = request.form.get('tool', '').strip()
        target_environment = request.form.get('target_environment', '').strip()
        date_str = request.form.get('date_performed', '')
        finding = request.form.get('finding', '').strip()
        risk = request.form.get('risk', 'MEDIUM').strip()
        recommendation = request.form.get('recommendation', '').strip()
        remediation = request.form.get('remediation', '').strip()

        file = request.files.get('evidence_file')

        if not title or not category or not description or not tool or not target_environment or not finding or not file:
            flash('All required fields and evidence file must be provided.', 'danger')
            return render_template('lab/upload_evidence.html')

        if not allowed_file(file.filename):
            flash('Invalid file extension. Permitted types: PNG, JPG, PDF, TXT.', 'danger')
            return render_template('lab/upload_evidence.html')

        try:
            date_performed = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()
        except ValueError:
            date_performed = datetime.utcnow().date()

        filename = get_secure_filename(file.filename)
        # Prepend timestamp to avoid collision
        timestamp_prefix = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
        unique_filename = f"{timestamp_prefix}{filename}"

        upload_dir = current_app.config['LAB_EVIDENCE_UPLOAD_DIR']
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)

        evidence = LabEvidence(
            title=title,
            category=category,
            description=description,
            tool=tool,
            target_environment=target_environment,
            date_performed=date_performed,
            finding=finding,
            risk=risk,
            recommendation=recommendation,
            remediation=remediation,
            evidence_file=unique_filename,
            created_by=current_user.id
        )
        db.session.add(evidence)
        db.session.commit()

        log_event('LAB_EVIDENCE_UPLOADED', f"Lab evidence uploaded: '{title}' ({tool}) for target '{target_environment}'.", user=current_user)
        flash('Cybersecurity lab evidence record created successfully!', 'success')
        return redirect(url_for('lab.index'))

    return render_template('lab/upload_evidence.html')


@lab_bp.route('/evidence/download/<int:id>')
@login_required
def download_file(id):
    """
    PROTECTED DOWNLOAD HANDLER:
    Restricted to authenticated users only.
    Serves files from instance/uploads/lab_evidence/ outside public web root.
    """
    evidence = LabEvidence.query.get_or_404(id)
    upload_dir = current_app.config['LAB_EVIDENCE_UPLOAD_DIR']
    
    return send_from_directory(
        directory=upload_dir,
        path=evidence.evidence_file,
        as_attachment=True
    )
