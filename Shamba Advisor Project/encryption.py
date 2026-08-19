from cryptography.fernet import Fernet


def generate_key():
    key = Fernet.generate_key()

    with open("secret.key", "wb") as key_file:
        key_file.write(key)

    return key


def load_key():
    try:
        with open("secret.key", "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        return generate_key()


def encrypt_data(data):
    key = load_key()
    cipher = Fernet(key)

    encrypted_data = cipher.encrypt(
        data.encode()
    )

    return encrypted_data


def decrypt_data(encrypted_data):
    key = load_key()
    cipher = Fernet(key)

    decrypted_data = cipher.decrypt(
        encrypted_data
    )

    return decrypted_data.decode()