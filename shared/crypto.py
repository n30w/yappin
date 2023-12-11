""" This has nothing to do with cryptocurrency. """

"""
RSA ENCRYPTION FUNCTIONS
"""

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


def generate_keys() -> tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    return private_key, public_key


def encrypt_message(message: str, public_key: rsa.RSAPublicKey) -> bytes:
    encrypted_message = public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return encrypted_message


def decrypt_message(encrypted_message: bytes, private_key: rsa.RSAPrivateKey) -> str:
    original_message = private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return original_message.decode()


# Example usage
private_key, public_key = generate_keys()
message = "Hello, this is a secure message."
encrypted_message = encrypt_message(message, public_key)
print("Encrypted message:", encrypted_message)

decrypted_message = decrypt_message(encrypted_message, private_key)
print("Decrypted message:", decrypted_message)


from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from os import urandom


"""
AES ENCRYPTION FUNCTIONS
"""


def generate_aes_key() -> bytes:
    return urandom(32)  # AES key of 256 bits


def encrypt_aes(message: str, key: bytes) -> bytes:
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(message.encode()) + padder.finalize()

    iv = urandom(16)  # Initialization vector
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    encrypted_message = encryptor.update(padded_data) + encryptor.finalize()

    return iv + encrypted_message  # Prepend IV for use in decryption


def decrypt_aes(encrypted_message: bytes, key: bytes) -> str:
    iv = encrypted_message[:16]
    encrypted_message = encrypted_message[16:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_message = decryptor.update(encrypted_message) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    message = unpadder.update(padded_message) + unpadder.finalize()

    return message.decode()
