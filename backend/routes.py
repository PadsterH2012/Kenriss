from flask import jsonify, session, render_template, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from app import app, db

@app.route('/register', methods=['POST'])
def register():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Missing username, email, or password'}), 400
    
    username = data['username']
    email = data['email']
    password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully!'})

@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user and check_password_hash(user.password, data['password']):
        session['user_id'] = user.id
        return jsonify({'message': 'Login successful!', 'redirect': url_for('dashboard')})
    
    return jsonify({'message': 'Invalid credentials!'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully!'})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', username=user.username)

@app.route('/user_settings', methods=['GET', 'POST'])
def user_settings():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        data = request.form
        if 'username' in data and 'email' in data and 'currentPassword' in data:
            if check_password_hash(user.password, data['currentPassword']):
                user.username = data['username']
                user.email = data['email']
                db.session.commit()
                return jsonify({'message': 'Profile updated successfully!'})
            else:
                return jsonify({'message': 'Current password is incorrect'}), 400
        else:
            return jsonify({'message': 'Missing required fields'}), 400
    
    return render_template('user_settings.html', username=user.username, email=user.email)

@app.route('/app_settings', methods=['GET', 'POST'])
def app_settings():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
    
    if request.method == 'POST':
        theme = request.form.get('theme')
        session['theme'] = theme
        return jsonify({'message': 'Settings updated successfully!'})
    
    current_theme = session.get('theme', 'light')
    return render_template('app_settings.html', current_theme=current_theme)
