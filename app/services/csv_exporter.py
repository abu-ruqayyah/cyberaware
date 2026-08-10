import csv
import io
from app.models.quiz import QuizAttempt

def export_quiz_attempts_csv():
    """Generate CSV spreadsheet string of all completed quiz attempts."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Write Header
    writer.writerow([
        'Attempt ID',
        'Staff Username',
        'Staff Full Name',
        'Department',
        'Date Completed',
        'Total Questions',
        'Correct Answers',
        'Percentage Score',
        'Assessment Level',
        'Time Spent (seconds)'
    ])

    attempts = QuizAttempt.query.order_by(QuizAttempt.completed_at.desc()).all()
    for att in attempts:
        user = att.user
        writer.writerow([
            att.id,
            user.username if user else 'Deleted',
            user.full_name if user else 'Deleted',
            user.department if user else 'General',
            att.completed_at.strftime('%Y-%m-%d %H:%M:%S') if att.completed_at else 'In Progress',
            att.total_questions,
            att.score_achieved,
            f"{att.percentage_score}%",
            att.assessment_level or 'N/A',
            att.time_spent_seconds
        ])

    return output.getvalue()
