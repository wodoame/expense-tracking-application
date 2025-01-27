### Step 1: Install the `cryptography` Library
First, you need to install the `cryptography` library, which provides cryptographic recipes and primitives for Python.

```bash
pip install cryptography
```

### Step 2: Create an Encryption Utility
Create a utility class or module to handle encryption and decryption. This will make it easy to reuse the encryption logic across your application.

```python
# utils/encryption.py
from cryptography.fernet import Fernet

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
        decrypted_data = self.cipher.decrypt(encrypted_data)
        return decrypted_data.decode('utf-8')
```

### Step 3: Store the Encryption Key Securely
The encryption key is critical for encrypting and decrypting data. Store it securely, such as in environment variables or Django's `settings.py` (but avoid hardcoding it in the codebase).

For example, in `settings.py`:

```python
# settings.py
import os
from django.core.exceptions import ImproperlyConfigured

def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        raise ImproperlyConfigured(f"Set the {var_name} environment variable")

ENCRYPTION_KEY = get_env_variable('ENCRYPTION_KEY')
```

Then, set the `ENCRYPTION_KEY` environment variable in your system or `.env` file:

```bash
export ENCRYPTION_KEY='your-encryption-key-here'
```

### Step 4: Use Encryption in Your Django Models
Now, integrate the encryption utility into your Django models. For example, if you have a `UserExpenditure` model:

```python
# models.py
from django.db import models
from utils.encryption import EncryptionHelper
from django.conf import settings

class UserExpenditure(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encryption_helper = EncryptionHelper(key=settings.ENCRYPTION_KEY)

    def save(self, *args, **kwargs):
        # Encrypt sensitive fields before saving
        self.item_name = self.encryption_helper.encrypt(self.item_name)
        self.description = self.encryption_helper.encrypt(self.description)
        super().save(*args, **kwargs)

    def get_item_name(self):
        # Decrypt the item name when needed
        return self.encryption_helper.decrypt(self.item_name)

    def get_description(self):
        # Decrypt the description when needed
        return self.encryption_helper.decrypt(self.description)
```

### Step 5: Use the Encrypted Data in Views
When retrieving data, decrypt it before displaying or processing:

```python
# views.py
from django.shortcuts import render
from .models import UserExpenditure

def expenditure_detail(request, expenditure_id):
    expenditure = UserExpenditure.objects.get(id=expenditure_id)
    context = {
        'item_name': expenditure.get_item_name(),
        'price': expenditure.price,  # Price is not encrypted
        'description': expenditure.get_description(),
    }
    return render(request, 'expenditure_detail.html', context)
```

### Step 6: Handle Encryption Key Rotation (Optional)
If you need to rotate the encryption key (e.g., for security reasons), you’ll need to re-encrypt all existing data with the new key. This can be done with a Django management command or a script.

### Notes:
1. **Performance**: Encryption and decryption add some overhead. Ensure you test the performance impact on your application.
2. **Backup Key**: Always back up your encryption key securely. Losing it means losing access to your encrypted data.
3. **Database Indexing**: Encrypted fields cannot be indexed or searched directly. If you need to search or filter by these fields, consider using techniques like deterministic encryption or hashing for specific use cases.