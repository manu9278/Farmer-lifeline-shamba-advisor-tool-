from encryption import encrypt_data, decrypt_data


message = "Maize leaves are turning yellow."

encrypted = encrypt_data(message)

print("Encrypted data:")
print(encrypted)

decrypted = decrypt_data(encrypted)

print("\nDecrypted data:")
print(decrypted)