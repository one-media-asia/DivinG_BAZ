from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diving_admin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ============ Models ============

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # admin, instructor, user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    divers = db.relationship('Diver', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

class Diver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    certification_level = db.Column(db.String(50))  # Open Water, Advanced, etc.
    certification_number = db.Column(db.String(100))
    certification_date = db.Column(db.Date)
    experience_dives = db.Column(db.Integer, default=0)
    phone = db.Column(db.String(20))
    emergency_contact = db.Column(db.String(120))
    medical_conditions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    dives = db.relationship('Dive', secondary='dive_diver', backref=db.backref('divers', lazy=True))
    equipment = db.relationship('Equipment', backref='owner', lazy=True)

class DiveSite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    location = db.Column(db.String(200), nullable=False)
    depth_min = db.Column(db.Float)
    depth_max = db.Column(db.Float)
    description = db.Column(db.Text)
    difficulty_level = db.Column(db.String(20))  # Beginner, Intermediate, Advanced
    water_temperature = db.Column(db.Float)
    visibility = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    dives = db.relationship('Dive', backref='site', lazy=True)

class Dive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('dive_site.id'), nullable=False)
    dive_date = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer)
    max_depth = db.Column(db.Float)
    air_used = db.Column(db.Float)  # PSI or Bar
    conditions = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    dive_diver = db.relationship('Diver', secondary='dive_diver')

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    diver_id = db.Column(db.Integer, db.ForeignKey('diver.id'), nullable=False)
    equipment_type = db.Column(db.String(50), nullable=False)  # BCD, Tank, Regulator, etc.
    brand = db.Column(db.String(80))
    model = db.Column(db.String(80))
    serial_number = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    last_maintenance = db.Column(db.Date)
    next_maintenance = db.Column(db.Date)
    condition = db.Column(db.String(20))  # Good, Fair, Needs Repair
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Certification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    diver_id = db.Column(db.Integer, db.ForeignKey('diver.id'), nullable=False)
    cert_type = db.Column(db.String(100), nullable=False)
    agency = db.Column(db.String(100))
    date_issued = db.Column(db.Date, nullable=False)
    expiration_date = db.Column(db.Date)
    cert_number = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Association table for many-to-many relationship
dive_diver = db.Table('dive_diver',
    db.Column('dive_id', db.Integer, db.ForeignKey('dive.id'), primary_key=True),
    db.Column('diver_id', db.Integer, db.ForeignKey('diver.id'), primary_key=True)
)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

# ============ Routes ============

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        return jsonify({'error': 'Invalid credentials'}), 401
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    diver_count = Diver.query.filter_by(user_id=current_user.id).count()
    dive_count = db.session.query(Dive).join(dive_diver).join(Diver).filter(Diver.user_id == current_user.id).count()
    equipment_count = db.session.query(Equipment).join(Diver).filter(Diver.user_id == current_user.id).count()
    
    return render_template('dashboard.html', 
                         diver_count=diver_count,
                         dive_count=dive_count,
                         equipment_count=equipment_count)

# ============ Diver Routes ============

@app.route('/divers', methods=['GET', 'POST'])
@login_required
def divers():
    if request.method == 'POST':
        diver = Diver(
            user_id=current_user.id,
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            certification_level=request.form.get('certification_level'),
            certification_number=request.form.get('certification_number'),
            phone=request.form.get('phone'),
            emergency_contact=request.form.get('emergency_contact'),
            medical_conditions=request.form.get('medical_conditions')
        )
        db.session.add(diver)
        db.session.commit()
        return redirect(url_for('divers'))
    
    user_divers = Diver.query.filter_by(user_id=current_user.id).all()
    return render_template('divers.html', divers=user_divers)

@app.route('/diver/<int:diver_id>')
@login_required
def diver_detail(diver_id):
    diver = Diver.query.get_or_404(diver_id)
    if diver.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    equipment = Equipment.query.filter_by(diver_id=diver_id).all()
    return render_template('diver_detail.html', diver=diver, equipment=equipment)

@app.route('/diver/<int:diver_id>/edit', methods=['POST'])
@login_required
def edit_diver(diver_id):
    diver = Diver.query.get_or_404(diver_id)
    if diver.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    diver.first_name = request.form.get('first_name', diver.first_name)
    diver.last_name = request.form.get('last_name', diver.last_name)
    diver.certification_level = request.form.get('certification_level', diver.certification_level)
    diver.experience_dives = request.form.get('experience_dives', diver.experience_dives, type=int)
    diver.phone = request.form.get('phone', diver.phone)
    diver.emergency_contact = request.form.get('emergency_contact', diver.emergency_contact)
    
    db.session.commit()
    return redirect(url_for('diver_detail', diver_id=diver_id))

@app.route('/diver/<int:diver_id>/delete', methods=['POST'])
@login_required
def delete_diver(diver_id):
    diver = Diver.query.get_or_404(diver_id)
    if diver.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(diver)
    db.session.commit()
    return redirect(url_for('divers'))

