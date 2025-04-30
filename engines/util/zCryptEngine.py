# Last modified: 2025-01-30 06:16:37
# Version: 0.0.9
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
import base64
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union


# secretKey16bytes


def pad_data(data):
    """Pad the data to be compatible with AES block size (16 bytes)."""
    padder = PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    return padded_data


def unpad_data(data):
    """Remove padding from the decrypted data."""
    unpadder = PKCS7(128).unpadder()
    unpadded_data = unpadder.update(data) + unpadder.finalize()
    return unpadded_data


def genHash(theStringOfText):

    theStringOfText = theStringOfText.strip().lower().encode()
    cipher = Cipher(
        algorithms.AES(secretKey16bytes), modes.ECB(), backend=default_backend()
    )
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(pad_data(theStringOfText)) + encryptor.finalize()
    # Encode as base64 and truncate to 8 characters
    return base64.urlsafe_b64encode(encrypted_data).decode()[:8]


def decryptHash(shortToken):
    """Decipher the short token back to the original email address."""
    # Pad the token back to a valid base64 length and decode
    padded_token = (shortToken + "=" * ((4 - len(shortToken) % 4) % 4)).encode()
    encrypted_data = base64.urlsafe_b64decode(padded_token)
    cipher = Cipher(
        algorithms.AES(secretKey16bytes), modes.ECB(), backend=default_backend()
    )
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    return unpad_data(decrypted_data).decode()


def verifyAuthToken(theStringOfText, userAuthToken):

    theStringOfText = theStringOfText.strip().lower()
    generatedToken = genHash(theStringOfText)
    return generatedToken == userAuthToken
