import pickle
from django.db import transaction
from .models import Question
from reference.models import Trade
import base64
import os
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

# --- Encryption Constants ---
MAGIC_NUMBER = b'ARM1'
SALT_SIZE = 16

def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a secure Fernet key from password using PBKDF2HMAC"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key_material = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(key_material)

def is_encrypted_dat(file_data):
    """Check if file is encrypted by looking for magic number"""
    return len(file_data) > 4 and file_data[:4] == MAGIC_NUMBER

def decrypt_dat_content(encrypted_data, password):
    """Decrypt encrypted DAT file content"""
    # Validate minimum length
    if len(encrypted_data) < 20:  # MAGIC(4) + SALT(16) = minimum 20 bytes
        raise ValueError("File too short to be a valid encrypted DAT file")
    
    pos = 4
    salt = encrypted_data[pos:pos + SALT_SIZE]
    pos += SALT_SIZE
    fernet_token = encrypted_data[pos:]

    # Validate we have actual encrypted data
    if len(fernet_token) == 0:
        raise ValueError("No encrypted data found in file")

    key = derive_key(password, salt)
    fernet = Fernet(key)

    try:
        decrypted_pickle = fernet.decrypt(fernet_token)
        return decrypted_pickle
    except InvalidToken:
        raise ValueError("Invalid password or corrupted file.")

def encrypt_and_package(raw_pickle_data, password):
    """Encrypt data and package with custom header"""
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    fernet = Fernet(key)

    fernet_token = fernet.encrypt(raw_pickle_data)
    encrypted_data = MAGIC_NUMBER + salt + fernet_token
    return encrypted_data

# --- Original Functions ---
def load_dat_from_filefield(file_field):
    """Read pickle .dat and return Python object"""
    with file_field.open("rb") as f:
        return pickle.load(f)

@transaction.atomic
def import_questions_from_dicts(records):
    """Import questions from list of dictionaries"""
    created = []
    for q in records:
        trade = Trade.objects.filter(name=q.get("trade")).first() if q.get("trade") else None

        obj = Question.objects.create(
            text=q["text"],
            part=q["part"],
            marks=q.get("marks", 1),
            options=q.get("options"),
            correct_answer=q.get("correct_answer"),
            trade=trade,
        )
        created.append(obj)
    return created