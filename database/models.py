from datetime import datetime
from database.db import db
from flask_bcrypt import generate_password_hash, check_password_hash


class Group(db.Document, db.DynamicDocument):
    name = db.StringField(required=True, unique=True)
    type = db.StringField(required=True, choices=["PUBLIC", "PRIVATE"])
    members = db.ListField(db.StringField())
    moderators = db.ListField(db.StringField())
    admins = db.ListField(db.StringField())


class User(db.Document, db.DynamicDocument):
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True)
    password = db.StringField(required=True)

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Comment(db.Document, db.DynamicDocument):
    author = db.ReferenceField(User)
    content = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.utcnow)


class Post(db.Document, db.DynamicDocument):
    author = db.StringField(required=True)
    content = db.StringField(required=True)
    group = db.ReferenceField(Group)
    group_name = db.ReferenceField(Group)
    approved = db.BooleanField(default=False)
    comments = db.ListField(db.ReferenceField('Comment', reverse_delete_rule=db.PULL))
    added_by = db.ReferenceField('User')
    time = db.DateTimeField(default=datetime.utcnow)


Post.register_delete_rule(Comment, 'added_by', db.CASCADE)
