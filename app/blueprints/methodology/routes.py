from flask import Blueprint, render_template
from flask_login import login_required

methodology_bp = Blueprint('methodology', __name__, url_prefix='/methodology')

@methodology_bp.route('/assessment')
def assessment_methodology():
    """Renders academic explanation of the security awareness assessment workflow."""
    return render_template('methodology/assessment_methodology.html')


@methodology_bp.route('/lab')
def lab_methodology():
    """Renders academic explanation of the cybersecurity technical lab methodology."""
    return render_template('methodology/lab_methodology.html')
