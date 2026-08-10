# CyberAware — Gamified Security Awareness Assessment Platform
**Academic Cybersecurity Capstone Project**  
**Student Name:** Zainab Damina  
**Institution:** 3MTT Cybersecurity Program  

---

## Executive Overview

**CyberAware** is an enterprise-grade, gamified security awareness assessment web application developed to transform corporate cybersecurity training into an interactive, measurable, and engaging learning experience.

Traditional staff security awareness training often relies on passive video watching or static reading material, leading to low retention rates and unmeasured risk exposure. CyberAware solves this problem by combining interactive micro-assessment quizzes, real-time timer dynamics, server-side evaluated scoring, automated PDF certificate generation, analytical CSV exports, and a dedicated safe cybersecurity laboratory module.

---

## Problem Statement

Human error remains the leading root cause of enterprise security incidents, account takeovers, and phishing compromises. Organizations struggle with:
1. **Low Staff Engagement**: Traditional mandatory annual training is perceived as dry and non-interactive.
2. **Lack of Measurable Risk Analytics**: Security teams lack visibility into specific category weaknesses (e.g. distinguishing password hygiene flaws from phishing vulnerability).
3. **Insecure Training Tools**: Ineffective training systems often evaluate scores on the client-side or leak correct answer keys in browser code.
4. **Lack of Practical Laboratory Evidence**: Training frameworks rarely bridge the gap between theoretical staff awareness and hands-on technical defensive security analysis.

---

## Project Objectives

- **Gamified Learning**: Engage staff participants with real-time countdown timers, progress bars, achievement badges, and opt-in leaderboards.
- **Server-Side Security Enforcement**: Guarantee tamper-proof scoring where quiz answers are evaluated exclusively on the server.
- **Targeted Remediation & Reporting**: Provide immediate category weakness breakdowns and compile official ReportLab PDF evaluation reports.
- **Security Audit Logging**: Record immutable security events for authentication, quiz submissions, administration, and file uploads while redacting credentials.
- **Safe Cybersecurity Laboratory**: Document defensive technical security assessments (Kali Linux, Nmap, Wireshark, OWASP ZAP) conducted strictly in authorized, controlled lab environments.

---

## Technology Stack

- **Core Backend Framework**: Python 3.10+ & Flask 3.x
- **Database & ORM**: SQLite & SQLAlchemy ORM
- **Authentication & Security**: Flask-Login, Flask-WTF (CSRF), Flask-Limiter (Rate Limiting), Werkzeug PBKDF2-SHA256 password hashing
- **Frontend UI & Styling**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5, Chart.js, Bootstrap Icons, Glassmorphism UI tokens
- **Reporting Services**: Python ReportLab PDF Generator & Python CSV Exporter
- **Automated Testing Suite**: PyTest 8.x
- **Production WSGI Application Servers**: Gunicorn / Waitress

---

## System Architecture

CyberAware follows a modular **Model-View-Controller (MVC) / Blueprint** design pattern:

```
3mtt_capstone/
├── app/
│   ├── __init__.py                 # Application factory (create_app, extension setup, security headers)
│   ├── config.py                   # Environment-driven configuration (SECRET_KEY, DATABASE_URL)
│   ├── models/                     # SQLAlchemy ORM Models
│   │   ├── user.py                 # User & Role models
│   │   ├── question.py             # Category, Question, & Option models
│   │   ├── quiz.py                 # QuizAttempt, AnswerLog, Badge, UserBadge models
│   │   ├── lab.py                  # LabEvidence model
│   │   └── audit.py                # AuditLog model
│   ├── blueprints/                 # Modular Route Controllers
│   │   ├── auth/                   # Registration, Login, Logout handlers
│   │   ├── admin/                  # Command Center, Question Bank CRUD, User Directory, Audit Logs
│   │   ├── quiz/                   # Quiz Runner, Instant Feedback, Leaderboard
│   │   ├── reports/                # ReportLab PDF & CSV Export routes
│   │   ├── lab/                    # Safe Cybersecurity Lab & Protected Download routes
│   │   └── methodology/            # Academic Assessment & Technical Lab Workflow pages
│   ├── services/                   # Business Logic Layer
│   │   ├── scoring.py              # Server-Side Scoring Engine & Risk Tier Mapping
│   │   ├── audit_logger.py         # Security Audit Logger (Redacts credentials)
│   │   ├── pdf_generator.py        # ReportLab PDF Certificate Compiler
│   │   ├── csv_exporter.py         # CSV Analytics Exporter
│   │   └── security_utils.py       # RBAC Decorators & File Sanitizers
│   ├── static/                     # PUBLIC Static Web Assets ONLY
│   └── templates/                  # Jinja2 HTML Templates
├── instance/                       # PROTECTED Directory (Non-public storage)
│   ├── platform.db                 # Relational Database
│   └── uploads/                    # PROTECTED File Storage
│       ├── reports/                # Generated PDF Reports
│       └── lab_evidence/           # Uploaded Lab Screenshots & Evidence
├── tests/                          # Automated PyTest Test Suite
├── .env.example                    # Production Environment Template
├── requirements.txt                # Python Dependencies
├── run.py                          # Development Launcher & Schema Seeder
└── wsgi.py                         # Production WSGI Entry Point
```

---

## Major Features

