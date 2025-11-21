# auth.py
import db

def create_user(username, password, role="user"):
    db.create_user(username, password, role)

def authenticate(username, password):
    return db.verify_user(username, password)

def get_role(username):
    return db.get_user_role(username)
