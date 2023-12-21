from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    
    # Define the many-to-many relationship with GroupChat
    group_chats = db.relationship('GroupChats', secondary='user_group_chat', back_populates='users')

class GroupChats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.String(255), nullable=False, unique=True)
    account_sid = db.Column(db.String(255))
    chat_service_sid = db.Column(db.String(255))
    messaging_service_sid = db.Column(db.String(255))
    friendly_name = db.Column(db.String(255))
    unique_name = db.Column(db.String(255))
    attributes = db.Column(db.JSON)
    date_created = db.Column(db.String(255))
    date_updated = db.Column(db.String(255))
    state = db.Column(db.String(255))
    
    # Define the many-to-many relationship with User
    users = db.relationship('User', secondary='user_group_chat', back_populates='group_chats')

# Define the association table for the many-to-many relationship
user_group_chat = db.Table('user_group_chat',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_chat_id', db.Integer, db.ForeignKey('group_chats.id'), primary_key=True)
)
