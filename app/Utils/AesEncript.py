import os
import base64
from typing import Optional
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def _derive_key(password: str, salt: bytes, iterations: int = 100_000) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations)
    return kdf.derive(password.encode("utf-8"))

def encrypt_aes256(plaintext: str, password: str, iterations: int = 100_000) -> str:
    """
    Devuelve base64(salt(16) + iv(16) + ciphertext).
    """
    salt = os.urandom(16)
    key = _derive_key(password, salt, iterations)
    iv = os.urandom(16)

    padder = padding.PKCS7(128).padder()
    padded = padder.update(plaintext.encode("utf-8")) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ct = encryptor.update(padded) + encryptor.finalize()

    return base64.urlsafe_b64encode(salt + iv + ct).decode("utf-8")

def decrypt_aes256(token_b64: str, password: str, iterations: int = 100_000) -> Optional[str]:
    """
    Recibe base64(salt+iv+ciphertext) y devuelve el plaintext o None si falla.
    """
    try:
        data = base64.urlsafe_b64decode(token_b64)
        salt, iv, ct = data[:16], data[16:32], data[32:]
        key = _derive_key(password, salt, iterations)

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded = decryptor.update(ct) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded) + unpadder.finalize()
        return plaintext.decode("utf-8")
    except Exception:
        return None