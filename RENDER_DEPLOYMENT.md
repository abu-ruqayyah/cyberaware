# CyberAware — Render Deployment Guide
**Capstione Project Production Deployment Protocol**  
**Student:** Zainab Damina  

---

## Executive Overview

This guide outlines the step-by-step instructions to deploy **CyberAware: Gamified Security Awareness Assessment Platform** onto **Render** using a **Render Web Service** (Python 3 + Gunicorn WSGI) connected to a **Render PostgreSQL Managed Database**.

---

## ⚠️ Important Production Warnings

> [!WARNING]  
> **Ephemeral Filesystem Notice**: Render Free Web Services use an ephemeral filesystem. Locally generated/uploaded files (such as PDF reports in `instance/uploads/reports/` or evidence files in `instance/uploads/lab_evidence/`) may not persist across service redeployments or restarts. Persistent file storage requires mounting a Render Persistent Disk or integrating external cloud object storage (e.g. AWS S3). The local environment serves as the authoritative permanent laboratory evidence environment.

> [!NOTE]  
> **Render Free PostgreSQL Lifetime**: Render Free PostgreSQL instances currently have a 90-day expiration limit and are intended for demonstration, testing, and academic capstone evaluation.

---

## Step-by-Step Render Deployment Instructions

### 1. Push Repository to GitHub
Ensure all code and configuration files are committed to your GitHub repository:
```bash
git add .
git commit -m "Prepare CyberAware for Render Deployment"
git push origin main
```

### 2. Create Render PostgreSQL Instance
1. Log into your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** → **PostgreSQL**.
3. Configure Database:
   - **Name**: `cyberaware-db`
   - **Database**: `cyberaware`
   - **User**: `cyberaware_user`
   - **Region**: Select closest region (e.g. Oregon / Frankfurt)
   - **Instance Type**: Free
4. Click **Create Database**.
5. Once created, copy the **Internal Database URL** (or External Connection String).

### 3. Create Render Web Service
1. In Render Dashboard, click **New +** → **Web Service**.
2. Select **Build and deploy from a Git repository** and connect your GitHub repository `3mtt_capstone`.
3. Configure Service Details:
   - **Name**: `cyberaware-platform`
   - **Region**: Same region as your database
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     gunicorn --bind 0.0.0.0:$PORT wsgi:app
     ```
   - **Instance Type**: Free

### 4. Configure Environment Variables
In the **Environment** section of your Render Web Service, add the following key-value pairs:

| Key | Recommended Value / Setting | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | *[Paste Render PostgreSQL URL]* | Connection URI (auto-normalized from `postgres://` to `postgresql://`). |
| `SECRET_KEY` | *[Generate strong 32+ char secret]* | Session & CSRF signing key. |
| `FLASK_APP` | `wsgi.py` | Application entry point. |
| `FLASK_ENV` | `production` | Production environment flag. |
| `FLASK_DEBUG` | `False` | Disables debug mode and traceback exposure. |
| `SESSION_COOKIE_SECURE` | `True` | Mandates HTTPS-only session cookies. |
| `ADMIN_USERNAME` | `admin_prod` | Initial production administrator username. |
| `ADMIN_EMAIL` | `admin@cyberaware.local` | Initial production administrator email. |
| `ADMIN_PASSWORD` | *[Strong Production Password]* | Initial production administrator password. |
| `SEED_DEMO_DATA` | `False` | Disables sample staff & demo quiz seeding in production. |

### 5. Trigger Initial Deployment
1. Click **Deploy Web Service**.
2. Monitor the Render deployment logs. Gunicorn will bind to `0.0.0.0:$PORT` and `wsgi.py` will initialize database tables automatically via `seed_database()`.

---

## Deployment Verification & Smoke Testing Protocol

Once Render displays **Live**, perform the following verification steps:

1. **Health Check Endpoint**:
   - Navigate to `https://<your-render-app>.onrender.com/health`
   - Expected Output: `{"status": "ok"}` (HTTP 200 OK).
2. **Landing & Methodology Pages**:
   - Open home page `/`, `/methodology/assessment`, and `/methodology/lab`.
3. **Authentication & Admin Authorization**:
   - Log in using your configured `ADMIN_USERNAME` and `ADMIN_PASSWORD`.
   - Access `/admin/dashboard` to verify Trainer Command Center.
4. **Question Bank CRUD**:
   - Create, edit, and view questions under `/admin/questions`.
5. **Staff Quiz & Server-Side Scoring**:
   - Register a test staff account via `/auth/register`.
   - Complete a security awareness quiz under `/quiz/start`.
   - Verify server-calculated score, percentage, risk tier classification, and targeted remediation.
6. **PDF & CSV Reporting**:
   - Download attempt PDF assessment report and export system CSV analytics.
7. **Security Audit Logs**:
   - Inspect `/admin/audit-logs` to confirm security actions are captured with zero credential leakage.

---
*Render Deployment Protocol prepared for CyberAware Capstone Project.*
