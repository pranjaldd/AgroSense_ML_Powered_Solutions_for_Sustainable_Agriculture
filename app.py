from flask import Flask, render_template, request, redirect, session, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from weed import weed_bp
from plantdisease import plant_disease_bp as plant_bp
from water import cropwater_bp  # Import the cropwater blueprint
import pdfkit

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

# Create DB
with app.app_context():
    db.create_all()

# Register blueprints
app.register_blueprint(weed_bp)
app.register_blueprint(plant_bp)
app.register_blueprint(cropwater_bp)  # Register the cropwater blueprint

# Routes
@app.route('/')
def intro_page():
    return render_template('intro_index.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['email'] = user.email
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid email or password. Please try again or register.")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('register.html', error="Email already registered. Please login.")

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('dashboard.html', user=user)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

# Start server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
