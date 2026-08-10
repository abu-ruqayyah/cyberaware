from app.models import LabEvidence, User
from datetime import date

def test_lab_evidence_unauthenticated_download_rejected(client, app):
    with app.app_context():
        user = User.query.filter_by(username='testadmin').first()
        lab = LabEvidence(
            title='Test Scan',
            category='Scanning',
            description='Localhost scan',
            tool='Nmap',
            target_environment='Localhost',
            date_performed=date.today(),
            finding='Open port',
            risk='LOW',
            recommendation='Filter port',
            remediation='Filtered port',
            evidence_file='test_evidence.txt',
            created_by=user.id
        )
        from app.extensions import db
        db.session.add(lab)
        db.session.commit()

        # Try unauthenticated download
        response = client.get(f'/lab/evidence/download/{lab.id}')
        assert response.status_code in [302, 401]
