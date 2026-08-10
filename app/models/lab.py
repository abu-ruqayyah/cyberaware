from datetime import datetime
from app.extensions import db

class LabEvidence(db.Model):
    __tablename__ = 'lab_evidence'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(80), nullable=False)  # Network Scanning, Traffic Analysis, Web Vulnerability, System Hardening
    description = db.Column(db.Text, nullable=False)
    tool = db.Column(db.String(50), nullable=False)  # Kali Linux, Nmap, Wireshark, OWASP ZAP
    target_environment = db.Column(db.String(150), nullable=False)  # Localhost, Student VM, Lab Target
    date_performed = db.Column(db.Date, nullable=False)
    finding = db.Column(db.Text, nullable=False)
    risk = db.Column(db.String(20), nullable=False, default='MEDIUM')  # LOW, MEDIUM, HIGH, CRITICAL
    recommendation = db.Column(db.Text, nullable=False)
    remediation = db.Column(db.Text, nullable=False)
    evidence_file = db.Column(db.String(255), nullable=False)  # Stored in instance/uploads/lab_evidence/
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<LabEvidence {self.id}: {self.title} ({self.tool})>'
