from flask import render_template, request, url_for, redirect, flash, session, Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
# from config import app, db
# from models import User, Topic, Posts
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

# SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
#     username="sstafford4",
#     password="FinalProj2024",
#     hostname="sstafford4.mysql.pythonanywhere-services.com",
#     databasename="sstafford4$final_project",
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

    def like_count(self):
        return self.post_likes.filter_by(is_like=True).count()

    def dislike_count(self):
        return self.post_likes.filter_by(is_like=False).count()

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
            'updated_at': self.updated_at.isoformat(),
            'like_count': self.like_count(),
            'dislike_count': self.dislike_count()
        }

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    comment_username = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationships
    user = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    post = db.relationship('Posts', backref=db.backref('comments', lazy='dynamic'))

    def __init__(self, post_id, user_id, comment_username,content):
        self.post_id = post_id
        self.user_id = user_id
        self.comment_username = comment_username
        self.content = content

    def to_json(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'comment_username': self.comment_username,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }

class PostLikes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    is_like = db.Column(db.Boolean, nullable=False)  # True for like, False for dislike
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationships
    user = db.relationship('User', backref=db.backref('post_likes', lazy='dynamic'))
    post = db.relationship('Posts', backref=db.backref('post_likes', lazy='dynamic'))


    def __init__(self, user_id, post_id, is_like):
        self.user_id = user_id
        self.post_id = post_id
        self.is_like = is_like

    def to_json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'is_like': self.is_like,
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

        recent_comments = (
            db.session.query(
                Comments.id.label('comment_id'),
                Comments.content.label('comment_content'),
                Comments.comment_username.label('commenter_username'),
                Comments.created_at.label('comment_date'),
                Posts.id.label('post_id'),
                Posts.title.label('post_title'),
                User.id.label('user_id'),
                User.real_name.label('user_real_name'),
                User.username.label('user_username')
            )
            .join(Posts, Comments.post_id == Posts.id)
            .join(User, Comments.user_id == User.id)
            .order_by(Comments.created_at.desc())
            .limit(4)
            .all()
        )

        # Convert recent comments to a JSON-friendly format for the template
        recent_comments_list = [
            {
                'comment_id': comment.comment_id,
                'comment_content': comment.comment_content,
                'commenter_username': comment.commenter_username,
                'comment_date': comment.comment_date,
                'post_id': comment.post_id,
                'post_title': comment.post_title,
                'user_id': comment.user_id,
                'user_real_name': comment.user_real_name,
                'user_username': comment.user_username
            }
            for comment in recent_comments
        ]

        return render_template('main_page.html',
                               all_topics=all_topics,
                               followed_topic_ids=followed_topic_ids,
                               posts=relevant_posts,
                               username=username,
                               recent_comments=recent_comments_list
                               )
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

            # all_topics = Topic.query.all()
            # relevant_posts = Posts.query.all()

            followed_topics = user.followed_topics
            all_topics = Topic.query.all()

            # Get the posts for the topics the user is following
            # relevant_posts = Posts.query.filter(Posts.topic_id.in_([topic.id for topic in followed_topics])).all()
            relevant_posts = Posts.query.filter(
                Posts.topic_id.in_([topic.id for topic in followed_topics])
            ).order_by(Posts.created_at.desc()).all()
            # Get a list of topic IDs that the user is following
            followed_topic_ids = [topic.id for topic in followed_topics]

            recent_comments = (
                db.session.query(
                    Comments.id.label('comment_id'),
                    Comments.content.label('comment_content'),
                    Comments.comment_username.label('commenter_username'),
                    Comments.created_at.label('comment_date'),
                    Posts.id.label('post_id'),
                    Posts.title.label('post_title'),
                    User.id.label('user_id'),
                    User.real_name.label('user_real_name'),
                    User.username.label('user_username')
                )
                .join(Posts, Comments.post_id == Posts.id)
                .join(User, Comments.user_id == User.id)
                .order_by(Comments.created_at.desc())
                .limit(4)
                .all()
            )

            # Convert recent comments to a JSON-friendly format for the template
            recent_comments_list = [
                {
                    'comment_id': comment.comment_id,
                    'comment_content': comment.comment_content,
                    'commenter_username': comment.commenter_username,
                    'comment_date': comment.comment_date,
                    'post_id': comment.post_id,
                    'post_title': comment.post_title,
                    'user_id': comment.user_id,
                    'user_real_name': comment.user_real_name,
                    'user_username': comment.user_username
                }
                for comment in recent_comments
            ]

            flash("Logged in!")
            return render_template('main_page.html', all_topics=all_topics, user_id=user.id, username=user.username, posts=relevant_posts, followed_topic_ids=followed_topic_ids, recent_comments=recent_comments_list)
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

    recent_comments = (
        db.session.query(
            Comments.id.label('comment_id'),
            Comments.content.label('comment_content'),
            Comments.comment_username.label('commenter_username'),
            Comments.created_at.label('comment_date'),
            Posts.id.label('post_id'),
            Posts.title.label('post_title'),
            User.id.label('user_id'),
            User.real_name.label('user_real_name'),
            User.username.label('user_username')
        )
        .join(Posts, Comments.post_id == Posts.id)
        .join(User, Comments.user_id == User.id)
        .order_by(Comments.created_at.desc())
        .limit(4)
        .all()
    )

    # Convert recent comments to a JSON-friendly format for the template
    recent_comments_list = [
        {
            'comment_id': comment.comment_id,
            'comment_content': comment.comment_content,
            'commenter_username': comment.commenter_username,
            'comment_date': comment.comment_date,
            'post_id': comment.post_id,
            'post_title': comment.post_title,
            'user_id': comment.user_id,
            'user_real_name': comment.user_real_name,
            'user_username': comment.user_username
        }
        for comment in recent_comments
    ]

    # Combine results and remove duplicates
    search_results = list({post.id: post for post in posts_by_topic + posts_by_user + posts_by_title}.values())

    # Render the main page with the new search results
    return render_template('main_page.html', search_results=search_results, query=query, all_topics=all_topics,
                                   followed_topic_ids=followed_topic_ids,
                                   posts=relevant_posts,
                                   username=username, recent_comments=recent_comments_list)


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
    comment = Comments(post_id=post_id, user_id=user_id, comment_username=user.username, content=content)
    try:
        db.session.add(comment)
        db.session.commit()

        # Redirect back to the post page to reload with the new comment
        return redirect(url_for('view_post', post_id=post_id))

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {str(e)}")
        return redirect(url_for('view_post', post_id=post_id))


