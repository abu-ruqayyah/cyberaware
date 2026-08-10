import os
from app import create_app
from app.extensions import db
from app.models import User, Category, Question, Option, Badge, LabEvidence
from datetime import datetime, date

app = create_app()

def seed_database():
    """
    Initialize production schema and optionally seed demo data.
    Controlled via SEED_DEMO_DATA environment setting.
    """
    with app.app_context():
        os.makedirs(app.config['INSTANCE_DIR'], exist_ok=True)
        db.create_all()

        # Seed Badges
        badges_data = [
            {'name': 'Shield Cadet', 'description': 'Completed your first security awareness quiz assessment.', 'badge_icon': 'bi-shield-check', 'criteria_code': 'FIRST_QUIZ'},
            {'name': 'Security Champion', 'description': 'Achieved an Excellent score rating of 90% or higher.', 'badge_icon': 'bi-trophy', 'criteria_code': 'SECURITY_CHAMPION'},
            {'name': 'Phishing Destroyer', 'description': 'Scored 100% in the Phishing Security category.', 'badge_icon': 'bi-envelope-check', 'criteria_code': 'PHISHING_DESTROYER'}
        ]
        for b_info in badges_data:
            if not Badge.query.filter_by(criteria_code=b_info['criteria_code']).first():
                badge = Badge(**b_info)
                db.session.add(badge)

        # Seed 12 Core Categories
        categories_list = [
            ('Password Security', 'Best practices for strong passphrases and password hygiene.', 'bi-key'),
            ('Phishing', 'Identifying phishing emails, deceptive links, and spoofed domains.', 'bi-envelope-exclamation'),
            ('Social Engineering', 'Recognizing impersonation, pretexting, and baiting tactics.', 'bi-person-exclamation'),
            ('Malware', 'Understanding ransomware, spyware, trojans, and malicious payloads.', 'bi-bug'),
            ('Safe Browsing', 'Navigating HTTPS sites, avoiding fake popups, and secure Web usage.', 'bi-globe'),
            ('Email Security', 'Email header checks, attachment safety, and secure communications.', 'bi-mailbox'),
            ('Mobile Security', 'Securing smartphones, app permissions, and public Wi-Fi risks.', 'bi-phone'),
            ('Physical Security', 'Tailgating prevention, clean desk policy, and badge compliance.', 'bi-building-lock'),
            ('Data Protection', 'Data classification, encryption, and handling sensitive PII.', 'bi-file-earmark-lock'),
            ('Access Control', 'Principle of Least Privilege and Role-Based Access Control (RBAC).', 'bi-person-badge'),
            ('MFA', 'Multi-Factor Authentication methods, authenticator apps, and push tokens.', 'bi-device-auth'),
            ('Incident Reporting', 'Immediate reporting procedures for suspected security breaches.', 'bi-exclamation-octagon')
        ]

        cat_map = {}
        for name, desc, icon in categories_list:
            cat = Category.query.filter_by(name=name).first()
            if not cat:
                cat = Category(name=name, description=desc, icon_class=icon)
                db.session.add(cat)
                db.session.flush()
            cat_map[name] = cat.id

        # Seed Initial Admin Account (Environment-Driven)
        admin_username = app.config['ADMIN_USERNAME']
        admin_email = app.config['ADMIN_EMAIL']
        admin_password = app.config['ADMIN_PASSWORD']

        if not User.query.filter_by(role='ADMIN').first():
            admin = User(
                username=admin_username,
                email=admin_email,
                full_name='Security Trainer Admin',
                department='IT Security & Compliance',
                role='ADMIN'
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            print(f"Initial Admin account created: username='{admin_username}'")

        # Seed Demo Questions and Staff ONLY if SEED_DEMO_DATA is enabled
        if app.config.get('SEED_DEMO_DATA', True):
            if not User.query.filter_by(username='zainab').first():
                staff = User(
                    username='zainab',
                    email='zainab.damina@cyberaware.local',
                    full_name='Zainab Damina',
                    department='Information Assurance',
                    role='STAFF'
                )
                staff.set_password('StaffPassword123!')
                db.session.add(staff)

            questions_seed = [
                {
                    'cat': 'Password Security',
                    'text': 'Which of the following is the STRONGEST password creation strategy?',
                    'diff': 'EASY',
                    'exp': 'Passphrases combining 4+ random words with special characters produce high entropy that resists brute-force attacks.',
                    'rem': 'Adopt memorable passphrases of 14+ characters rather than complex short passwords.',
                    'opts': [
                        ('P@ssw0rd1', False),
                        ('Correct-Horse-Battery-Staple-2026!', True),
                        ('Zainab12345', False),
                        ('Admin2026', False)
                    ]
                },
                {
                    'cat': 'Phishing',
                    'text': 'You receive an urgent email claiming your bank account is suspended with a link to "verify identity". What should you do first?',
                    'diff': 'MEDIUM',
                    'exp': 'Urgency and threatening account suspension are classic phishing triggers. Never click links in unsolicited emails.',
                    'rem': 'Always inspect the sender domain and navigate to official portals independently.',
                    'opts': [
                        ('Click the link immediately to prevent suspension', False),
                        ('Report the email to IT Security and navigate to official portal manually', True),
                        ('Reply to the email requesting proof of identity', False),
                        ('Forward the email to all colleagues', False)
                    ]
                },
                {
                    'cat': 'Social Engineering',
                    'text': 'An unknown caller claiming to be IT Helpdesk requests your login password to fix a "server error". What should you do?',
                    'diff': 'EASY',
                    'exp': 'Legitimate IT administrators will NEVER ask for your password over phone or email.',
                    'rem': 'Never disclose passwords. Verify caller identity using official internal directories.',
                    'opts': [
                        ('Provide the password so the error is fixed quickly', False),
                        ('Refuse to share the password and immediately report the incident', True),
                        ('Provide a false password to test the caller', False),
                        ('Ask them to call back tomorrow', False)
                    ]
                },
                {
                    'cat': 'Malware',
                    'text': 'What is the primary indicator of a Ransomware infection?',
                    'diff': 'MEDIUM',
                    'exp': 'Ransomware encrypts user files and demands payment in cryptocurrency for decryption keys.',
                    'rem': 'Maintain offsite backups and never execute untrusted email attachments.',
                    'opts': [
                        ('User files are suddenly encrypted with ransom notes demanding payment', True),
                        ('The computer fan runs at maximum speed', False),
                        ('The monitor changes resolution automatically', False),
                        ('Web browser bookmarks are reorganized', False)
                    ]
                },
                {
                    'cat': 'Safe Browsing',
                    'text': 'What security protocol is indicated by a padlock icon and "https://" in the web address bar?',
                    'diff': 'EASY',
                    'exp': 'HTTPS uses Transport Layer Security (TLS/SSL) encryption to secure communication between browser and website.',
                    'rem': 'Ensure websites handling credentials or data use valid HTTPS certificates.',
                    'opts': [
                        ('Transport Layer Security (TLS/SSL) Encryption', True),
                        ('High-Speed Transport Protocol', False),
                        ('Hypertext Transfer Processing Standard', False),
                        ('Unencrypted Open Connection', False)
                    ]
                },
                {
                    'cat': 'MFA',
                    'text': 'Why is Multi-Factor Authentication (MFA) vastly superior to a single password?',
                    'diff': 'MEDIUM',
                    'exp': 'MFA requires two or more distinct factors (something you know, something you have, something you are), rendering stolen passwords insufficient for access.',
                    'rem': 'Enforce MFA across all corporate and personal web accounts.',
                    'opts': [
                        ('It prevents users from ever forgetting their passwords', False),
                        ('Even if a password is compromised, attackers cannot gain access without the second factor token', True),
                        ('It encrypts the hard drive automatically', False),
                        ('It replaces the need for firewall software', False)
                    ]
                }
            ]

            for q_data in questions_seed:
                c_id = cat_map.get(q_data['cat'])
                if c_id and not Question.query.filter_by(question_text=q_data['text']).first():
                    question = Question(
                        category_id=c_id,
                        question_text=q_data['text'],
                        difficulty=q_data['diff'],
                        explanation=q_data['exp'],
                        remediation_advice=q_data['rem']
                    )
                    db.session.add(question)
                    db.session.flush()

                    for opt_text, is_corr in q_data['opts']:
                        opt = Option(question_id=question.id, option_text=opt_text, is_correct=is_corr)
                        db.session.add(opt)

            admin_user = User.query.filter_by(role='ADMIN').first()
            if admin_user and not LabEvidence.query.filter_by(title='Localhost Port & Service Discovery Scan').first():
                sample_lab = LabEvidence(
                    title='Localhost Port & Service Discovery Scan',
                    category='Network Scanning',
                    description='Defensive enumeration of local service bounds using Nmap against localhost target.',
                    tool='Nmap',
                    target_environment='Localhost (127.0.0.1)',
                    date_performed=date.today(),
                    finding='Port 8080/tcp open exposing debug endpoint.',
                    risk='MEDIUM',
                    recommendation='Bind management interfaces exclusively to internal loopback and mandate authentication.',
                    remediation='Updated application config to restrict service binding and enforced TLS certificates.',
                    evidence_file='nmap_localhost_scan_evidence.txt',
                    created_by=admin_user.id
                )
                db.session.add(sample_lab)

        db.session.commit()

if __name__ == '__main__':
    seed_database()
    app.run(host='127.0.0.1', port=5000)
