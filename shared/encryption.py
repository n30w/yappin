# from shared.files import *
import random
import string

import rsa

from shared.files import write, read

N_BITS_OF_ENCRYPTION = 512


class Key:
    def __init__(self, key: rsa.PublicKey | rsa.PrivateKey = None) -> None:
        self.key: rsa.PublicKey | rsa.PrivateKey = key

        # checks if a key has been saved to disk or not
        self.saved_to_disk: bool = False

        # path to save file
        self.save_path: str = ""

    def serialize(self) -> str:
        """
        Creates a serialized version of the key, can be used to transmit.
        """
        # save_pkcs1 returns bytes, then .decode is a method of bytes class, decodes into UTF-8
        return self.key.save_pkcs1().decode("utf-8")

    def deserialize(self, key: str) -> None:
        """
        Deserializes a key from utf-8 format into bytes which can be used to encrypt.
        """

        # converts the string to bytes
        key_bytes = key.encode("utf-8")

        self.key = rsa.PublicKey.load_pkcs1(key_bytes)

    def save(self, path: str) -> None:
        """saves key in string form to text file. If already saved, returns True."""
        write(self.serialize(), path)
        # if no errors
        self.saved_to_disk = True

    def load(self, path: str) -> str:
        """loads a key from disk text file."""
        return read(path)  # remove any \n


def new_key_from_utf(key: str) -> Key:
    k = deserialize_key(key)
    return Key(k)


def deserialize_key(key: str) -> rsa.PublicKey:
    key_bytes = key.encode("utf-8")
    return rsa.PublicKey.load_pkcs1(key_bytes)


class Locksmith:
    def check_for_local_keys(self) -> bool:
        """Tries to find if there are any local keys already generated."""
        pass

    @staticmethod
    def generate_keys() -> (Key, Key):
        """
        Generates the public and private keys for the client.
        """

        (rsa_gen_pub, rsa_gen_prv) = rsa.newkeys(N_BITS_OF_ENCRYPTION)

        public_key: Key = Key(rsa_gen_pub)
        private_key: Key = Key(rsa_gen_prv)

        return (public_key, private_key)

    @staticmethod
    def encrypt(public_key: Key, message: str) -> str:
        """
        Takes a non-encrypted message, then encrypts it, then returns the encrypted string.
        """
        utf_bytes = message.encode("utf-8")
        encrypted_bytes = rsa.encrypt(utf_bytes, public_key.key)
        decoded = encrypted_bytes.decode("utf-8")
        return decoded

    @staticmethod
    def decrypt(private_key: Key, message: str) -> str:
        """
        Takes an encrypted message, decrypts it, then returns the decrypted string.
        """
        return rsa.decrypt(message.encode(), private_key.key).decode("utf-8")


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
