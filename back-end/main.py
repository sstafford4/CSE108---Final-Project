from flask import render_template, request, url_for, redirect, flash, session, Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
# from config import app, db
# from models import User, Topic, Posts
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

# SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
#     username="sstafford4",
#     password="Simperia1",
#     hostname="sstafford4.mysql.pythonanywhere-services.com",
#     databasename="sstafford4$default",
# )
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:12263899@localhost/final_project'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Association table for Users following Topics
user_topic = db.Table(
    'user_topic',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('topic_id', db.Integer, db.ForeignKey('topic.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    real_name = db.Column(db.String(64), index=True, unique=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

    # Relationship to the posts created by the user
    posts = db.relationship('Posts', backref='poster', lazy='dynamic')

    # Many-to-many relationship for followed topics
    followed_topics = db.relationship('Topic', secondary=user_topic, backref=db.backref('followers', lazy='dynamic'))

    def __init__(self, real_name, username, email, password):
        self.real_name = real_name
        self.username = username
        self.email = email
        self.set_password(password)  # Pass the password here to ensure it's set correctly

    def set_password(self, password):
        if password:  # Make sure the password is not empty or None
            self.password = generate_password_hash(password)
        else:
            raise ValueError("Password cannot be empty.")  # Optional: Add custom validation

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_json(self):
        return {
            'realName': self.real_name,
            'username': self.username,
            'email': self.email
        }

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)

    # Relationship to the posts in this topic
    posts = db.relationship('Posts', backref='topic', lazy='dynamic')

    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'post_count': self.posts.count(),
            'followers_count': self.followers.count()
        }

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poster_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    poster_username = db.Column(db.String(100), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), index=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self, poster_id, poster_username, topic_id, title, content):
        self.poster_id = poster_id
        self.poster_username = poster_username
        self.topic_id = topic_id
        self.title = title
        self.content = content

    def to_json(self):
        return {
            'id': self.id,
            'poster_id': self.poster_id,
            'poster_username': self.poster_username,
            'topic_id': self.topic_id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationships
    user = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    post = db.relationship('Posts', backref=db.backref('comments', lazy='dynamic'))

    def __init__(self, post_id, user_id, content):
        self.post_id = post_id
        self.user_id = user_id
        self.content = content

    def to_json(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }


app.secret_key = 'your_secret_key_here'  # Change this to a secure random key


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear the session data (e.g., remove user info or other session variables)
    session.clear()
    flash('Logged out successfully')

    # Redirect to the login page
    return redirect(url_for('login'))  # Assuming 'login' is the name of the login route

@app.route('/main_page')
def main_page():
    # Ensure the user is logged in, and retrieve the username from session
    if 'logged_in' in session:
        user_id = session['user_id']
        username = session.get('username')  # Retrieve the username from session

        # Get the user object from the database
        user = User.query.get(user_id)

        # Get the topics the user is following
        followed_topics = user.followed_topics
        all_topics = Topic.query.all()

        # Get the posts for the topics the user is following
        # relevant_posts = Posts.query.filter(Posts.topic_id.in_([topic.id for topic in followed_topics])).all()
        relevant_posts = Posts.query.filter(
            Posts.topic_id.in_([topic.id for topic in followed_topics])
        ).order_by(Posts.created_at.desc()).all()
        # Get a list of topic IDs that the user is following
        followed_topic_ids = [topic.id for topic in followed_topics]

        return render_template('main_page.html',
                               all_topics=all_topics,
                               followed_topic_ids=followed_topic_ids,
                               posts=relevant_posts,
                               username=username)
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

@app.route('/follow_topic/<int:topic_id>', methods=['GET'])
def follow_topic(topic_id):
    # Ensure the user is logged in, using the session
    if 'logged_in' in session:
        user_id = session['user_id']

        # Find the user and the topic they want to follow
        user = User.query.filter_by(id=user_id).first()
        topic = Topic.query.filter_by(id=topic_id).first()

        if not topic:
            flash("Topic not found.")
            return redirect(url_for('main_page'))

        # Check if the user is already following the topic
        if topic in user.followed_topics:
            flash("You are already following this topic.")
        else:
            # Add the topic to the user's followed topics
            user.followed_topics.append(topic)
            db.session.commit()
            flash(f"You are now following the topic: {topic.name}")

        return redirect(url_for('main_page'))  # Redirect back to the main page

    else:
        flash("You need to log in first.")
        return redirect(url_for('login'))

@app.route('/unfollow_topic/<int:topic_id>', methods=['GET'])
def unfollow_topic(topic_id):
    # Ensure the user is logged in, using the session
    if 'logged_in' in session:
        user_id = session['user_id']

        # Find the user and the topic they want to unfollow
        user = User.query.filter_by(id=user_id).first()
        topic = Topic.query.filter_by(id=topic_id).first()

        if not topic:
            flash("Topic not found.")
            return redirect(url_for('main_page'))

        # Check if the user is following the topic
        if topic in user.followed_topics:
            # Remove the topic from the user's followed topics
            user.followed_topics.remove(topic)
            db.session.commit()
            flash(f"You have unfollowed the topic: {topic.name}")
        else:
            flash("You are not following this topic.")

        return redirect(url_for('main_page'))  # Redirect back to the main page

    else:
        flash("You need to log in first.")
        return redirect(url_for('login'))

@app.route('/search_posts', methods=['GET'])
def search_posts():
    user_id = session.get('user_id')
    username = session.get('username')
    query = request.args.get('query', '').strip()  # Get the search query from the URL parameters

    if not query:
        flash("Please enter a search query.")
        return redirect(url_for('main_page'))

    # Perform the search: find posts by topic name or user username
    posts_by_topic = Posts.query.join(Topic).filter(Topic.name.ilike(f"%{query}%")).all()
    posts_by_user = Posts.query.join(User).filter(User.username.ilike(f"%{query}%")).all()
    posts_by_title = Posts.query.filter(Posts.title.ilike(f"%{query}%")).all()

    #   Get the user object from the database
    user = User.query.get(user_id)

    # Get the topics the user is following
    followed_topics = user.followed_topics
    all_topics = Topic.query.all()

    # Get the posts for the topics the user is following
    relevant_posts = Posts.query.filter(
        Posts.topic_id.in_([topic.id for topic in followed_topics])
    ).order_by(Posts.created_at.desc()).all()

    # Get a list of topic IDs that the user is following
    followed_topic_ids = [topic.id for topic in followed_topics]

    # Combine results and remove duplicates
    search_results = list({post.id: post for post in posts_by_topic + posts_by_user + posts_by_title}.values())

    # Render the main page with the new search results
    return render_template('main_page.html', search_results=search_results, query=query, all_topics=all_topics,
                                   followed_topic_ids=followed_topic_ids,
                                   posts=relevant_posts,
                                   username=username)


@app.route('/submit_comment', methods=['POST'])
def submit_comment():
    user_id = session.get('user_id')
    username = session.get('username')

    # Get data from form
    post_id = request.form.get('post_id')
    content = request.form.get('content')

    # Ensure user is logged in
    if not user_id:
        flash("You must be logged in to submit a comment.")
        return redirect(url_for('login'))

    user = User.query.get(user_id)

    # Validate required fields
    if not post_id or not content.strip():
        flash("Comment content cannot be empty.")
        return redirect(url_for('view_post', post_id=post_id))

    # Create a new comment instance
    comment = Comments(post_id=post_id, user_id=user_id, content=content)
    try:
        db.session.add(comment)
        db.session.commit()
        flash("Comment submitted successfully!")

        # Redirect back to the post page to reload with the new comment
        return redirect(url_for('view_post', post_id=post_id))

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {str(e)}")
        return redirect(url_for('view_post', post_id=post_id))


@app.route('/view_post/<int:post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    user_id = session.get('user_id')
    username = session.get('username')

    # Get the post by ID (single post)
    post = Posts.query.get(post_id)

    if post is None:
        # Handle the case where the post does not exist
        return "Post not found", 404

    # Prepare post_info as a dictionary for the template
    post_info = {
        "id": post.id,
        "poster_id": post.poster_id,
        "poster_username": post.poster_username,
        "title": post.title,
        "content": post.content,
        "created_at": post.created_at
    }

    # Get all comments associated with the post
    comments = Comments.query.filter_by(post_id=post_id).order_by(Comments.created_at.desc()).all()

    # Prepare comment_info for rendering
    comment_info = [
        {
            "content": comment.content,
            "created_at": comment.created_at
        }
        for comment in comments
    ]

    # Render the template with post and comment information
    return render_template('view_post.html', post_info=post_info, comment_info=comment_info)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)

