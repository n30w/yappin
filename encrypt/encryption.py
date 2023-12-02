from shared.files import *
import random
import string

import rsa

"""
IDEA:
1. password generator to suggest to a new user
        they can say if they want to use it or not in a GUI interface

        if they do: then there is a correpsonding username (or personally created username) to the password
        else not: the user can create their own password and username

2. encrypted private 1 on 1 chat:
        GUI will  displays last 4 characters of some encrypted string in the private chat
        in the video dicuss how it can be extend to mutiple users in a group chat

"""


"""class encrypter()

methods RSA 256 bit
string --> enc
enc --> string

attributes
def __init__(self, key):
    self.public_key : str
    self.private_key : str

look up: type annotation python

public and private key
"""


class Key:
    def __init__(self, key: rsa.PublicKey | rsa.PrivateKey) -> None:
        self.key: rsa.PublicKey | rsa.PrivateKey = key

        # checks if a key has been saved to disk or not
        self.saved_to_disk: bool = False

        # path to save file
        self.save_path: str = ""

    def serialize(self) -> str:
        # save_pkcs1 returns bytes, then .decode is a method of bytes class, decodes into UTF-8
        return self.key.save_pkcs1().decode("utf-8")

    def save(self, path: str) -> None:
        """saves key in string form to text file. If already saved, returns True."""
        write(self.serialize(), path)
        # if no errors
        self.saved_to_disk = True

    def load(self, path: str) -> str:
        """loads a key from disk text file."""
        return read(path)  # remove any \n


class Locksmith:
    def check_for_local_keys(self) -> bool:
        """Tries to find if there are any local keys already generated."""

    @staticmethod
    def generate_keys() -> (Key, Key):
        """
        Generates the public and private keys for the client.
        """

        (rsa_gen_pub, rsa_gen_prv) = rsa.newkeys(256)

        public_key: Key = Key(rsa_gen_pub)
        private_key: Key = Key(rsa_gen_prv)

        return (public_key, private_key)

    @staticmethod
    def encrypt(public_key: Key, message: str) -> str:
        """
        Takes a non-encrypted message, then encrypts it, then returns the encrypted string.
        """
        return rsa.encrypt(message.encode(), public_key.key).decode("utf-8")

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
