class Encrypt(object):
    def __init__(self, key):
        self.key = key

    def encrypt(self, message):
        encrypted_message = ""
        for i in range(len(message)):
            key_c = self.key[i % len(self.key)]
            encrypted_message += chr((ord(message[i]) + ord(key_c)) % 256)
        return encrypted_message

    def decrypt(self, encrypted_message):
        message = ""
        for i in range(len(encrypted_message)):
            key_c = self.key[i % len(self.key)]
            message += chr((ord(encrypted_message[i]) - ord(key_c)) % 256)
        return message