# ============ Equipment Routes ============

@app.route('/equipment', methods=['GET', 'POST'])
@login_required
def equipment():
    if request.method == 'POST':
        diver_id = request.form.get('diver_id', type=int)
        diver = Diver.query.get_or_404(diver_id)
        if diver.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        eq = Equipment(
            diver_id=diver_id,
            equipment_type=request.form.get('equipment_type'),
            brand=request.form.get('brand'),
            model=request.form.get('model'),
            serial_number=request.form.get('serial_number'),
            condition=request.form.get('condition', 'Good')
        )
        db.session.add(eq)
        db.session.commit()
        return redirect(url_for('equipment'))
    
    user_equipment = db.session.query(Equipment).join(Diver).filter(Diver.user_id == current_user.id).all()
    user_divers = Diver.query.filter_by(user_id=current_user.id).all()
    return render_template('equipment.html', equipment=user_equipment, divers=user_divers)

@app.route('/equipment/<int:eq_id>/delete', methods=['POST'])
@login_required
def delete_equipment(eq_id):
    eq = Equipment.query.get_or_404(eq_id)
    diver = Diver.query.get(eq.diver_id)
    if diver.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(eq)
    db.session.commit()
    return redirect(url_for('equipment'))

# ============ Dive Sites Routes ============

@app.route('/dive-sites', methods=['GET', 'POST'])
@login_required
def dive_sites():
    if request.method == 'POST' and current_user.role == 'admin':
        site = DiveSite(
            name=request.form.get('name'),
            location=request.form.get('location'),
            depth_min=request.form.get('depth_min', type=float),
            depth_max=request.form.get('depth_max', type=float),
            description=request.form.get('description'),
            difficulty_level=request.form.get('difficulty_level'),
            water_temperature=request.form.get('water_temperature', type=float)
        )
        db.session.add(site)
        db.session.commit()
        return redirect(url_for('dive_sites'))
    
    sites = DiveSite.query.all()
    return render_template('dive_sites.html', sites=sites)

# ============ Dives Routes ============

@app.route('/dives', methods=['GET', 'POST'])
@login_required
def dives():
    if request.method == 'POST':
        dive = Dive(
            site_id=request.form.get('site_id', type=int),
            dive_date=datetime.fromisoformat(request.form.get('dive_date')), # pyright: ignore[reportArgumentType]
            duration_minutes=request.form.get('duration_minutes', type=int),
            max_depth=request.form.get('max_depth', type=float),
            air_used=request.form.get('air_used', type=float),
            conditions=request.form.get('conditions'),
            notes=request.form.get('notes')
        )
        db.session.add(dive)
        db.session.flush()
        
        diver_ids = request.form.getlist('diver_ids')
        for diver_id in diver_ids:
            diver = Diver.query.get(diver_id)
            if diver.user_id == current_user.id:
                dive.divers.append(diver)
        
        db.session.commit()
        return redirect(url_for('dives'))
    
    user_divers = Diver.query.filter_by(user_id=current_user.id).all()
    sites = DiveSite.query.all()
    user_dives = db.session.query(Dive).join(dive_diver).join(Diver).filter(Diver.user_id == current_user.id).all()
    
    return render_template('dives.html', dives=user_dives, divers=user_divers, sites=sites)

@app.route('/dive/<int:dive_id>')
@login_required
def dive_detail(dive_id):
    dive = Dive.query.get_or_404(dive_id)
    if not any(d.user_id == current_user.id for d in dive.divers):
        return jsonify({'error': 'Unauthorized'}), 403
    return render_template('dive_detail.html', dive=dive)

# ============ Certification Routes ============

@app.route('/certifications', methods=['GET', 'POST'])
@login_required
def certifications():
    if request.method == 'POST':
        diver_id = request.form.get('diver_id', type=int)
        diver = Diver.query.get_or_404(diver_id)
        if diver.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        cert = Certification(
            diver_id=diver_id,
            cert_type=request.form.get('cert_type'),
            agency=request.form.get('agency'),
            date_issued=datetime.strptime(request.form.get('date_issued'), '%Y-%m-%d').date(),
            cert_number=request.form.get('cert_number')
        )
        
        expiration_date = request.form.get('expiration_date')
        if expiration_date:
            cert.expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d').date()
        
        db.session.add(cert)
        db.session.commit()
        return redirect(url_for('certifications'))
    
    user_divers = Diver.query.filter_by(user_id=current_user.id).all()
    user_certifications = db.session.query(Certification).join(Diver).filter(Diver.user_id == current_user.id).all()
    
    return render_template('certifications.html', 
                         divers=user_divers, 
                         certifications=user_certifications,
                         now=datetime.utcnow().date())

@app.route('/certification/<int:cert_id>/delete', methods=['POST'])
@login_required
def delete_certification(cert_id):
    cert = Certification.query.get_or_404(cert_id)
    diver = Diver.query.get(cert.diver_id)
    if diver.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(cert)
    db.session.commit()
    return redirect(url_for('certifications'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
