import hashlib
import os
import base64


SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
KEY_LEN = 64
SALT_LEN = 16

def hash_password(password: str) -> str:
    salt = os.urandom(SALT_LEN)
    key = hashlib.scrypt(
        password=password.encode(),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=KEY_LEN
    )

    return base64.b64encode(salt + key).decode()


def verify_password(password: str, stored_hash: str):
    try:
        decoded = base64.b64decode(stored_hash.encode())
        salt = decoded[:SALT_LEN]
        stored_key = decoded[SALT_LEN:]

        new_key = hashlib.scrypt(
            password=password.encode(),
            salt=salt,
            n=SCRYPT_N,
            r=SCRYPT_R,
            p=SCRYPT_P,
            dklen=KEY_LEN
        )

        return new_key == stored_key
    except Exception:
        return False
    