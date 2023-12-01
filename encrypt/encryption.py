import pickle
import random
import string

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
    def __init__(self, key: str) -> None:
        self.key: str = key

    def write(self, path="_key") -> None:
        """Pickles the key."""
        file = open(path, "wb")
        pickle.dump(self, file)
        file.close()

    def read(self, path="_key") -> str:
        """Reads the key from the pickling"""
        file = open(path, "rb")
        data: Key = pickle.load(file)
        file.close()
        return data.key


class Encrypter:
    def __init__(self) -> None:
        self.public_key: str
        self.private_key: str

    def generate_keys(self) -> None:
        """
        Generates the public and private keys for the client.
        """
        pass

    def encrypt(self, message: str) -> str:
        """
        Takes a non-encrypted message, then encrypts it, then returns the encrypted string.
        """
        pass

    def decrypt(self, message: str) -> str:
        """
        Takes an encrypted message, decrypts it, then returns the decrypted string.
        """
        pass


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