@app.route('/view_post/<int:post_id>', methods=['GET'])
def view_post(post_id):
    user_id = session.get('user_id')
    username = session.get('username')

    post = Posts.query.get(post_id)
    if post is None:
        return "Post not found", 404

    comments = Comments.query.filter_by(post_id=post_id).order_by(Comments.created_at.desc()).all()
    like_count = PostLikes.query.filter_by(post_id=post_id, is_like=True).count()
    dislike_count = PostLikes.query.filter_by(post_id=post_id, is_like=False).count()

    user_like_status = None
    if user_id:
        like_entry = PostLikes.query.filter_by(user_id=user_id, post_id=post_id).first()
        if like_entry:
            user_like_status = "like" if like_entry.is_like else "dislike"

    return render_template('view_post.html',
                           post_info=post,
                           comment_info=comments,
                           like_count=like_count,
                           dislike_count=dislike_count,
                           user_like_status=user_like_status)

@app.route('/like_post/<int:post_id>', methods=['GET','POST'])
def like_post(post_id):
    if 'logged_in' in session:
        user_id = session['user_id']
        like_entry = PostLikes.query.filter_by(user_id=user_id, post_id=post_id).first()

        # Check if the user already liked or disliked the post
        if like_entry:
            if like_entry.is_like:
                db.session.delete(like_entry)  # Remove like if already liked
            else:
                like_entry.is_like = True  # Switch from dislike to like
        else:
            # Add a new like
            like_entry = PostLikes(user_id=user_id, post_id=post_id, is_like=True)
            db.session.add(like_entry)

        db.session.commit()
        return redirect(url_for('view_post', post_id=post_id))
    else:
        flash("You need to log in to like posts.")
        return redirect(url_for('login'))

@app.route('/dislike_post/<int:post_id>', methods=['GET', 'POST'])
def dislike_post(post_id):
    if 'logged_in' in session:
        user_id = session['user_id']
        like_entry = PostLikes.query.filter_by(user_id=user_id, post_id=post_id).first()

        # Check if the user already liked or disliked the post
        if like_entry:
            if not like_entry.is_like:
                db.session.delete(like_entry)  # Remove dislike if already disliked
            else:
                like_entry.is_like = False  # Switch from like to dislike
        else:
            # Add a new dislike
            like_entry = PostLikes(user_id=user_id, post_id=post_id, is_like=False)
            db.session.add(like_entry)

        db.session.commit()
        return redirect(url_for('view_post', post_id=post_id))
    else:
        flash("You need to log in to dislike posts.")
        return redirect(url_for('login'))

@app.route('/account_settings', methods=['GET', 'POST'])
def account_settings():
    if 'logged_in' in session:
        user_id = session['user_id']
        username = session.get('username')

        your_posts = Posts.query.filter_by(poster_id=user_id).order_by(Posts.created_at.desc()).all()

        return render_template('account_settings.html', posts=your_posts, username=username)

@app.route('/view_profile/<int:poster_id>', methods=['GET', 'POST'])
def view_profile(poster_id):
    post_user = User.query.get(poster_id)
    if post_user is None:
        return "User not found", 404

    all_user_posts = Posts.query.filter_by(poster_id=poster_id).all()

    return render_template('view_profile.html', posts=all_user_posts, username=post_user.username)

@app.route('/delete_post/<int:post_id>', methods=['DELETE', 'GET', 'POST'])
def delete_post(post_id):
    # Retrieve the post by its ID
    post = Posts.query.get(post_id)

    if not post:
        # If the post does not exist, return a 404 error
        flash("Post not found")

    try:
        # Delete related comments
        Comments.query.filter_by(post_id=post_id).delete()

        # Delete related likes
        PostLikes.query.filter_by(post_id=post_id).delete()

        # Delete the post itself
        db.session.delete(post)
        db.session.commit()

        # Return a success message
        return redirect(url_for('account_settings'))
    except Exception as e:
        # Rollback the session in case of any errors
        db.session.rollback()
        return redirect(url_for('account_settings'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)