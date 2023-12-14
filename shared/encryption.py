# from shared.files import *
from abc import ABC, abstractmethod
import random
import string

from cryptography.hazmat.primitives.asymmetric import rsa
from shared.files import write, read
from shared.crypto import (
    base_64_to_public_key,
    decrypt_aes,
    decrypt_message_with_rsa,
    encrypt_aes,
    encrypt_message_with_rsa,
    from_base_64,
    generate_aes_key,
    generate_rsa_keys,
    serialize_public_key,
    to_base_64,
)

N_BITS_OF_ENCRYPTION = 256


type AES_Key = bytes


class Key(ABC):
    def __init__(
        self, key: rsa.RSAPublicKey | rsa.RSAPrivateKey | AES_Key = None
    ) -> None:
        self.key: rsa.RSAPublicKey | rsa.RSAPrivateKey | AES_Key = key
        # checks if a key has been saved to disk or not
        self.saved_to_disk: bool = False

        # path to save file
        self.save_path: str = ""

    @abstractmethod
    def serialize(self) -> str:
        """
        Creates a serialized version of the key, can be used to transmit.
        """
        return ""

    @abstractmethod
    def deserialize(self, key: str) -> None:
        """
        Expects a string encoded in base64 for the key.
        """
        return None

    @abstractmethod
    def encrypt_and_encode(self, message: str) -> str:
        """
        Encodes and encrypts message using key. The return value is a Base64 encoded string.
        """
        return ""

    @abstractmethod
    def decode_and_decrypt(self, message: str) -> str:
        """
        Decodes and decrypts a message using key. The message is expected to be encoded in Base64 format!
        """
        return ""


class RSAKey(Key):
    def __init__(self, key: rsa.RSAPublicKey | rsa.RSAPrivateKey = None) -> None:
        super().__init__(key)

    def serialize(self) -> str:
        b: bytes = serialize_public_key(self.key)
        s: str = to_base_64(b)
        return s

    def deserialize(self, key: str) -> None:
        new_key: rsa.RSAPublicKey = base_64_to_public_key(key)
        self.key = new_key

    def encrypt_and_encode(self, message: str) -> str:
        b: bytes = encrypt_message_with_rsa(message, self.key)
        s: str = to_base_64(b)
        return s

    def decode_and_decrypt(self, message: str) -> str:
        b: bytes = from_base_64(message)
        s: str = decrypt_message_with_rsa(s, self.key)
        return s


class AESKey(Key):
    def __init__(self) -> None:
        key = Locksmith.generate_session_key()
        super().__init__(key)

    def serialize(self) -> str:
        return to_base_64(self.key)

    def deserialize(self, key: str) -> None:
        self.key = from_base_64(key)

    def encrypt_and_encode(self, message: str) -> str:
        b: bytes = encrypt_aes(message, self.key)
        s: str = to_base_64(b)
        return s

    def decode_and_decrypt(self, message: str) -> str:
        b: bytes = from_base_64(message)
        s: str = decrypt_aes(b, self.key)
        return s


class Locksmith:
    def check_for_local_keys(self) -> bool:
        """Tries to find if there are any local keys already generated."""
        pass

    @staticmethod
    def generate_session_key() -> Key:
        k = generate_aes_key()
        aes_key: Key = Key(k)
        return aes_key

    @staticmethod
    def generate_rsa_keys() -> tuple[RSAKey, RSAKey]:
        """
        Generates the public and private keys for the client, as well as a custom session key.
        """
        rsa_gen_prv: rsa.RSAPrivateKey
        rsa_gen_pub: rsa.RSAPublicKey

        rsa_gen_prv, rsa_gen_pub = generate_rsa_keys()

        public_key: RSAKey = RSAKey(rsa_gen_pub)
        private_key: RSAKey = RSAKey(rsa_gen_prv)

        return (public_key, private_key)

    @staticmethod
    def generate_session_key() -> AESKey:
        session_key = generate_aes_key()
        return AESKey(session_key)


def generate_password(password_length: str) -> str:
    """
    Generates a password using random package. Returns empty string if length is invalid.

    ### Args
        password_length: str -- length of password, given as a string from GUI input.
    """
    length = int(password_length)
    if length >= 5 and length <= 40:
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))
    return ""
