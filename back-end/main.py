from flask import render_template, request, url_for, redirect, flash, session
from config import app, db
from models import User, Topic, Posts

app.secret_key = 'your_secret_key_here'  # Change this to a secure random key

# @app.route('/')
# def index():
#     return render_template('login.html')
#
# # @app.route('/main_page')
# # def main_page():
# #     all_topics = Topic.query.all()
# #     # for now, this will just get all of the posts in the db, however, I want to change it later so that it only gets posts
# #     # relevant to the user (following or similar topics, etc)
# #     relevant_posts = Posts.get.all()
# #     return render_template('main_page.html', all_topics=all_topics, posts=relevant_posts)
#
# @app.route('/main_page')
# def main_page():
#     all_topics = Topic.query.all()
#
#     # This will get all posts in the database for now
#     relevant_posts = Posts.query.all()  # This should be Posts.query.all(), not Posts.get.all()
#
#     return render_template('main_page.html', all_topics=all_topics, posts=relevant_posts)
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#
#         user = User.query.filter_by(username=username).first()
#         if user and user.check_password(password):
#             session['logged_in'] = True
#             session['user_id'] = user.id
#             # this is going to be returning all topics so that they can be shown on the main hub page
#             all_topics = Topic.query.all()
#             relevant_posts = Posts.query.all()
#             flash("You cool, mf")
#             return render_template('main_page.html', all_topics=all_topics, user_id=user.id, username=user.username, posts=relevant_posts)
#
#         else:
#             #flash("Invalid username or password")
#             flash("Man, FUCK you.")
#             return redirect(url_for('index'))
#
#     return redirect(url_for('index'))
#
# @app.route('/create_account', methods=['GET', 'POST'])
# def create_account():
#     if request.method == 'POST':
#         real_name = request.form.get('real_name')
#         username = request.form.get('username')
#         email = request.form.get('email')
#         password = request.form.get('password')
#
#         # Check if username already exists
#         existing_user = User.query.filter_by(username=username).first()
#         if existing_user:
#             flash("This username is already taken.")
#             return redirect(url_for('create_account'))
#
#         # Validate that password is not empty or None
#         if not password:
#             flash("Password cannot be empty.")
#             return redirect(url_for('create_account'))
#
#         # Create a new user with a valid password
#         new_user = User(real_name=real_name, username=username, email=email, password=password)  # Pass password directly here
#         db.session.add(new_user)
#         db.session.commit()
#
#         flash("Account created")
#         return redirect(url_for('login'))
#
#     return render_template('login.html')
#
# @app.route('/create_post', methods=['GET', 'POST'])
# def create_post():
#     if request.method == 'POST':
#         user_id = session.get('user_id')
#         topic_name = request.form.get('post_topic')
#         post_title = request.form.get('post_title')
#         content = request.form.get('post_content')
#
#         # Check if the topic already exists
#         existing_topic = Topic.query.filter_by(name=topic_name).first()
#
#         # If the topic doesn't exist, create it
#         if not existing_topic:
#             new_topic = Topic(name=topic_name, description=f"See what people are saying about {topic_name}!")
#             db.session.add(new_topic)
#             db.session.commit()  # Commit to get the new topic's ID
#
#             topic_id = new_topic.id  # Use the newly created topic's ID
#         else:
#             topic_id = existing_topic.id  # Use the existing topic's ID
#
#         # Create a new post with the appropriate topic_id
#         new_post = Posts(poster_id=user_id, topic_id=topic_id, title=post_title, content=content)
#         db.session.add(new_post)
#         db.session.commit()
#
#         # Redirect or return a response, such as:
#         return redirect(url_for('main_page'))  # Replace 'some_view' with the desired view after posting
#
#     # If it's a GET request, return the form to create a post
#     return render_template('main_page.html')

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/main_page')
def main_page():
    # Ensure the user is logged in, and retrieve the username from session
    if 'logged_in' in session:
        user_id = session['user_id']
        username = session.get('username')  # Retrieve the username from session

        all_topics = Topic.query.all()
        relevant_posts = Posts.query.all()

        return render_template('main_page.html', all_topics=all_topics, posts=relevant_posts, username=username)
    else:
        flash("You need to log in first.")
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['logged_in'] = True
            session['user_id'] = user.id
            session['username'] = user.username  # Store username in the session

            all_topics = Topic.query.all()
            relevant_posts = Posts.query.all()

            flash("You cool, mf")
            return render_template('main_page.html', all_topics=all_topics, user_id=user.id, username=user.username, posts=relevant_posts)
        else:
            flash("Invalid username or password")
            return redirect(url_for('index'))

    return redirect(url_for('index'))

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        real_name = request.form.get('real_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("This username is already taken.")
            return redirect(url_for('create_account'))

        # Validate that password is not empty or None
        if not password:
            flash("Password cannot be empty.")
            return redirect(url_for('create_account'))

        # Create a new user with a valid password
        new_user = User(real_name=real_name, username=username, email=email, password=password)  # Pass password directly here
        db.session.add(new_user)
        db.session.commit()

        flash("Account created")
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        user_id = session.get('user_id')  # Get user_id from session
        user = User.query.filter_by(id=user_id).first()
        topic_name = request.form.get('post_topic')
        post_title = request.form.get('post_title')
        content = request.form.get('post_content')

        # Check if the topic already exists
        existing_topic = Topic.query.filter_by(name=topic_name).first()

        # If the topic doesn't exist, create it
        if not existing_topic:
            new_topic = Topic(name=topic_name, description=f"See what people are saying about {topic_name}!")
            db.session.add(new_topic)
            db.session.commit()  # Commit to get the new topic's ID

            topic_id = new_topic.id  # Use the newly created topic's ID
        else:
            topic_id = existing_topic.id  # Use the existing topic's ID

        # Create a new post with the appropriate topic_id
        new_post = Posts(poster_id=user_id, poster_username = user.username, topic_id=topic_id, title=post_title, content=content)
        db.session.add(new_post)
        db.session.commit()

        # Redirect or return a response, such as:
        return redirect(url_for('main_page'))  # Replace 'some_view' with the desired view after posting

    # If it's a GET request, return the form to create a post
    return render_template('main_page.html')



if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)