import os
from datetime import datetime
from flask import current_app
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_attempt_pdf_report(attempt):
    """
    Generate an official PDF security assessment report for a quiz attempt.
    Saves PDF file to instance/uploads/reports/ (protected, non-public directory).
    """
    reports_dir = current_app.config['REPORTS_UPLOAD_DIR']
    os.makedirs(reports_dir, exist_ok=True)

    filename = f"cyberaware_report_attempt_{attempt.id}.pdf"
    filepath = os.path.join(reports_dir, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=colors.HexColor('#2563EB'),
        spaceAfter=15
    )

    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=12,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155')
    )

    story = []

    # Header
    story.append(Paragraph("CyberAware", title_style))
    story.append(Paragraph("Gamified Security Awareness Assessment Platform — Staff Report", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=15))

    # Participant Metadata Table
    user = attempt.user
    meta_data = [
        [Paragraph("<b>Participant Name:</b>", body_style), Paragraph(user.full_name, body_style),
         Paragraph("<b>Assessment Date:</b>", body_style), Paragraph(attempt.completed_at.strftime('%Y-%m-%d %H:%M') if attempt.completed_at else 'N/A', body_style)],
        [Paragraph("<b>Department:</b>", body_style), Paragraph(user.department or 'General', body_style),
         Paragraph("<b>Attempt ID:</b>", body_style), Paragraph(f"#{attempt.id}", body_style)],
        [Paragraph("<b>Email:</b>", body_style), Paragraph(user.email, body_style),
         Paragraph("<b>Role:</b>", body_style), Paragraph(user.role, body_style)]
    ]

    meta_table = Table(meta_data, colWidths=[110, 160, 110, 160])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#F1F5F9')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # Score Card Banner
    level_color = '#16A34A' if attempt.percentage_score >= 80 else ('#D97706' if attempt.percentage_score >= 60 else '#DC2626')
    
    score_data = [
        [Paragraph("<b>Total Questions</b>", body_style), Paragraph("<b>Correct Answers</b>", body_style), Paragraph("<b>Score Percentage</b>", body_style), Paragraph("<b>Awareness Classification</b>", body_style)],
        [Paragraph(f"<b>{attempt.total_questions}</b>", body_style), Paragraph(f"<b>{attempt.score_achieved}</b>", body_style), Paragraph(f"<b>{attempt.percentage_score}%</b>", body_style), Paragraph(f"<b>{attempt.assessment_level}</b>", body_style)]
    ]
    score_table = Table(score_data, colWidths=[120, 120, 120, 180])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TEXTCOLOR', (3,1), (3,1), colors.HexColor(level_color)),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 15))

    # Detailed Question Performance Breakdown
    story.append(Paragraph("Category Performance & Identified Weaknesses", h2_style))

    # Query answer logs
    answer_rows = [
        [Paragraph("<b>#</b>", body_style), Paragraph("<b>Category</b>", body_style), Paragraph("<b>Question</b>", body_style), Paragraph("<b>Result</b>", body_style)]
    ]
    
    idx = 1
    for ans in attempt.answers:
        q = ans.question
        cat_name = q.category.name if q and q.category else "General"
        q_text = (q.question_text[:50] + "...") if q and len(q.question_text) > 50 else (q.question_text if q else "N/A")
        result_str = "<font color='#16A34A'><b>CORRECT</b></font>" if ans.is_correct else "<font color='#DC2626'><b>INCORRECT</b></font>"
        
        answer_rows.append([
            Paragraph(str(idx), body_style),
            Paragraph(cat_name, body_style),
            Paragraph(q_text, body_style),
            Paragraph(result_str, body_style)
        ])
        idx += 1

    ans_table = Table(answer_rows, colWidths=[30, 130, 280, 100])
    ans_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(ans_table)
    story.append(Spacer(1, 15))

    # Remediation Recommendations
    story.append(Paragraph("Targeted Remediation & Educational Guidance", h2_style))
    remediation_text = """
    Based on your assessment evaluation, review the following security guidelines:<br/>
    • <b>Password Security:</b> Always use passphrase combinations of at least 14+ characters and multi-factor authentication (MFA).<br/>
    • <b>Phishing Awareness:</b> Inspect sender email headers, verify URLs before clicking, and report suspicious messages.<br/>
    • <b>Data Protection:</b> Ensure sensitive files are encrypted at rest and in transit.
    """
    story.append(Paragraph(remediation_text, body_style))
    story.append(Spacer(1, 20))

    # Disclaimer Footer
    disclaimer = "<i>Note: This assessment level is a training indicator for cybersecurity awareness and does not replace organizational risk modeling.</i>"
    story.append(Paragraph(disclaimer, ParagraphStyle('Disc', parent=styles['Italic'], fontSize=8, textColor=colors.HexColor('#64748B'))))

    doc.build(story)
    return filepath
