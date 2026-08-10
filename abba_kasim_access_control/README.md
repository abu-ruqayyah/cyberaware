# Access Control Audit & Least Privilege Evaluation Platform

**Student Name**: Abba Kasim  
**Program**: 3MTT (3 Million Technical Talent) Program  
**Track**: Cybersecurity & Systems Hardening  
**Project Title**: Access Control Audit & Least Privilege Evaluation Platform  

---

## 🎯 Executive Summary
Over-privilege is a primary threat vector in modern enterprise environments. When users and roles accumulate unnecessary administrative, financial, or system privileges beyond their operational requirements, it leads to privilege escalation, insider threat abuse, and compliance violations.

The **Access Control Audit Platform** (`AccessAudit`) systematically evaluates role-based access control (RBAC) structures against the **Principle of Least Privilege (PoLP)** and **NIST SP 800-53 Access Control** standards. The application features:
- **Interactive Role Review Matrix**: Map roles to granular permissions with real-time entitlement right-sizing.
- **Automated Audit Engine**: Calculates an organizational Least Privilege Score (LPS) and detects toxic Separation of Duties (SoD) permission pairs.
- **Executive Reporting Engine**: Generates dynamic ReportLab PDF audit certificates and CSV spreadsheets.
- **Technical Safe Cyber Lab**: Authoritative evidence portal documenting VM lab testing with VirtualBox, Kali Linux, Wireshark, Nmap, and OWASP ZAP.

---

## 🏗️ Technology Architecture

- **Backend**: Python 3, Flask, SQLAlchemy ORM, Flask-Login
- **Frontend**: HTML5, Vanilla CSS, Bootstrap 5, Chart.js
- **Document Generation**: ReportLab PDF, CSV
- **Testing**: PyTest (Automated Test Suite)
- **Deployment**: Gunicorn WSGI, PostgreSQL / SQLite

---

## 🚀 Quick Start Instructions

1. **Navigate to Project Directory**:
   ```bash
   cd abba_kasim_access_control
   ```

2. **Activate Virtual Environment & Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Application**:
   ```bash
   python run.py
   ```

4. **Access Portal**:
   - Open browser to `http://127.0.0.1:5001`
   - **Lead Auditor Credentials**:
     - **Username**: `abba_auditor`
     - **Password**: `AuditAdminPassword123!`

---

## 🧪 Automated PyTest Suite

Run the full automated unit test suite:
```bash
python -m pytest -v
```
