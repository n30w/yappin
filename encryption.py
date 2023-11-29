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

<<<<<<< Updated upstream
public and private key 

=======
public and private key
>>>>>>> Stashed changes
"""


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