### 1. Staff Quiz Engine & Gamification
- **12 Security Categories**: Password Security, Phishing, Social Engineering, Malware, Safe Browsing, Email Security, Mobile Security, Physical Security, Data Protection, Access Control, MFA, Incident Reporting.
- **Dynamic Timer**: Configurable countdown timer (30s per question) with dynamic progress bar.
- **Achievement Badges**: Auto-granted badges (`Shield Cadet`, `Security Champion`, `Phishing Destroyer`).
- **Leaderboard**: Opt-in staff ranking by personal best score.

### 2. Administrator & Trainer Command Center
- **Interactive Analytics**: Chart.js question category distribution and recent performance metrics.
- **Question Bank CRUD**: Full management interface to add, edit, or remove questions, options, difficulty ratings, and educational explanations.
- **Audit Logs Viewer**: Searchable log table capturing all security events.

### 3. Automated Reporting
- **ReportLab PDF Certificates**: Generates individual PDF assessment certificates with metadata, score banners, question logs, and category weakness matrices.
- **CSV Data Export**: One-click download of all quiz attempt records for spreadsheet analysis.

### 4. Safe Cybersecurity Laboratory Evidence
- Documented findings from **Kali Linux**, **Nmap**, **Wireshark**, and **OWASP ZAP**.
- Protected file storage in `instance/uploads/lab_evidence/` served exclusively to authenticated users.

---

## Security Controls

1. **Server-Side Scoring**: Answer keys are never transmitted to the client browser. Submissions send selected option IDs to `scoring.py` for server-side accuracy verification against the database.
2. **Protected Upload Directory**: User uploads and PDF reports are stored in `instance/uploads/` outside the web root (`app/static/`). Access is controlled via authenticated Flask routes using `send_from_directory`.
3. **Audit Logging & Credential Redaction**: All security events are logged with actor ID, IP address, user-agent, and event type. Password strings are automatically redacted.
4. **Universal CSRF Protection**: All state-changing forms (`POST`, `PUT`, `DELETE`) enforce **Flask-WTF** CSRF token validation.
5. **Security HTTP Headers**:
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: SAMEORIGIN`
   - `Referrer-Policy: strict-origin-when-cross-origin`
   - `Content-Security-Policy`: Restricts resource loading to trusted origin and CDNs.
6. **Password Hashing & Session Security**: Werkzeug PBKDF2-SHA256 hashing, `HttpOnly=True`, `SameSite='Lax'`, and 30-minute session expiration.

---

## Organizational Risk Classification Matrix

| Score Percentage (%) | Assessment Level | Risk & Awareness Classification |
| :---: | :---: | :--- |
| **90 – 100%** | **Excellent** | **Low Awareness Risk** |
| **80 – 89%** | **Very Good** | **Moderate-Low Risk** |
| **70 – 79%** | **Good** | **Acceptable Threshold** |
| **60 – 69%** | **Needs Improvement** | **Elevated Awareness Risk** |
| **Below 60%** | **High Awareness Risk** | **Critical Risk** |

---

## Safe Cybersecurity Laboratory Scope

All technical security testing documented in the lab evidence module is performed **ONLY** against authorized targets:
- `Localhost (127.0.0.1)`
- `Student's Isolated Virtual Machines`
- `Intentionally vulnerable lab targets (e.g. Metasploitable, OWASP Juice Shop)`

*Testing against public websites or unauthorized infrastructure is strictly prohibited.*

---

## Automated PyTest Verification Matrix

The test suite in `tests/` contains 15 automated test cases:
- `test_auth.py`: Registration, login, logout, password security.
- `test_authorization.py`: RBAC enforcement (Staff blocked from Admin routes with 403 Forbidden).
- `test_csrf.py`: Validates CSRF token rejection (400 Bad Request) on unauthenticated POSTs.
- `test_scoring.py`: Server-side scoring accuracy, time calculations, percentage computations, risk tier assignments.
- `test_questions.py`: Question Bank CRUD operations.
- `test_reports.py`: PDF report compiler and CSV exporter routines.
- `test_audit.py`: Event logging and verification of zero credential leakage.
- `test_lab_access.py`: Access control verification on `instance/uploads/` files.

To run the test suite:
```bash
python -m pytest -v
```

---

## Production Deployment Preparation

### Environment Setup
1. Copy `.env.example` to `.env` and fill in production secrets:
   ```bash
   cp .env.example .env
   ```
2. Configure mandatory environment variables:
   ```ini
   SECRET_KEY=your-production-super-secret-key-32-chars
   DATABASE_URL=sqlite:///instance/platform.db
   FLASK_ENV=production
   FLASK_DEBUG=False
   SESSION_COOKIE_SECURE=True
   ADMIN_USERNAME=admin_prod
   ADMIN_EMAIL=admin@organization.org
   ADMIN_PASSWORD=StrongProductionPassword123!
   SEED_DEMO_DATA=False
   ```

### WSGI Startup Commands
- **Windows Production (Waitress)**:
  ```bash
  waitress-serve --port=5000 wsgi:app
  ```
- **Linux / Cloud Production (Gunicorn)**:
  ```bash
  gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:app
  ```

---

## Project Limitations & Future Improvements

### Limitations
- Uses SQLite database by default; for large-scale enterprise deployments (> 10,000 concurrent staff users), migrating to PostgreSQL via SQLAlchemy `DATABASE_URL` is recommended.
- PDF generation uses standard ReportLab page templates without custom vector graphics.

### Future Improvements
- Multi-tenant organizational partitioning for enterprise client isolation.
- Automated simulated phishing campaign module (email webhook triggers).
- Integration with Enterprise Single Sign-On (SSO / SAML 2.0 / OAuth2).

---
*Developed for 3MTT Cybersecurity Capstone Project — Zainab Damina*
