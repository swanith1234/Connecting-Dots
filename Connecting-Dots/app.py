from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite for simplicity, change this in production
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    domain = db.Column(db.String(50), nullable=False)
    subdomain = db.Column(db.String(50), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            return redirect(url_for('userdashboard'))
        else:
            return 'Login failed. Check your username and password.'
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        domain = request.form['domain']
        subdomain = request.form['subdomain']

        new_user = User(username=username, password=password, email=email, domain=domain, subdomain=subdomain)

        try:
            with app.app_context():
                db.session.add(new_user)
                db.session.commit()
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            return 'Username or email already exists. Please choose a different one.'

    return render_template('signup.html')

@app.route('/userdashboard', methods=['GET', 'POST'])
def userdashboard():
    domains = ['Web app', 'Android app', 'Machine Learning']
    subdomains = {
        'Web app': ['HTML', 'CSS', 'JS', 'ANGULAR', 'REACT', 'NODE JS', 'NEXT JS', 'DJANGO', 'DATABASES', 'UX/UI'],
        'Android app': ['FLUTTER', 'REACT NATIVE', 'C++', 'KOTLIN', 'JAVA'],
        'Machine Learning': ['Tensor flow', 'Scikit Learn', 'Seaborn']
    }

    search_domain = request.form.get('search_domain', None)
    search_subdomain = request.form.get('search_subdomain', None)

    try:
        if search_domain and search_subdomain:
            users = User.query.filter_by(domain=search_domain, subdomain=search_subdomain).all()
        elif search_domain:
            users = User.query.filter_by(domain=search_domain).all()
        elif search_subdomain:
            users = User.query.filter_by(subdomain=search_subdomain).all()
        else:
            users = User.query.all()

        return render_template('userdashboard.html', users=users, domains=domains, subdomains=subdomains,
                               search_domain=search_domain, search_subdomain=search_subdomain)

    except SQLAlchemyError as e:
        # Log the error or handle it appropriately
        print(f"Error querying the database: {e}")

    return render_template('userdashboard.html', domains=domains, subdomains=subdomains)

if __name__ == '__main__':
    app.run(debug=True)
