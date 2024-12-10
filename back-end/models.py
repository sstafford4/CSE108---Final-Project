# from config import db
# from werkzeug.security import generate_password_hash, check_password_hash
# from datetime import datetime
#
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     real_name = db.Column(db.String(64), index=True, unique=True)
#     username = db.Column(db.String(100), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(250), nullable=False)
#
#     def __init__(self, real_name, username, email, password):
#         self.real_name = real_name
#         self.username = username
#         self.email = email
#
#     # werkzeug auto-salts all of the passwords it hashes, so we dont need any further password adjustments.
#     def set_password(self, password):
#         self.password = generate_password_hash(password)
#
#     def check_password(self, password):
#         return check_password_hash(self.password, password)
#
#     def to_json(self):
#         return {
#             'realName': self.real_name,
#             'username': self.username,
#             'email': self.email
#         }
#
# class Topic(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#
#
# class Posts(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     poster_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
#     title = db.Column(db.String(64), index=True, unique=True, nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.now)
#     updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
#
#     def __init__(self, poster_id, title, content):
#         self.poster_id = poster_id
#         self.title = title
#         self.content = content
#
#     def to_json(self):
#         return {
#             'id': self.id,
#             'poster_id': self.poster_id,
#             'title': self.title,
#             'content': self.content,
#             'created_at': self.created_at.isoformat(),
#             'updated_at': self.updated_at.isoformat()
#         }


from config import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

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
    poster_username = db.Column(db.String(100), unique=True, nullable=False)
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