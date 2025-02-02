from cryptography.fernet import Fernet, InvalidToken
class EncryptionHelper:
    def __init__(self, key=None):
        # Generate a key if not provided
        if key is None:
            self.key = Fernet.generate_key()
        else:
            # Ensure the key is in bytes format
            if isinstance(key, str):
                self.key = key.encode('utf-8')  # Convert string to bytes
            elif isinstance(key, bytes):
                self.key = key
            else:
                raise TypeError("Key must be a string or bytes")

        self.cipher = Fernet(self.key)

    def encrypt(self, data):
        """
        Encrypts the given data.
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        encrypted_data = self.cipher.encrypt(data)
        return encrypted_data.decode('utf-8')

    def decrypt(self, encrypted_data):
        """
        Decrypts the given encrypted data.
        """
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode('utf-8')
        try:
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return decrypted_data.decode('utf-8')
        except InvalidToken:
            return encrypted_data.decode('utf-8') # return the data that was passed in as it is already decrypted (assumption for our purposes)
    
    def is_encrypted(self, data):
        return data != self.decrypt(data)  # If data is encrypted, it will be different from the decrypted data otherwise the decrypted data will be the same as the input data