from flask import Flask, render_template, redirect, url_for, flash, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
from flask_login import LoginManager, UserMixin, login_user, logout_user
from key_gen import generate_key
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
from urllib.parse import unquote

app = Flask(__name__)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

SECRET_KEY = os.urandom(32)
SECRET_KEY_2 = os.urandom(32)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)

# Set up the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = SECRET_KEY_2  # Change this to a strong secret key
jwt = JWTManager(app)


# required or server sends a 500 error
@login_manager.user_loader
def load_user(user_id):
    # Return the user object for the given user_id
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template("index.html")


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    api_key = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    api_key = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        key = generate_key()
        user = User(username=form.username.data, email=form.email.data,
                    password=generate_password_hash(form.password.data),
                    api_key=key)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))  # Replace 'login' with your login route
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            # compares the passwords and logins the user if successful
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Login Successful")
                return redirect(url_for('index'))
            else:
                flash("Wrong Password - Please Try Again.")
        else:
            flash("That User Does Not Exist - Please Try Again Or Register New Account")

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("Logout Successful")
    return redirect(url_for('login'))


@app.route('/api_key')
def get_api_key():
    return render_template('api_key.html')


# Auth for API
@app.route("/authenticate", methods=["POST"])
def authenticate():
    api_key = request.json.get("api_key", None)

    key = User.query.filter_by(api_key=api_key).first()

    if key:
        access_token = create_access_token(identity=api_key)
        return jsonify(access_token=access_token)
    else:
        return jsonify({"msg": "Bad username or password"}), 401


@app.route("/documentation/movies")
def movies_doc():
    return render_template("movies_doc.html")


@app.route("/documentation/authentication")
def auth_doc():
    return render_template("authentication_doc.html")


@app.route("/documentation/actors")
def actors_doc():
    return render_template("actors_doc.html")


@app.route("/movies/<movie_name>")
@jwt_required()
def get_movie(movie_name):
    movie = unquote(movie_name)
    conn = sqlite3.connect('instance/users.db')
    cursor = conn.cursor()
    query = f'''
    SELECT * FROM Movies WHERE names LIKE "{movie}"'''
    cursor.execute(query)
    results = cursor.fetchall()
    data = {
        "cast-crew": results[0][5],
        "description": results[0][4],
        "genre": results[0][3],
        "rating": results[0][2],
        "release-date": results[0][1],
        "title": results[0][0]
    }
    conn.close()
    return jsonify(data)


@app.route("/actors/<actor_name>")
@jwt_required()
def get_actor(actor_name):
    actor = unquote(actor_name)
    conn = sqlite3.connect('instance/users.db')
    cursor = conn.cursor()
    query = f'''
    SELECT *
      FROM Movies  
     WHERE instr(crew, '{actor}') > 0;'''
    cursor.execute(query)
    results = cursor.fetchall()
    list1 = []
    for result in results:
        data = {
            "cast-crew": result[5],
            "description": result[4],
            "genre": result[3],
            "rating": result[2],
            "release-date": result[1],
            "title": result[0]
        }
        list1.append(data)
    return jsonify(list1)


# will create the database if it does not exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
