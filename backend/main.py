from flask import Flask, render_template, request, redirect, url_for, session
import os
from backend.models import db, Designer, Founder, Match
from backend.matching import find_single_best_match, find_matches_for_founder
from backend.credits import has_credits, deduct_credit
from backend.email_utils import send_confirmation_email, send_match_email, send_rematch_email

# Get the project root directory (parent of backend)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(project_root, 'templates')
static_dir = os.path.join(project_root, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///creativeplay.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# -------------------------------------------------
# Home Page
# -------------------------------------------------
@app.route('/')
def home():
    return render_template('home.html')


# -------------------------------------------------
# Form Pages
# -------------------------------------------------
@app.route('/founder')
def founder_form():
    return render_template('founder_form.html')


@app.route('/designer')
def designer_form():
    return render_template('designer_form.html')


# -------------------------------------------------
# Submit Founder
# -------------------------------------------------
@app.route('/submit_founder', methods=['POST'])
def submit_founder():
    name = request.form.get('name')
    email = request.form.get('email')
    project = request.form.get('project')
    needs = request.form.get('needs')

    if not all([name, email, project, needs]):
        return redirect(url_for('founder_form'))

    # Create founder
    founder = Founder(name=name, email=email, project=project, needs=needs)
    db.session.add(founder)
    db.session.commit()

    # Send confirmation email
    send_confirmation_email(email, 'founder')

    # Find match
    matched_designer = find_single_best_match(founder)

    if matched_designer:
        # Create match record
        match = Match(founder_id=founder.id, designer_id=matched_designer.id, status='pending')
        db.session.add(match)
        db.session.commit()

        # Send match emails
        send_match_email(founder.email, matched_designer)
        send_match_email(matched_designer.email, founder)

        # Store match info in session for display
        session['match_founder_id'] = founder.id
        session['match_designer_id'] = matched_designer.id

        return redirect(url_for('match_success', role='Designer'))
    else:
        return render_template('no_match.html')


# -------------------------------------------------
# Submit Designer
# -------------------------------------------------
@app.route('/submit_designer', methods=['POST'])
def submit_designer():
    name = request.form.get('name')
    email = request.form.get('email')
    skills = request.form.get('skills')
    experience = request.form.get('experience', '')

    if not all([name, email, skills]):
        return redirect(url_for('designer_form'))

    # Check if designer already exists
    existing = Designer.query.filter_by(email=email).first()
    if existing:
        # Update existing designer
        existing.name = name
        existing.skills = skills
        existing.experience = experience
        db.session.commit()
        designer = existing
    else:
        # Create new designer
        designer = Designer(name=name, email=email, skills=skills, experience=experience)
        db.session.add(designer)
        db.session.commit()

    # Send confirmation email
    send_confirmation_email(email, 'designer')

    return render_template('confirmation.html')


# -------------------------------------------------
# Match Success Page
# -------------------------------------------------
@app.route('/match_success')
def match_success():
    role = request.args.get('role', 'Designer')
    
    # Get match info from session or latest match
    founder_id = session.get('match_founder_id')
    designer_id = session.get('match_designer_id')
    
    if founder_id and designer_id:
        if role.lower() == 'designer':
            matched_person = Designer.query.get(designer_id)
        else:
            matched_person = Founder.query.get(founder_id)
    else:
        # Fallback: get latest match
        latest_match = Match.query.order_by(Match.created_at.desc()).first()
        if latest_match:
            if role.lower() == 'designer':
                matched_person = latest_match.designer
            else:
                matched_person = latest_match.founder
        else:
            return redirect(url_for('home'))
    
    if not matched_person:
        return redirect(url_for('home'))
    
    # Set avatar and colors based on role
    if role.lower() == 'designer':
        avatar = 'designer.png'
        bg_color = '#E7F4FF'
    else:
        avatar = 'founder.png'
        bg_color = '#FBF1D6'
    
    return render_template('match_success.html', 
                         role=role,
                         avatar=avatar,
                         bg_color=bg_color)


# -------------------------------------------------
# Rematch Route
# -------------------------------------------------
@app.route('/rematch/<role>')
def rematch(role):
    # Get the latest founder from session or request
    founder_id = session.get('match_founder_id')
    
    if not founder_id:
        # Try to get from latest match
        latest_match = Match.query.order_by(Match.created_at.desc()).first()
        if latest_match:
            founder_id = latest_match.founder_id
        else:
            return redirect(url_for('home'))
    
    founder = Founder.query.get(founder_id)
    if not founder:
        return redirect(url_for('home'))
    
    # For designer rematch, check credits
    if role.lower() in ['designer', 'designers']:
        # Get designer ID from session or latest match
        designer_id = session.get('match_designer_id')
        if not designer_id:
            latest_match = Match.query.filter_by(founder_id=founder_id).order_by(Match.created_at.desc()).first()
            if latest_match:
                designer_id = latest_match.designer_id
        
        if designer_id and not has_credits(designer_id):
            return render_template('out_of_credits.html')
        
        if designer_id:
            deduct_credit(designer_id)
    
    # Find new matches
    new_matches = find_matches_for_founder(founder, limit=3)
    
    if not new_matches:
        return render_template('no_match.html')
    
    # Create match records for new matches
    for designer in new_matches:
        # Check if match already exists
        existing = Match.query.filter_by(
            founder_id=founder.id,
            designer_id=designer.id
        ).first()
        
        if not existing:
            match = Match(founder_id=founder.id, designer_id=designer.id, status='pending')
            db.session.add(match)
    
    db.session.commit()
    
    # Send rematch email
    send_rematch_email(founder.email, new_matches)
    
    # Display first match
    matched_designer = new_matches[0]
    session['match_founder_id'] = founder.id
    session['match_designer_id'] = matched_designer.id
    
    avatar = 'designer.png'
    bg_color = '#E7F4FF'
    
    return render_template('rematch_success.html',
                         role='Designer',
                         avatar=avatar,
                         bg_color=bg_color)


# -------------------------------------------------
# Admin Route (View All Matches)
# -------------------------------------------------
@app.route('/admin')
def admin_matches():
    matches = Match.query.order_by(Match.created_at.desc()).all()
    return render_template('matches_admin.html', matches=matches)


if __name__ == '__main__':
    app.run(debug=True)
