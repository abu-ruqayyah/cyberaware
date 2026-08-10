import os
from app import create_app
from app.models import db, User, Role, Permission, AuditLog, LabEvidence
from app.services.audit_engine import AccessControlAuditEngine

app = create_app()

def seed_database():
    """Initializes tables and populates default access control audit data."""
    with app.app_context():
        db.create_all()
        
        # 1. Seed Permissions
        if Permission.query.count() == 0:
            permissions_list = [
                # System Admin
                Permission(code='exec:root_sudo', name='Execute Root / Sudo Commands', category='System Admin', risk_level='CRITICAL', description='Full administrative privilege execution on system nodes.'),
                Permission(code='delete:audit_logs', name='Delete Security Audit Logs', category='System Admin', risk_level='CRITICAL', description='Ability to clear or manipulate system audit trails.'),
                Permission(code='manage:firewall', name='Modify Network Firewall Rules', category='System Admin', risk_level='HIGH', description='Modify network access control lists and firewall boundaries.'),
                Permission(code='assign:admin_role', name='Assign Administrative Roles', category='System Admin', risk_level='CRITICAL', description='Grant administrative privileges to user accounts.'),
                
                # Data Access
                Permission(code='read:customer_pii', name='Read Customer PII Data', category='Data Access', risk_level='HIGH', description='Access sensitive personally identifiable customer information.'),
                Permission(code='export:bulk_database', name='Export Bulk Database Dumps', category='Data Access', risk_level='HIGH', description='Download complete database backups and table exports.'),
                Permission(code='read:employee_records', name='Read Staff HR Records', category='Data Access', risk_level='MODERATE', description='View internal staff HR profiles and department details.'),
                Permission(code='write:employee_records', name='Modify Staff HR Records', category='Data Access', risk_level='MODERATE', description='Update staff HR information.'),
                
                # Financial
                Permission(code='write:payroll', name='Modify Payroll Records', category='Financial', risk_level='HIGH', description='Edit employee salary and payout figures.'),
                Permission(code='approve:payroll_payout', name='Approve Payroll Disbursement', category='Financial', risk_level='CRITICAL', description='Authorize payout disbursement to banking endpoints.'),
                Permission(code='read:financial_reports', name='Read Quarterly Financial Reports', category='Financial', risk_level='MODERATE', description='View internal organizational financial statements.'),
                
                # User Provisioning
                Permission(code='create:user_account', name='Create New User Accounts', category='User Provisioning', risk_level='HIGH', description='Provision new user identities in directory services.'),
                Permission(code='reset:user_password', name='Reset User Passwords', category='User Provisioning', risk_level='MODERATE', description='Trigger administrative password resets for accounts.'),
                Permission(code='disable:user_account', name='Disable / Lock Accounts', category='User Provisioning', risk_level='MODERATE', description='Lock or deactivate user directory accounts.')
            ]
            db.session.add_all(permissions_list)
            db.session.commit()
            print("Seeded 14 granular permissions across 4 categories.")

        # Map permissions dictionary for fast lookup
        perm_map = {p.code: p for p in Permission.query.all()}

        # 2. Seed Roles
        if Role.query.count() == 0:
            role_sysadmin = Role(
                name='System Administrator',
                department='IT Security & Compliance',
                description='Full IT infrastructure maintenance and access management.',
                is_system_role=True
            )
            role_sysadmin.permissions.extend([
                perm_map['exec:root_sudo'], perm_map['delete:audit_logs'],
                perm_map['manage:firewall'], perm_map['assign:admin_role'],
                perm_map['create:user_account'], perm_map['reset:user_password']
            ])

            role_payroll = Role(
                name='Payroll Specialist',
                department='Finance',
                description='Responsible for preparing monthly staff payroll statements.',
                is_system_role=False
            )
            role_payroll.permissions.extend([
                perm_map['write:payroll'], perm_map['read:financial_reports'], perm_map['read:employee_records']
            ])

            # Demo Over-Privileged Role (Contains SoD Violations & Excessive Rights)
            role_overpriv_hr = Role(
                name='Over-Privileged HR Manager',
                department='Human Resources',
                description='HR Manager role with accumulated excessive admin and financial permissions.',
                is_system_role=False
            )
            role_overpriv_hr.permissions.extend([
                perm_map['read:employee_records'], perm_map['write:employee_records'],
                perm_map['exec:root_sudo'], perm_map['write:payroll'], perm_map['approve:payroll_payout']
            ])

            # Demo Vendor Role (Mass Exfiltration & Audit Tampering Risk)
            role_vendor = Role(
                name='Third-Party Contractor Support',
                department='External Vendor',
                description='External contractor support role with excessive data export and audit log rights.',
                is_system_role=False
            )
            role_vendor.permissions.extend([
                perm_map['read:customer_pii'], perm_map['export:bulk_database'], perm_map['delete:audit_logs']
            ])

            role_helpdesk = Role(
                name='Junior Helpdesk Analyst',
                department='IT Support',
                description='Frontline IT support handling password resets and account creation.',
                is_system_role=False
            )
            role_helpdesk.permissions.extend([
                perm_map['reset:user_password'], perm_map['create:user_account'], perm_map['read:employee_records']
            ])

            db.session.add_all([role_sysadmin, role_payroll, role_overpriv_hr, role_vendor, role_helpdesk])
            db.session.commit()
            print("Seeded 5 organizational roles with privilege variations.")

        # 3. Seed Users
        admin_username = app.config['ADMIN_USERNAME']
        admin_email = app.config['ADMIN_EMAIL']
        admin_password = app.config['ADMIN_PASSWORD']

        admin_user = User.query.filter_by(role='ADMIN').first()
        if not admin_user:
            admin_user = User(
                username=admin_username,
                email=admin_email,
                full_name='Abba Kasim (Lead Auditor)',
                department='IT Security & Compliance',
                job_title='Principal Security Auditor',
                role='ADMIN',
                is_active_account=True
            )
            admin_user.set_password(admin_password)
            
            # Assign Sysadmin role
            sysadmin_role = Role.query.filter_by(name='System Administrator').first()
            if sysadmin_role:
                admin_user.assigned_roles.append(sysadmin_role)
                
            db.session.add(admin_user)
            print(f"Initial Auditor Admin account created: username='{admin_username}'")
        else:
            admin_user.username = admin_username
            admin_user.email = admin_email
            admin_user.set_password(admin_password)
            print(f"Auditor Admin account updated: username='{admin_username}'")

        if app.config.get('SEED_DEMO_DATA', True):
            # Seed Demo Staff & Dormant Admin
            if User.query.filter_by(username='sarah_hr').first() is None:
                sarah = User(
                    username='sarah_hr',
                    email='sarah@accessaudit.local',
                    full_name='Sarah Jenkins',
                    department='Human Resources',
                    job_title='HR Lead',
                    role='AUDITEE',
                    is_active_account=True
                )
                sarah.set_password('StaffPassword123!')
                hr_role = Role.query.filter_by(name='Over-Privileged HR Manager').first()
                if hr_role:
                    sarah.assigned_roles.append(hr_role)
                db.session.add(sarah)

            if User.query.filter_by(username='contractor_mike').first() is None:
                mike = User(
                    username='contractor_mike',
                    email='mike.vendor@external.com',
                    full_name='Mike Vance (Contractor)',
                    department='External Vendor',
                    job_title='Database Migration Specialist',
                    role='ADMIN', # Inactive Admin demo!
                    is_active_account=False # Dormant inactive account!
                )
                mike.set_password('VendorPassword123!')
                vendor_role = Role.query.filter_by(name='Third-Party Contractor Support').first()
                if vendor_role:
                    mike.assigned_roles.append(vendor_role)
                db.session.add(mike)

            # Seed Demo Lab Evidence documentation if none exists
            if LabEvidence.query.count() == 0:
                demo_evidence_list = [
                    LabEvidence(
                        title='Wireshark Packet Analysis — Plaintext Credential & Role Exposure',
                        tool_category='Wireshark',
                        filename='wireshark_broken_access_control.pcapng',
                        file_path=os.path.join(app.config['LAB_EVIDENCE_FOLDER'], 'wireshark_broken_access_control.pcapng'),
                        description='Captured HTTP GET request traffic revealing unencrypted session tokens and administrative API endpoint traversal.',
                        findings_summary='Demonstrated OWASP A01:2021 Broken Access Control vulnerability where non-admin user tokens were accepted on /api/admin/roles.',
                        uploaded_by='Abba Kasim'
                    ),
                    LabEvidence(
                        title='Nmap Permission & Service Exposure Audit Scan',
                        tool_category='Nmap',
                        filename='nmap_access_control_audit.xml',
                        file_path=os.path.join(app.config['LAB_EVIDENCE_FOLDER'], 'nmap_access_control_audit.xml'),
                        description='Targeted Nmap NSE script scan auditing exposed SMB/RDP administrative shares and unauthorized port bindings.',
                        findings_summary='Identified open SMB share allowing read/write access to HR payroll folders without active kerberos authentication.',
                        uploaded_by='Abba Kasim'
                    ),
                    LabEvidence(
                        title='OWASP ZAP Automated Access Control Assessment',
                        tool_category='OWASP ZAP',
                        filename='owasp_zap_access_control_report.json',
                        file_path=os.path.join(app.config['LAB_EVIDENCE_FOLDER'], 'owasp_zap_access_control_report.json'),
                        description='Automated OWASP ZAP Access Control Matrix scan executing horizontal and vertical privilege escalation vectors.',
                        findings_summary='Flagged 3 vertical privilege escalation vectors where lower-tier accounts accessed higher-tier administrative functions.',
                        uploaded_by='Abba Kasim'
                    )
                ]
                db.session.add_all(demo_evidence_list)

            db.session.commit()

            # Execute Initial Access Control Audit if no session exists
            AccessControlAuditEngine.run_full_audit(
                executed_by='Abba Kasim (Lead Auditor)',
                session_title='Baseline Least Privilege Access Control Audit'
            )
            print("Executed initial Baseline Least Privilege Audit.")

if __name__ == '__main__':
    seed_database()
    app.run(debug=True, port=5001)
