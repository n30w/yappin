""" This has nothing to do with cryptocurrency. """

"""
RSA ENCRYPTION FUNCTIONS
"""

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding as pd
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from os import urandom
import base64


def generate_rsa_keys() -> tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    return private_key, public_key


def encrypt_message_with_rsa(message: str, public_key: rsa.RSAPublicKey) -> bytes:
    encrypted_message = public_key.encrypt(
        message.encode(),
        pd.OAEP(
            mgf=pd.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return encrypted_message


def decrypt_message_with_rsa(
    encrypted_message: bytes, private_key: rsa.RSAPrivateKey
) -> str:
    original_message = private_key.decrypt(
        encrypted_message,
        pd.OAEP(
            mgf=pd.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return original_message.decode()


def serialize_public_key(public_key: rsa.RSAPublicKey) -> bytes:
    """
    Serializes a public key into bytes.
    """
    pem_public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pem_public_key


def base_64_to_public_key(encoded_key: str) -> rsa.RSAPublicKey:
    # Decode the key from Base64
    key_bytes = base64.b64decode(encoded_key)

    # Deserialize the public key
    public_key = serialization.load_pem_public_key(key_bytes)

    return public_key


def bytes_to_public_key(key: bytes) -> rsa.RSAPublicKey:
    public_key = serialization.load_der_public_key(key)
    return public_key


def public_key_to_base64(public_key: rsa.RSAPublicKey) -> str:
    # Serialize the public key to the PEM format
    pem_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # Encode the PEM key using Base64
    b64_encoded_key = base64.b64encode(pem_key).decode("utf-8")

    return b64_encoded_key


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


def to_base_64(text: bytes) -> str:
    """
    Translates bytes to a base64 equivalent string.
    """
    return base64.b64encode(text).decode("utf-8")


def from_base_64(text: str) -> bytes:
    """
    Translates a base64 encoded UTF-8 string into bytes.
    """
    return base64.b64decode(text)


def encrypt_and_encode_aes(message: str, key: bytes) -> str:
    """
    Encrypts a message from UTF-8 string encoding into bytes, then encodes it using the Base64 into a UTF-8 string for transmission.
    """
    encrypted_message: bytes = encrypt_aes(message, key)
    encoded_message: str = to_base_64(encrypted_message)
    return encoded_message


def decode_and_decrypt_aes(encoded_message: str, key: bytes) -> str:
    """
    Decodes a message from Base64 encoding into bytes, then decrypts it using the AES key
    """
    encrypted_message: bytes = from_base_64(encoded_message)
    decrypted_message: str = decrypt_aes(encrypted_message, key)
    return decrypted_message


# Example usage
# private_key, public_key = generate_rsa_keys()
# message = "Hello, this is a secure message."
# encrypted_message = encrypt_message_with_rsa(message, public_key)
# print("Encrypted message:", encrypted_message)
# b64k = public_key_to_base64(public_key)
# print(b64k)

# decrypted_message = decrypt_message_with_rsa(encrypted_message, private_key)
# print("Decrypted message:", decrypted_message)
