import argparse

import oqs
import socket
import time

HOST = "192.168.0.41"
PORT = 123

kemalg = "Kyber512"
sigalg = "Dilithium3"


def key_exchange(conn):
    # Key exchange using Kyber
    print("=====================Performing Key Exchange using Kyber=====================")
    public_key = conn.recv(1024)
    # print(f"Received the client public key! {public_key}")

    with oqs.KeyEncapsulation(kemalg) as kem_server:
        # Encapsulating the server's secret using the client's public key
        print("Encapsulating the server's secret using the client's public key...")
        ciphertext, shared_secret_server = kem_server.encap_secret(public_key)
        time.sleep(2)
        # print(f"The ciphertext on the server is: {ciphertext}")

        # Sending the ciphertext to the client
        print("Sending ciphertext to the client...")
        conn.sendall(ciphertext)
        time.sleep(2)
        print("Ciphertext sent!")
        print(f"The shared secret by the server is: {shared_secret_server}")
        print("=====================End of Key Exchange (Kyber)=====================")


def digital_signature(conn):
    # Digital Signature using Dilithium3
    print("=====================Performing Digital Signature using Dilithium3=====================")
    with oqs.Signature(sigalg) as sig_server:
        # Generating Signer's Key Pair
        print("Generating the signer's keys...")
        public_key_sig = sig_server.generate_keypair()
        time.sleep(2)

        # Signer signs the message
        message_to_sign = "Some data to sign".encode()
        print("Signing the message...")
        signature = sig_server.sign(message_to_sign)
        time.sleep(2)

        delimiter = "EOF1".encode()
        # Send the data to the client
        print("Sending data to the client...")
        conn.sendall(public_key_sig + delimiter + message_to_sign + delimiter + signature + delimiter)
        time.sleep(2)
        print("=====================End of Digital Signature (Dilithium3)=====================")


def main():
    parser = argparse.ArgumentParser(description="Post Quantum Client-Server Application",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-s", "--server", help="Server's IP address")
    parser.add_argument("-p", "--port", help="Port Number")
    parser.add_argument("-o", "--option", help="KEM or Signature")
    args = parser.parse_args()
    config = vars(args)
    config["server"] = HOST
    config["port"] = PORT
    config["option"] = config["option"].lower().strip()


    # Starts the connection
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Client {addr} is connected to the server.")

            if config["option"] == "kem":
                # Key Exchange with Kyber512
                key_exchange(conn)
            elif config["option"] == "sig" or config["option"] == "signature":
                # Digital Signature with Dilithium3
                digital_signature(conn)
            else:
                print("Invalid option. Supported Options:"
                      "1. KEM"
                      "2. SIG/Signature")
                exit()


if __name__ == '__main__':
    main()
