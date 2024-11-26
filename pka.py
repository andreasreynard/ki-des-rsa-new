from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key, load_pem_private_key, Encoding, PublicFormat, PrivateFormat, NoEncryption
)
import time

# Generate RSA key pairs for Client1, Client2, and the PKA
def generate_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key

# Encrypt a message with a public key
def enc_w_pu(public_key, message):
    return public_key.encrypt(message, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))

# Decrypt a message with a private key
def dec_w_pr(private_key, ciphertext):
    return private_key.decrypt(ciphertext, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))

# Sign a message with a private key
def sign_w_pr(private_key, message):
    return private_key.sign(message, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),hashes.SHA256())

# Verify a signature with a public key
def ver_w_pu(public_key, message, signature):
    try:
        public_key.verify(signature, message, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
        return True
    except Exception:
        return False

# Simulate the PKA
class PKA:
    def __init__(self, private_key, public_key):
        self.private_key = private_key
        self.public_key = public_key
        self.public_keys = {}

    def register_user(self, user_id, public_key):
        self.public_keys[user_id] = public_key

    def get_public_key(self, user_id, request, timestamp):
        if user_id in self.public_keys:
            message = self.public_keys[user_id].public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo) + request + timestamp
            signature = sign_w_pr(self.private_key, message)
            return message, signature
        else:
            raise Exception('User not found')

def main_key(num):
    # Generate keys for Client1, Client2, and the PKA
    private_key_pka, public_key_pka = generate_keys()
    private_key1, public_key1 = generate_keys()
    private_key2, public_key2 = generate_keys()

    # Register Client1 and Client2 with the PKA
    pka = PKA(private_key_pka, public_key_pka)
    pka.register_user('Client1', public_key1)
    pka.register_user('Client2', public_key2)

    # Client1 requests Client2's public key from the PKA
    public_key_message2, signature2 = pka.get_public_key('Client2', b"Request Client2's public key", str(time.time()).encode())

    # Verify PKA's response
    if ver_w_pu(public_key_pka, public_key_message2, signature2):
        print("Client2's public key verified from PKA")
        public_key2 = load_pem_public_key(public_key_message2[:450])  # Adjust for key size

    # Client1 sends a message to Client2
    nonce1 = b'+-;:,.?!'
    message2client2 = enc_w_pu(public_key2, b'Client1||' + nonce1)
    print('Client1 sent encrypted message to Client2')

    # Client2 decrypts Client1's message
    decrypted_message = dec_w_pr(private_key2, message2client2)
    id_client1, received_nonce1 = decrypted_message.split(b'||')
    print(f'Client2 received message: ID={id_client1.decode()}, Nonce1={received_nonce1.hex()}')

    # Client2 requests Client1's public key from the PKA
    public_key_message1, signature1 = pka.get_public_key('Client1', b"Request Client1's public key", str(time.time()).encode())

    # Verify PKA's response
    if ver_w_pu(public_key_pka, public_key_message1, signature1):
        print("Client1's public key verified from PKA")
        public_key1 = load_pem_public_key(public_key_message1[:450])  # Adjust for key size

    # Client2 responds to Client1 with a new nonce
    nonce2 = b'GHijWxyZ'
    response2client1 = enc_w_pu(public_key1, received_nonce1 + b'||' + nonce2)
    print('Client2 sent encrypted response to Client1')

    # Client1 decrypts Client2's response
    decrypted_response = dec_w_pr(private_key1, response2client1)
    received_nonce1_from_client2, received_nonce2 = decrypted_response.split(b'||')
    if received_nonce1_from_client2 == nonce1:
        print(f'Client1 verified Nonce1: {received_nonce1_from_client2.hex()}')
        print(f'Client1 received Nonce2: {received_nonce2.hex()}')

    # Client1 sends Nonce2 back to Client2
    final_message2client2 = enc_w_pu(public_key2, received_nonce2)
    print('Client1 sent Nonce2 back to Client2')

    # Client2 verifies Nonce2
    final_response = dec_w_pr(private_key2, final_message2client2)
    if final_response == nonce2:
        print(f'Client2 verified Nonce2: {final_response.hex()}')
        print('Mutual authentication complete!')

    if num == 1:
        return received_nonce1_from_client2.hex()
    if num == 2:
        return final_response.hex()
