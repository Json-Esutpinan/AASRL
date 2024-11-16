import hashlib
import os

def generate_salt():
    return os.urandom(16).hex()

def hash_password(password, salt):
    return hashlib.sha256((salt + password).encode()).hexdigest()

def verify_password(input_password, stored_hash, salt):
    return hash_password(input_password, salt) == stored_hash
