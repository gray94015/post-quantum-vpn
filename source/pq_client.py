import argparse

import oqs
import socket
import time

HOST = "192.168.0.41"
PORT = 123

kemalg = "Kyber512"
sigalg = "Dilithium3"


def key_exchange(s):
    # Key exchange using Kyber512
    print("=====================Performing Key Exchange using Kyber512=====================")
    with oqs.KeyEncapsulation(kemalg) as kem_client:
        print("Generating Keypair...")
        client_public_key = kem_client.generate_keypair()
        time.sleep(2)
        print("Sending Public Key to the server...")
        s.sendall(client_public_key)
        time.sleep(2)
        # print(f"The public key from the client is: {client_public_key}")
        ciphertext = s.recv(1048576)
        print(f"Received ciphertext from the server.")
        print("Decapsulating the ciphertext from the server with my pulic key...")
        shared_secret_client = kem_client.decap_secret(ciphertext)
        time.sleep(2)
        print(f"The shared secret by the client is: {shared_secret_client}")
        print("=====================End of Key Exchange (Kyber512)=====================")


def digital_signature(s):
    # Digital Signature using Dilithium3
    print("=====================Performing Digital Signature using Dilithium3=====================")
    with oqs.Signature(sigalg) as sig_client:

        # Receiving Public Key, Message, and Signature from the server
        message_from_server = s.recv(1048576)
        data = message_from_server.split("EOF1".encode())
        public_key = data[0]
        message = data[1]
        signature = data[2]
        print("Received the data from the server.")

        # Verify the signature
        print("Verifying the signature...")
        time.sleep(2)
        if sig_client.verify(message, signature, public_key):
            print("Signature verified successfully.")
        else:
            print("Signature verification failed.")

        print("=====================End of Key Exchange (Dilithium3)=====================")


def main():
    parser = argparse.ArgumentParser(description="Post Quantum Client-Server Application",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-s", "--server", help="Server's IP address")
    parser.add_argument("-p", "--port", help="Port Number")
    parser.add_argument("-o", "--option", help="KEM or SIG")
    args = parser.parse_args()
    config = vars(args)
    config["server"] = HOST
    config["port"] = PORT
    config["option"] = config["option"].lower().strip()

    # Starts the connection
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        if config["option"] == "kem":
            # Key Exchange with Kyber512
            key_exchange(s)
        elif config["option"] == "sig" or config["option"] == "signature":
            # Digital Signature with Dilithium3
            digital_signature(s)
        else:
            print("Invalid option. Supported Options:"
                  "1. KEM"
                  "2. SIG/Signature")
            exit()


if __name__ == '__main__':
    main()
