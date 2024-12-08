from flask import render_template, request, url_for, redirect, flash, session
from config import app, db
from models import User

app.secret_key = 'your_secret_key_here'  # Change this to a secure random key

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['logged_in'] = True
            session['user_id'] = user.id
            flash("You cool, mf")
            return render_template('main_page.html')

        else:
            #flash("Invalid username or password")
            flash("Man, FUCK you.")
            return redirect(url_for('index'))

    return redirect(url_for('index'))

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("This username is already taken bro. ")
            return redirect(url_for('create_account'))

        # Create a new user and set hashed password
        new_user = User(username=username, email=email, password=None)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Account created")
        return redirect(url_for('login'))

    return render_template('login.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)